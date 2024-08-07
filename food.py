import numpy as np


class Food:
    def __init__(self, position, max_resource_units):
        self.position = np.array(position)
        self.food_radius = 5
        self.count_resource_units = max_resource_units
        self.color_intensity = 1.0

    def consume(self):
        self.count_resource_units -= 1
        self.color_intensity -= 0.001

    def get_color(self):
        return (0, 0, self.color_intensity, 1.0)