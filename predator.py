import numpy as np


# Define the Predator class, which represents a predator agent in the environment
class Predator:
    # Initialize the predator with its position, direction, and speed
    def __init__(self, position, direction, speed):
        # Convert the initial position to a numpy array for vector operations
        self.position = np.array(position)

        # Calculate the unit direction vector based on the given angle (direction)
        self.unit_dir_vec = np.array([np.cos(direction), np.sin(direction)])

        # Set the speed of the predator, multiplying by 1.5 to enhance its speed
        self.speed = speed * 1.5

    # Method to move the predator towards a target point
    def move_towards_point(self, target, dt, space_size):
        # Calculate the vector from the predator's current position to the target
        direction_to_target = target - self.position

        # Compute the norm (magnitude) of the direction vector
        norm = np.linalg.norm(direction_to_target)

        # If the norm is not zero, normalize the direction vector
        if norm != 0:
            self.unit_dir_vec = direction_to_target / norm

        # Update the predator's position based on its speed, direction, and time step
        self.position += self.unit_dir_vec * self.speed * dt

        # Handle the wrapping of the predator's position in a toroidal (wrap-around) space
        if self.position[0] > space_size:
            self.position[0] = 0.0  # Wrap around horizontally
        elif self.position[0] < 0.0:
            self.position[0] = space_size

        if self.position[1] > space_size:
            self.position[1] = 0.0  # Wrap around vertically
        elif self.position[1] < 0.0:
            self.position[1] = space_size
