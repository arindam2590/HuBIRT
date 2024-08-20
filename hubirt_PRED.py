import time  # Importing time module for tracking simulation time
import os  # Importing os module for file handling
import numpy as np  # Importing numpy for numerical operations
import matplotlib.pyplot as plt  # Importing matplotlib for plotting
import matplotlib.animation as animation  # Importing animation module for creating animations
from agent import Agent  # Importing the Agent class
from food import Food  # Importing the Food class
from predator import Predator  # Importing the Predator class

# Class to manage the swarm of agents
class Swarm:
    def __init__(self, N, speed, space_size, sigma, rep_r, orien_r, attr_r, pred_r, dt):
        # Initialize swarm parameters
        self.num_agents = N  # Number of agents in the swarm
        self.dt = dt  # Time step for the simulation
        self.space_size = space_size  # Size of the simulation space
        self.sigma = sigma  # Noise intensity

        # Initialize the swarm's agents and predator
        self.agents = Swarm.__initialize_agent(N, speed)  # Create agents
        self.predator = Predator(np.random.uniform(self.space_size * 0.8, self.space_size * 0.95, 2),
                                 np.random.rand() * 2 * np.pi, speed)  # Initialize the predator

        # Interaction radii
        self.predator_radius = pred_r  # Radius within which agents perceive the predator
        self.repul_radius = rep_r  # Repulsion radius between agents
        self.orien_radius = orien_r  # Orientation radius between agents
        self.attrac_radius = attr_r  # Attraction radius between agents

    @staticmethod
    def __initialize_agent(N, speed):
        # Initialize each agent at a random position near a source point with a random direction
        source = (30, 30)  # Starting point for the swarm
        return [Agent(np.random.uniform(source[0] - 10, source[1] + 10, 2),
                      np.random.rand() * 2 * np.pi, speed) for _ in range(N)]

    def generate_noise(self, sigma):
        # Generate random noise to add stochastic behavior to the agents
        return np.random.normal(0, sigma)

    def reset_swarm(self):
        # Reset the forces and neighbor counts for each agent at the start of each simulation step
        for agent in self.agents:
            agent.d_r = np.zeros_like(agent.unit_dir_vec)  # Reset repulsion force vector
            agent.d_o = np.zeros_like(agent.unit_dir_vec)  # Reset orientation force vector
            agent.d_a = np.zeros_like(agent.unit_dir_vec)  # Reset attraction force vector
            agent.n_r = 0  # Reset repulsion neighbors count
            agent.n_a = 0  # Reset attraction neighbors count
            agent.n_o = 0  # Reset orientation neighbors count

    def simulate(self, foods):
        # Simulate one step of the swarm's behavior
        self.reset_swarm()  # Reset the swarm's state

        # Update agents based on their interactions with other agents, food, and the predator
        for i, agent in enumerate(self.agents):
            c_i = agent.position  # Current position of the agent

            # Check if agent is close to food and consume it if possible
            for food in foods:
                distance_to_food = np.linalg.norm(agent.position - food.position)
                if distance_to_food < food.food_radius and food.count_resource_units > 0:
                    food.consume()

            # Check for predator proximity and update the agent's behavior
            p = self.predator.position
            r_ip = (p - c_i)
            distance = np.linalg.norm(r_ip)
            if distance < self.predator_radius:
                r_ip /= distance
                agent.zop_update(r_ip)
            else:
                # Interact with other agents based on distance
                for other_agent in self.agents:
                    c_j = other_agent.position
                    r_ij = (c_j - c_i)
                    distance = np.linalg.norm(r_ij)

                    if distance != 0:
                        r_ij /= distance
                        if distance < self.repul_radius:
                            agent.zor_update(r_ij)
                        else:
                            v_j = other_agent.unit_dir_vec
                            if self.repul_radius <= distance < self.orien_radius:
                                agent.zoo_update(v_j)
                            elif self.orien_radius <= distance < self.attrac_radius:
                                agent.zoa_update(r_ij)

            # Normalize the orientation force if there are orientation neighbors
            if agent.n_o > 0:
                agent.d_o /= (agent.n_o + 1)

            # Add random noise to the agent's desired direction
            noise = self.generate_noise(self.sigma)
            agent.evaluate_desire_direction(noise)

        # Update agent positions and reset predator detection
        for agent in self.agents:
            agent.update(self.space_size, self.dt)
            agent.pred_detect = False

        # Check if all food resources have been consumed
        all_resources_consumed = all(food.count_resource_units <= 0 for food in foods)
        return all_resources_consumed

# Class to manage and run the simulation
class SimulationPRED:
    def __init__(self, N=100, speed=2.0, space_size=100, sigma=0.1, rep_r=3, orien_r=7, attr_r=12,
                 pred_r=15, dt=1.0, n_food=2, resource_units=5, filename='simulation_data.txt'):
        # Initialize simulation parameters
        self.start_time = None  # Start time of the simulation
        self.end_time = None  # End time of the simulation
        self.ani = None  # Animation object

        # Set up the plot for visualization
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_xlim(0, space_size)
        self.ax.set_ylim(0, space_size)

        # Initialize the swarm and plotting elements
        self.swarm = Swarm(N, speed, space_size, sigma, rep_r, orien_r, attr_r, pred_r, dt)
        self.scat = self.ax.quiver([agent.position[0] for agent in self.swarm.agents],
                                   [agent.position[1] for agent in self.swarm.agents],
                                   [agent.unit_dir_vec[0] for agent in self.swarm.agents],
                                   [agent.unit_dir_vec[1] for agent in self.swarm.agents])

        self.predator_scat = self.ax.quiver(self.swarm.predator.position[0],
                                            self.swarm.predator.position[1],
                                            self.swarm.predator.unit_dir_vec[0],
                                            self.swarm.predator.unit_dir_vec[1],
                                            color='r', scale=15)  # Plot the predator
        self.mouse_position = np.array([space_size / 2, space_size / 2])  # Initialize the predator's target position

        # Initialize food containers and their visual representation
        self.n_food_containers = n_food
        self.foods = [Food(self.get_food_position(space_size), resource_units) for _ in range(n_food)]
        self.food_circles = [plt.Circle(food.position, radius=food.food_radius, color=food.get_color()) for food in
                             self.foods]
        for circle in self.food_circles:
            self.ax.add_patch(circle)

        self.data_filename = filename  # File to save simulation data
        self.fig.canvas.mpl_connect('motion_notify_event', self.update_mouse_position)  # Track mouse movement

    def update_mouse_position(self, event):
        # Update the predator's target position based on mouse movement
        if event.inaxes:
            self.mouse_position = np.array([event.xdata, event.ydata])

    def animate(self, frame):
        # Run one frame of the simulation and update the visualization
        all_resources_consumed = self.swarm.simulate(self.foods)
        self.scat.set_offsets([agent.position for agent in self.swarm.agents])
        self.scat.set_UVC([agent.unit_dir_vec[0] for agent in self.swarm.agents],
                          [agent.unit_dir_vec[1] for agent in self.swarm.agents])

        self.predator_scat.set_offsets([self.swarm.predator.position])
        self.predator_scat.set_UVC(self.swarm.predator.unit_dir_vec[0], self.swarm.predator.unit_dir_vec[1])
        self.swarm.predator.move_towards_point(self.mouse_position, self.swarm.dt, self.swarm.space_size)

        # Update the color of food circles based on remaining resources
        for food, circle in zip(self.foods, self.food_circles):
            circle.set_color(food.get_color())

        # Check if all resources are consumed and end the simulation if so
        if all_resources_consumed:
            print('All food resources have been consumed. Simulation completed.')
            self.ani.event_source.stop()
            self.end_time = time.time()
            elapsed_time = self.end_time - self.start_time
            print(f'Total completion time: {elapsed_time:.2f} seconds')

            # Save the elapsed time to a file
            file_path = os.path.join('Data', self.data_filename)
            with open(file_path, "a") as file:
                file.write(f"{elapsed_time:.2f}\n")

        return self.scat, self.predator_scat, *self.food_circles

    def get_food_position(self, space_size):
        # Generate a random position for food within the space
        x_coord = np.random.rand() * 100

        # Adjust the y-coordinate based on the number of food containers
        if self.n_food_containers > 3:
            y_coord = np.random.rand() * 100
        else:
            y_coord = space_size / 2

        return np.array((x_coord, y_coord))

    def run(self):
        # Start the simulation and display the animation
        self.start_time = time.time()
        self.ani = animation.FuncAnimation(self.fig, self.animate, frames=100, interval=20, blit=True)
        plt.show()
