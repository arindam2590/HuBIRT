# Importing necessary modules and classes
from hubirt_PAR import SimulationPAR  # Import the simulation class for parameter-based swarm
from hubirt_PRED import SimulationPRED  # Import the simulation class for predator-based swarm
from utils import plot_graph  # Import the function to plot the graph of simulation results


def main():
    # Setting up the simulation mode; PAR_MODE = False indicates predator-based swarm mode
    PAR_MODE = False

    # Setting simulation parameters
    n_sim = 4  # Number of simulations to run
    max_trial = 5  # Number of trials per simulation
    N = 30  # Number of agents in the swarm
    r_rep = 5  # Radius of repulsion
    r_ori = 30  # Radius of orientation
    r_att = 32  # Radius of attraction
    r_pred = 35  # Radius of predator influence (only used in predator-based swarm)
    speed = 1.0  # Speed of agents
    sigma = 0.1  # Noise level in the agents' movement
    dt = 0.1  # Time step for the simulation
    space_size = 120  # Size of the simulation space
    n_food = [2, 2, 10, 10]  # Number of food items in each simulation
    res_unit = [1, 10, 100, 200]  # Resource units associated with food items

    # Loop through the number of simulations
    for i in range(n_sim):
        print(f'Simulation No. : {i + 1}')

        # If in parameter-based swarm mode
        if PAR_MODE:
            filename = 'simulation_data_PAR'  # Base filename for saving data
            title = 'Parameter based Swarm'  # Title for the graph
            # Loop through the number of trials for the current simulation
            for j in range(max_trial):
                print(f'------------------------------------------------------------')
                print(f'Trial No. : {j + 1}')
                data_filename = filename + str(i + 1) + '.txt'  # Generate data filename
                plot_filename = 'sim_completion_plot_PAR.png'  # Filename for the final plot
                # Initialize the simulation with the current parameters
                sim = SimulationPAR(N, speed, space_size, sigma, r_rep, r_ori, r_att, dt, n_food[i], res_unit[i],
                                    data_filename)
                sim.run()  # Run the simulation

        # If in predator-based swarm mode
        else:
            filename = 'simulation_data_PRED'  # Base filename for saving data
            title = 'Predator based Swarm'  # Title for the graph
            # Loop through the number of trials for the current simulation
            for j in range(max_trial):
                print(f'------------------------------------------------------------')
                print(f'Trial No. : {j + 1}')
                data_filename = filename + str(i + 1) + '.txt'  # Generate data filename
                plot_filename = 'sim_completion_plot_PRED.png'  # Filename for the final plot
                # Initialize the simulation with the current parameters, including predator radius
                sim = SimulationPRED(N, speed, space_size, sigma, r_rep, r_ori, r_att, r_pred, dt, n_food[i],
                                     res_unit[i], data_filename)
                sim.run()  # Run the simulation

    print(f'==========================================================')
    # After all simulations and trials are completed, plot the results
    plot_graph(PAR_MODE, n_sim, filename, plot_filename, title)


# Driver code
if __name__ == "__main__":
    main()
