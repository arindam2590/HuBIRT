import numpy as np

class Food:
    # Constructor to initialize the Food object
    def __init__(self, position, max_resource_units):
        # Position of the food represented as a NumPy array
        self.position = np.array(position)
        # The radius within which the food can be detected or consumed
        self.food_radius = 5
        # The total number of resource units (e.g., food quantity) available
        self.count_resource_units = max_resource_units
        # The initial intensity of the food's color (could represent its freshness or visibility)
        self.color_intensity = 1.0

    # Method to simulate the consumption of one unit of the food
    def consume(self):
        # Decrease the number of resource units by one
        self.count_resource_units -= 1
        # Reduce the color intensity slightly (e.g., to simulate the food becoming less visible or fresh as it is consumed)
        self.color_intensity -= 0.001

    # Method to retrieve the current color of the food
    def get_color(self):
        # Return the color in RGBA format, where only the blue channel (color_intensity) and alpha (opacity) are variable
        return (0, 0, self.color_intensity, 1.0)
