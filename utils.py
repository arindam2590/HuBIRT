import os
import numpy as np
import matplotlib.pyplot as plt


def plot_graph(PAR_MODE, n_sim, data_filename, plot_filename, title):
    # Initialize an empty list to store simulation data
    data = []

    # Check if parallel mode is enabled (PAR_MODE)
    if PAR_MODE:
        # Load data from text files for each simulation
        for i in range(n_sim):
            file_path = os.path.join('Data', data_filename + str(i + 1) + '.txt')
            sim_data = np.loadtxt(file_path)
            data.append(sim_data)
    else:
        # Load data from text files for each simulation (sequentially)
        for i in range(n_sim):
            file_path = os.path.join('Data', data_filename + str(i + 1) + '.txt')
            sim_data = np.loadtxt(file_path)
            data.append(sim_data)

    # Create a figure and axis object for plotting
    fig, ax = plt.subplots()

    # Generate a box plot of the data, showing means with a line and patches for the boxes
    boxplot = ax.boxplot(data, showmeans=True, meanline=False, patch_artist=True)

    # Extract the mean points from the box plot data
    mean_points = [boxplot['means'][i].get_ydata()[0] for i in range(len(data))]

    # Plot the mean points on the box plot
    ax.plot(range(1, len(data) + 1), mean_points, color='magenta', linestyle='-', linewidth=3, markersize=6, label='Mean')

    # Set the x and y labels and the plot title
    ax.set_xlabel('No. of Simulation')
    ax.set_ylabel('Completion Time')
    ax.set_title(title)

    # Adjust the layout of the plot to prevent clipping of labels/titles
    plt.tight_layout()

    # Save the plot to the specified file path
    file_path = os.path.join('Data', plot_filename)
    plt.savefig(file_path)
