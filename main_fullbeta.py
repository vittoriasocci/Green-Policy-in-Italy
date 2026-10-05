from multiprocessing import Pool, cpu_count
from time import perf_counter
import os
import random
import numpy as np

from functions import *

# MODEL PARAMETERS
N_c = 100000
N_s = 895

election = 5
policy_x_election = 5
pp_x_policy = 10
decay = 0.99
BETA = 1
min_beta = {"H":0.9,"HM":0.8, "M":0.7,"ML":0.6,"L":0.5}

FINAL_STEP = election * policy_x_election * pp_x_policy  # 250

SIGMA_VALUES = [
    0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225,
    0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.475,
    0.5, 0.525, 0.55, 0.575, 0.6, 0.625, 0.65, 0.675, 0.7, 0.725,
    0.75, 0.775, 0.8, 0.825, 0.85, 0.875, 0.9, 0.925, 0.95, 0.975,
    1
]

REPETITIONS = 50
REWIRE_P = 0.1

BASE_EDGE_FILE = "last_created_network_21.txt"

income_index = {"H": 0, "HM": 1, "M": 2, "ML": 3, "L": 4}
community_index = {
    "PIE": 0, "AOS": 1, "LIG": 2, "LOMB": 3, "TREN": 4,
    "VEN": 5, "FRIU": 6, "EMI": 7, "TOSC": 8, "UMB": 9,
    "MAR": 10, "LAZ": 11, "ABR": 12, "MOL": 13, "CAMP": 14,
    "PUGL": 15, "BAS": 16, "CAL": 17, "SIC": 18, "SAR": 19
}

# POLICY (choose one to simulate it)
UNIFORM     = [0.5, 0.5, 0.5, 0.5, 0.5]
REGRESSIVE  = [0.9, 0.75, 0.5, 0.25, 0.1]
PROGRESSIVE = [0.1, 0.25, 0.5, 0.75, 0.9]
BIMODAL     = [0.8, 0.4, 0.1, 0.4, 0.8]
MIDDLE      = [0.2, 0.6, 0.9, 0.6, 0.2]
BROWN       = [0, 0, 0, 0, 0]

POLICY_DICT = {
    "brown": BROWN,
    "uniform": UNIFORM,
    "bimodal": BIMODAL,
    "middle": MIDDLE,
    "regressive": REGRESSIVE,
    "progressive": PROGRESSIVE,
}

POLICY_NAME = "brown"  #change the policy to be simulated here
pol_eff_incG = POLICY_DICT[POLICY_NAME]
pol_eff_incB = [0, 0, 0, 0, 0]


CITIZEN = None
SEATS = None
BASE_EDGES = None


def init_process():
    
    global CITIZEN, SEATS, BASE_EDGES

    # citizens
    CITIZEN = []
    size_income = [0] * 5
    size_gender = [0, 0]

    for i in range(N_c):
        geo_list = exact_geo(i, N_c)
        geo = geo_list[0]
        position = geo_list[1]
        size_com = geo_list[2]

        income_list = exact_income(geo, position, size_com, size_income)
        income = income_list[0]
        income_class = income_list[1]

        alpha = random_alpha()
        beta = BETA #(1-min_beta[income]) * random.random() + min_beta[income] #BETA

        gender = 0 if random.random() < 0.49 else 1
        size_gender[gender] += 1

        CITIZEN.append(Citizen(i, income, gender, geo, position, size_com, income_class, alpha, beta))

    # political seats
    SEATS = []
    for i in range(N_s):
        geo = exact_geo_seats(i, N_s)
        SEATS.append(Seat(i, geo, True))

    
    BASE_EDGES = load_edges(BASE_EDGE_FILE)
    build_neighbors(CITIZEN, BASE_EDGES)


def worker_rep(task):
    SIGMA, rep_id = task
    global CITIZEN, SEATS, BASE_EDGES

    # building the small-world network
    rewired_edges = rewire_edges(BASE_EDGES, N_c, REWIRE_P, 10)

    build_neighbors(CITIZEN, rewired_edges)

    # giant component of the rewired graph
    gset = giant_component(CITIZEN)
    GIANT_CITIZEN = [CITIZEN[i] for i in gset]
    if len(GIANT_CITIZEN) == 0:
        return (SIGMA, None)

    tot_income = [0] * 5
    tot_comm = [0] * 20
    for p in GIANT_CITIZEN:
        tot_income[income_index[p.income]] += 1
        tot_comm[community_index[p.geo]] += 1

    # reset alpha/beta and seats
    for p in CITIZEN:
        p.alpha = random_alpha()
        p.beta = BETA #(1-min_beta[p.income]) * random.random() + min_beta[p.income] #BETA
    for s in SEATS:
        s.vote = True

    # Complete simulation (over GIANT_CITIZEN)
    for _ in range(election):

        # average alpha by region
        alpha_community = [0.0] * 20
        size_community = [0.0] * 20
        for cit in GIANT_CITIZEN:
            idx = community_index[cit.geo]
            size_community[idx] += 1.0
            alpha_community[idx] += cit.alpha
        for i in range(20):
            if size_community[i] > 0:
                alpha_community[i] /= size_community[i]

        # seat election
        for i in range(N_s):
            community = SEATS[i].geo
            SEATS[i].vote = (random.random() < alpha_community[community_index[community]])

        # policy cicles
        for _policy in range(policy_x_election):

            # policy election
            if random.random() < (1.0 * count_green_seats(SEATS)) / (N_s * 1.0):
                pol_eff_inc = pol_eff_incG
            else:
                pol_eff_inc = pol_eff_incB

            # policy stage
            for cit in GIANT_CITIZEN:
                cit.alpha = cit.alpha + pol_eff_inc[income_index[cit.income]] * (1 - cit.alpha) * cit.alpha * cit.beta
                if cit.alpha >= 1:
                    cit.alpha = 1

            # peer pressure stage
            for _pp in range(pp_x_policy):
                for _ in range(len(GIANT_CITIZEN)):
                    cit = random.choice(GIANT_CITIZEN)
                    if len(cit.neighbors) == 0:
                        continue
                    media = 0.0
                    for k in cit.neighbors:
                        media += CITIZEN[k].alpha
                    neighbors_alpha = media / len(cit.neighbors)
                    cit.alpha = decay * (neighbors_alpha * SIGMA + cit.alpha * (1 - SIGMA))

    # final measures
    green_seats = float(count_green_seats(SEATS))

    income_avg = [0.0] * 5
    total_alpha = 0.0
    for p in GIANT_CITIZEN:
        a = p.alpha
        income_avg[income_index[p.income]] += a
        total_alpha += a

    for j in range(5):
        if tot_income[j] > 0:
            income_avg[j] /= float(tot_income[j])

    all_avg = total_alpha / float(len(GIANT_CITIZEN))

    comm_avg = [0.0] * 20
    for p in GIANT_CITIZEN:
        comm_avg[community_index[p.geo]] += p.alpha
    for i in range(20):
        if tot_comm[i] > 0:
            comm_avg[i] /= float(tot_comm[i])

    return (SIGMA, (green_seats, all_avg, income_avg, comm_avg))


def main():
    out1 = f"{POLICY_NAME}01.txt"
    out2 = f"{POLICY_NAME}012.txt"

    header1 = "income\tPP\tpolicy\telection\talpha_mean\talpha_std\talpha_se\tpolicy_type\tstep\tgreen_seats_mean\tgreen_seats_std\tgreen_seats_se\tsigma\tgamma\tbeta\tgreen_policy\n"
    header2 = "CCAA\tPP\tpolicy\telection\talpha_mean\talpha_std\talpha_se\tpolicy_type\tstep\tgreen_seats_mean\tgreen_seats_std\tgreen_seats_se\tsigma\tgamma\tbeta\n"

    # nproc = max(1, cpu_count() - 1)
    nproc = 12  

    print("Policy scelta:", POLICY_NAME, pol_eff_incG)
    print("SIGMA_VALUES:", SIGMA_VALUES)
    print("REPETITIONS:", REPETITIONS, "nproc:", nproc)
    print("BASE_EDGE_FILE:", BASE_EDGE_FILE)

    # task list: (sigma, rep)
    tasks = [(s, r) for s in SIGMA_VALUES for r in range(REPETITIONS)]
    total_tasks = len(tasks)

    green_vals  = {s: [] for s in SIGMA_VALUES}
    all_vals    = {s: [] for s in SIGMA_VALUES}
    income_vals = {s: [[] for _ in range(5)] for s in SIGMA_VALUES}
    comm_vals   = {s: [[] for _ in range(20)] for s in SIGMA_VALUES}

    rep_done = {s: 0 for s in SIGMA_VALUES}

    t0 = perf_counter()

    with Pool(processes=nproc, initializer=init_process) as pool:
        done = 0
        for sigma, payload in pool.imap_unordered(worker_rep, tasks, chunksize=1):
            done += 1
            rep_done[sigma] += 1

            print(f"replica {rep_done[sigma]}/{REPETITIONS} per sigma = {sigma} completata", flush=True)

            if payload is not None:
                g, a_all, inc_avg, com_avg = payload
                green_vals[sigma].append(g)
                all_vals[sigma].append(a_all)
                for j in range(5):
                    income_vals[sigma][j].append(inc_avg[j])
                for i in range(20):
                    comm_vals[sigma][i].append(com_avg[i])

    elapsed_min = (perf_counter() - t0) / 60.0
    print(f"Tutte le repliche finite. Tempo totale: {elapsed_min:.1f} minuti")

    
    with open(out1, "w") as f, open(out2, "w") as f2:
        f.write(header1)
        f2.write(header2)

        step = FINAL_STEP
        policy_type_out = "X"

        region_keys = list(community_index.keys())
        income_keys = list(income_index.keys())

        # scrivi sigma in ordine
        for SIGMA in sorted(SIGMA_VALUES):
            green_mean, green_std, green_se, _ = mean_std_se(green_vals[SIGMA])
            all_mean, all_std, all_se, _ = mean_std_se(all_vals[SIGMA])

            inc_mean = [0.0] * 5
            inc_std  = [0.0] * 5
            inc_se   = [0.0] * 5
            for j in range(5):
                m, s, se, _ = mean_std_se(income_vals[SIGMA][j])
                inc_mean[j], inc_std[j], inc_se[j] = m, s, se

            com_mean = [0.0] * 20
            com_std  = [0.0] * 20
            com_se   = [0.0] * 20
            for i in range(20):
                m, s, se, _ = mean_std_se(comm_vals[SIGMA][i])
                com_mean[i], com_std[i], com_se[i] = m, s, se

            for j in range(5):
                f.write(
                    income_keys[j] + "\t" +
                    str(pp_x_policy) + "\t" + str(policy_x_election) + "\t" + str(election) + "\t" +
                    str(round(inc_mean[j], 4)) + "\t" +
                    str(round(inc_std[j], 4)) + "\t" +
                    str(round(inc_se[j], 4)) + "\t" +
                    policy_type_out + "\t" +
                    str(step) + "\t" +
                    str(round(green_mean, 4)) + "\t" +
                    str(round(green_std, 4)) + "\t" +
                    str(round(green_se, 4)) + "\t" +
                    str(SIGMA) + "\t" + str(decay) + "\t" + str(BETA) + "\t" +
                    str(pol_eff_incG[j]) + "\n"
                )

            f.write(
                "ALL\t" +
                str(pp_x_policy) + "\t" + str(policy_x_election) + "\t" + str(election) + "\t" +
                str(round(all_mean, 4)) + "\t" +
                str(round(all_std, 4)) + "\t" +
                str(round(all_se, 4)) + "\t" +
                policy_type_out + "\t" +
                str(step) + "\t" +
                str(round(green_mean, 4)) + "\t" +
                str(round(green_std, 4)) + "\t" +
                str(round(green_se, 4)) + "\t" +
                str(SIGMA) + "\t" + str(decay) + "\t" + str(BETA) + "\t" +
                "NA\n"
            )

            # ----- FILE 2: regioni + ALL -----
            for i in range(20):
                f2.write(
                    region_keys[i] + "\t" +
                    str(pp_x_policy) + "\t" + str(policy_x_election) + "\t" + str(election) + "\t" +
                    str(round(com_mean[i], 4)) + "\t" +
                    str(round(com_std[i], 4)) + "\t" +
                    str(round(com_se[i], 4)) + "\t" +
                    policy_type_out + "\t" +
                    str(step) + "\t" +
                    str(round(green_mean, 4)) + "\t" +
                    str(round(green_std, 4)) + "\t" +
                    str(round(green_se, 4)) + "\t" +
                    str(SIGMA) + "\t" + str(decay) + "\t" + str(BETA) + "\n"
                )

            f2.write(
                "ALL\t" +
                str(pp_x_policy) + "\t" + str(policy_x_election) + "\t" + str(election) + "\t" +
                str(round(all_mean, 4)) + "\t" +
                str(round(all_std, 4)) + "\t" +
                str(round(all_se, 4)) + "\t" +
                policy_type_out + "\t" +
                str(step) + "\t" +
                str(round(green_mean, 4)) + "\t" +
                str(round(green_std, 4)) + "\t" +
                str(round(green_se, 4)) + "\t" +
                str(SIGMA) + "\t" + str(decay) + "\t" + str(BETA) + "\n"
            )

    print("Finito. File scritti:", out1, out2)


if __name__ == "__main__":
    main()

