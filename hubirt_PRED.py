import time
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from agent import Agent
from food import Food
from predator import Predator


class Swarm:
    def __init__(self, N, speed, space_size, sigma, rep_r, orien_r, attr_r, pred_r, dt):
        self.num_agents = N
        self.dt = dt
        self.space_size = space_size
        self.sigma = sigma

        self.agents = Swarm.__initialize_agent(N, speed)
        self.predator = Predator(np.random.uniform(self.space_size * 0.8, self.space_size * 0.95, 2), np.random.rand() * 2 * np.pi, speed)

        self.predator_radius = pred_r
        self.repul_radius = rep_r
        self.orien_radius = orien_r
        self.attrac_radius = attr_r

    def __initialize_agent(N, speed):
        # Initialize each agent at a random position near a source point with random direction
        source = (30, 30)  # Starting point for the swarm
        return [Agent(np.random.uniform(source[0] - 10, source[1] + 10, 2), np.random.rand() * 2 * np.pi, speed) for _ in range(N)]

    def generate_noise(self, sigma):
        return np.random.normal(0, sigma)

    def reset_swarm(self):
        # Reset the forces and neighbor counts for each agent
        for agent in self.agents:
            agent.d_r = np.zeros_like(agent.unit_dir_vec)  # Reset repulsion force vector
            agent.d_o = np.zeros_like(agent.unit_dir_vec)  # Reset orientation force vector
            agent.d_a = np.zeros_like(agent.unit_dir_vec)  # Reset attraction force vector
            agent.n_r = 0  # Reset repulsion neighbors count
            agent.n_a = 0  # Reset attraction neighbors count
            agent.n_o = 0  # Reset orientation neighbors count

    def simulate(self, foods):
        self.reset_swarm()

        for i, agent in enumerate(self.agents):
            c_i = agent.position
            for food in foods:
                distance_to_food = np.linalg.norm(agent.position - food.position)
                if distance_to_food < food.food_radius:
                    if food.count_resource_units > 0:
                        food.consume()

            p = self.predator.position
            r_ip = (p - c_i)
            distance = np.linalg.norm(r_ip)
            if distance < self.predator_radius:
                r_ip /= distance
                agent.zop_update(r_ip)
            else:
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
                            if distance >= self.repul_radius and distance < self.orien_radius:
                                agent.zoo_update(v_j)
                            elif distance >= self.orien_radius and distance < self.attrac_radius:
                                agent.zoa_update(r_ij)

            if agent.n_o > 0:
                agent.d_o /= (agent.n_o + 1)

            noise = self.generate_noise(self.sigma)
            agent.evaluate_desire_direction(noise)

        for agent in self.agents:
            agent.update(self.space_size, self.dt)
            agent.pred_detect = False

        all_resources_consumed = all(food.count_resource_units <= 0 for food in foods)
        return all_resources_consumed

class SimulationPRED:
    def __init__(self, N=100, speed=2.0, space_size=100, sigma=0.1, rep_r=3, orien_r=7, attr_r=12,
                 pred_r=15, dt=1.0, n_food=2, resource_units=5, filename='simulation_data.txt'):
        self.start_time = None
        self.end_time = None
        self.ani = None
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_xlim(0, space_size)
        self.ax.set_ylim(0, space_size)

        self.swarm = Swarm(N, speed, space_size, sigma, rep_r, orien_r, attr_r, pred_r, dt)
        self.scat = self.ax.quiver([agent.position[0] for agent in self.swarm.agents],
                                   [agent.position[1] for agent in self.swarm.agents],
                                   [agent.unit_dir_vec[0] for agent in self.swarm.agents],
                                   [agent.unit_dir_vec[1] for agent in self.swarm.agents])

        self.predator_scat = self.ax.quiver(self.swarm.predator.position[0],
                                            self.swarm.predator.position[1],
                                            self.swarm.predator.unit_dir_vec[0],
                                            self.swarm.predator.unit_dir_vec[1],
                                            color='r', scale=15)
        self.mouse_position = np.array([space_size / 2, space_size / 2])

        self.n_food_containers = n_food
        self.foods = [Food(self.get_food_position(space_size), resource_units) for _ in range(n_food)]
        self.food_circles = [plt.Circle(food.position, radius=food.food_radius, color=food.get_color()) for food in
                             self.foods]
        for circle in self.food_circles:
            self.ax.add_patch(circle)

        self.data_filename = filename
        self.fig.canvas.mpl_connect('motion_notify_event', self.update_mouse_position)

    def update_mouse_position(self, event):
        if event.inaxes:
            self.mouse_position = np.array([event.xdata, event.ydata])

    def animate(self, frame):
        all_resources_consumed = self.swarm.simulate(self.foods)
        self.scat.set_offsets([agent.position for agent in self.swarm.agents])
        self.scat.set_UVC([agent.unit_dir_vec[0] for agent in self.swarm.agents],
                          [agent.unit_dir_vec[1] for agent in self.swarm.agents])

        self.predator_scat.set_offsets([self.swarm.predator.position])
        self.predator_scat.set_UVC(self.swarm.predator.unit_dir_vec[0], self.swarm.predator.unit_dir_vec[1])
        self.swarm.predator.move_towards_point(self.mouse_position, self.swarm.dt, self.swarm.space_size)

        for food, circle in zip(self.foods, self.food_circles):
            circle.set_color(food.get_color())

        if all_resources_consumed:
            print('All food resources have been consumed. Simulation completed.')
            self.ani.event_source.stop()
            self.end_time = time.time()
            elapsed_time = self.end_time - self.start_time
            print(f'Total completion time: {elapsed_time:.2f} seconds')

            file_path = os.path.join('Data', self.data_filename)
            with open(file_path, "a") as file:
                file.write(f"{elapsed_time:.2f}\n")

        return self.scat, self.predator_scat, *self.food_circles

    def get_food_position(self, space_size):
        x_coord = np.random.rand() * 100

        if self.n_food_containers > 3:
            y_coord = np.random.rand() * 100
        else:
            y_coord = space_size / 2

        return np.array((x_coord, y_coord))

    def run(self):
        self.start_time = time.time()
        self.ani = animation.FuncAnimation(self.fig, self.animate, frames=100, interval=20, blit=True)
        plt.show()