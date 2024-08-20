import time  # Import the time module to track simulation duration.
import os  # Import the os module for file path operations.
import numpy as np  # Import numpy for numerical operations.
import matplotlib.pyplot as plt  # Import matplotlib for plotting.
import matplotlib.animation as animation  # Import animation module for creating animated plots.
from agent import Agent  # Import the Agent class from a custom module.
from food import Food  # Import the Food class from a custom module.

class Swarm:
    def __init__(self, N, speed, space_size, sigma, rep_r, orien_r, attr_r, dt):
        """
        Initialize the Swarm object with specified parameters.
        """
        self.num_agents = N  # Number of agents in the swarm.
        self.dt = dt  # Time step for simulation.
        self.space_size = space_size  # Size of the simulation space.
        self.sigma = sigma  # Standard deviation for noise in agent movement.

        # Initialize agents with random positions and directions.
        self.agents = self._initialize_agent(N, speed)

        # Set the radii for different zones (repulsion, orientation, attraction).
        self.repul_radius = rep_r
        self.orien_radius = orien_r
        self.attrac_radius = attr_r

    def _initialize_agent(self, N, speed):
        """
        Initialize agents with random positions near a source and random directions.
        """
        source = (30, 30)  # Starting point for the swarm.
        # Create a list of agents with random positions and directions.
        return [Agent(np.random.uniform(source[0] - 10, source[1] + 10, 2), np.random.rand() * 2 * np.pi, speed) for _ in range(N)]

    def generate_noise(self, sigma):
        """
        Generate random noise for agent movement.
        """
        return np.random.normal(0, sigma)

    def reset_swarm(self):
        """
        Reset the forces and neighbor counts for each agent.
        """
        for agent in self.agents:
            agent.d_r = np.zeros_like(agent.unit_dir_vec)  # Reset repulsion force vector.
            agent.d_o = np.zeros_like(agent.unit_dir_vec)  # Reset orientation force vector.
            agent.d_a = np.zeros_like(agent.unit_dir_vec)  # Reset attraction force vector.
            agent.n_r = 0  # Reset repulsion neighbors count.
            agent.n_a = 0  # Reset attraction neighbors count.
            agent.n_o = 0  # Reset orientation neighbors count.

    def simulate(self, foods):
        """
        Simulate the swarm's movement and interaction with food sources.
        """
        self.reset_swarm()

        for i, agent in enumerate(self.agents):
            c_i = agent.position  # Current position of the agent.
            for food in foods:
                # Check if agent is close enough to consume the food.
                distance_to_food = np.linalg.norm(agent.position - food.position)
                if distance_to_food < food.food_radius:
                    if food.count_resource_units > 0:
                        food.consume()  # Agent consumes a unit of food.

            for other_agent in self.agents:
                c_j = other_agent.position  # Position of another agent.
                r_ij = (c_j - c_i)  # Vector from agent i to agent j.
                distance = np.linalg.norm(r_ij)  # Distance between agents.
                if distance != 0:
                    r_ij /= distance  # Normalize the vector.
                    if distance < self.repul_radius:
                        agent.zor_update(r_ij)  # Update repulsion force.
                    else:
                        v_j = other_agent.unit_dir_vec  # Direction vector of agent j.
                        if distance >= self.repul_radius and distance < self.orien_radius:
                            agent.zoo_update(v_j)  # Update orientation force.
                        elif distance >= self.orien_radius and distance < self.attrac_radius:
                            agent.zoa_update(r_ij)  # Update attraction force.

            if agent.n_o > 0:
                agent.d_o /= (agent.n_o + 1)  # Average the orientation force if there are neighbors.

            noise = self.generate_noise(self.sigma)  # Generate movement noise.
            agent.evaluate_desire_direction(noise)  # Calculate the desired direction with noise.

        for agent in self.agents:
            agent.update(self.space_size, self.dt)  # Update the agent's position based on the forces.

        # Check if all food resources have been consumed.
        all_resources_consumed = all(food.count_resource_units <= 0 for food in foods)
        return all_resources_consumed


class SimulationPAR:
    def __init__(self, N=100, speed=2.0, space_size=100, sigma=0.1, rep_r=3, orien_r=7, attr_r= 12, dt=1.0, n_food=2, resource_units=5,
                 filename='simulation_data.txt'):
        """
        Initialize the simulation with swarm parameters and food sources.
        """
        self.start_time = None  # Start time of the simulation.
        self.end_time = None  # End time of the simulation.
        self.ani = None  # Animation object.
        self.fig, self.ax = plt.subplots(figsize=(10, 10))  # Create a plot for visualization.
        self.ax.set_xlim(0, space_size)  # Set the x-axis limits.
        self.ax.set_ylim(0, space_size)  # Set the y-axis limits.

        # Initialize the swarm with specified parameters.
        self.swarm = Swarm(N, speed, space_size, sigma, rep_r, orien_r, attr_r, dt)
        # Scatter plot for the agents' positions and directions.
        self.scat = self.ax.quiver([agent.position[0] for agent in self.swarm.agents],
                                   [agent.position[1] for agent in self.swarm.agents],
                                   [agent.unit_dir_vec[0] for agent in self.swarm.agents],
                                   [agent.unit_dir_vec[1] for agent in self.swarm.agents])

        # Initialize food sources with random positions and resources.
        self.n_food_containers = n_food
        self.foods = [Food(self.get_food_position(space_size), resource_units) for _ in range(n_food)]
        # Create circular patches for visualizing food resources.
        self.food_circles = [plt.Circle(food.position, radius=food.food_radius, color=food.get_color()) for food in
                             self.foods]
        for circle in self.food_circles:
            self.ax.add_patch(circle)  # Add the food circles to the plot.
        self.data_filename = filename  # Filename to save the simulation results.

    def animate(self, frame):
        """
        Update the plot in each frame of the animation.
        """
        all_resources_consumed = self.swarm.simulate(self.foods)  # Simulate the swarm's behavior.
        # Update the agents' positions and directions in the plot.
        self.scat.set_offsets([agent.position for agent in self.swarm.agents])
        self.scat.set_UVC([agent.unit_dir_vec[0] for agent in self.swarm.agents],
                          [agent.unit_dir_vec[1] for agent in self.swarm.agents])

        # Update the colors of the food circles based on remaining resources.
        for food, circle in zip(self.foods, self.food_circles):
            circle.set_color(food.get_color())

        if all_resources_consumed:
            print('All food resources have been consumed. Simulation completed.')
            self.ani.event_source.stop()  # Stop the animation if all resources are consumed.
            self.end_time = time.time()  # Record the end time.
            elapsed_time = self.end_time - self.start_time  # Calculate the elapsed time.
            print(f'Total completion time: {elapsed_time:.2f} seconds')

            # Save the elapsed time to a file.
            file_path = os.path.join('Data', self.data_filename)
            with open(file_path, "a") as file:
                file.write(f"{elapsed_time:.2f}\n")

        return self.scat, *self.food_circles  # Return updated scatter and food circles.

    def get_food_position(self, space_size):
        """
        Generate a random position for food within the simulation space.
        """
        x_coord = np.random.rand() * 100  # Random x-coordinate.

        if self.n_food_containers > 3:
            y_coord = np.random.rand() * 100  # Random y-coordinate.
        else:
            y_coord = space_size / 2  # Fixed y-coordinate if fewer food sources.

        return np.array((x_coord, y_coord))

    def run(self):
        """
        Run the simulation and display the animation.
        """
        self.start_time = time.time()  # Record the start time.
        # Create an animation with 100 frames, updating every 20 milliseconds.
        self.ani = animation.FuncAnimation(self.fig, self.animate, frames=100, interval=20, blit=True)
        plt.show()  # Display the animation.
