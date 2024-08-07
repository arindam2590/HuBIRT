import numpy as np


class Predator:
    def __init__(self, position, direction, speed):
        self.position = np.array(position)
        self.unit_dir_vec = np.array([np.cos(direction), np.sin(direction)])
        self.speed = speed * 1.5

    def move_towards_point(self, target, dt, space_size):
        direction_to_target = target - self.position
        norm = np.linalg.norm(direction_to_target)
        if norm != 0:
            self.unit_dir_vec = direction_to_target / norm
        self.position += self.unit_dir_vec * self.speed * dt

        if self.position[0] > space_size:
            self.position[0] = 0.0
        elif self.position[0] < 0.0:
            self.position[0] = space_size

        if self.position[1] > space_size:
            self.position[1] = 0.0
        elif self.position[1] < 0.0:
            self.position[1] = space_size