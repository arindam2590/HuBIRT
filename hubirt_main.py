from hubirt_PAR import SimulationPAR
from hubirt_PRED import SimulationPRED


def main():
    PAR_MODE = False

    n_sim = 4
    max_trial = 1
    N = 30
    r_rep = 5
    r_ori = 30
    r_att = 32
    r_pred = 35
    speed = 1.0
    sigma = 0.1
    dt = 0.1
    space_size = 120
    n_food = [2, 2, 10, 10]
    res_unit = [1, 10, 100, 200]

    for i in range(n_sim):
        print(f'Simulation No. : {i + 1}')
        if PAR_MODE:
            filename = 'simulation_data_PAR'
            title = 'Parameter based Swarm'
            for j in range(max_trial):
                print(f'------------------------------------------------------------')
                print(f'Trial No. : {j + 1}')
                data_filename = filename + str(i + 1) + '.txt'
                plot_filename = 'sim_completion_plot_PAR.png'
                sim = SimulationPAR(N, speed, space_size, sigma, r_rep, r_ori, r_att, dt, n_food[i], res_unit[i], data_filename)
                sim.run()
        else:
            filename = 'simulation_data_PRED'
            title = 'Predator based Swarm'
            for j in range(max_trial):
                print(f'------------------------------------------------------------')
                print(f'Trial No. : {j + 1}')
                data_filename = filename + str(i + 1) + '.txt'
                plot_filename = 'sim_completion_plot_PRED.png'
                sim = SimulationPRED(N, speed, space_size, sigma, r_rep, r_ori, r_att, r_pred, dt, n_food[i], res_unit[i], data_filename)
                sim.run()


if __name__ == "__main__":
    main()
