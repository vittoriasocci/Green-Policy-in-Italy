from multiprocessing import Pool, cpu_count
from time import perf_counter
import os
import random
import numpy as np
import pandas as pd

from functions import *

N_c = 100000
N_s = 895

election = 5
policy_x_election = 5
pp_x_policy = 10
decay = 0.99
BETA = 1
min_beta = {"H":0.9,"HM":0.8, "M":0.7,"ML":0.6,"L":0.5}
female_min = 1 # choose in {0,0.25,0.5,0.75,1} to simulate different gender cases in self-efficacy
print(f"beta donne: {female_min}")

FINAL_STEP = election * policy_x_election * pp_x_policy  # 250

SIGMA_VALUES = [0.05]
print(f"sigma values: {SIGMA_VALUES}")

REPETITIONS = 50
REWIRE_P = 0.1

BASE_EDGE_FILE = "last_created_network_21.txt" #choose the file with the value of lambda requested
print(f"grafo in input: {BASE_EDGE_FILE}")

income_index = {"H": 0, "HM": 1, "M": 2, "ML": 3, "L": 4}
community_index = {
    "PIE": 0, "AOS": 1, "LIG": 2, "LOMB": 3, "TREN": 4,
    "VEN": 5, "FRIU": 6, "EMI": 7, "TOSC": 8, "UMB": 9,
    "MAR": 10, "LAZ": 11, "ABR": 12, "MOL": 13, "CAMP": 14,
    "PUGL": 15, "BAS": 16, "CAL": 17, "SIC": 18, "SAR": 19
}

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

POLICY_NAME = "regressive"
pol_eff_incG = POLICY_DICT[POLICY_NAME]
pol_eff_incB = [0, 0, 0, 0, 0]
print(f"policy scelta: {POLICY_NAME}: {pol_eff_incG}")

CITIZEN = None
SEATS = None
BASE_EDGES = None


def init_process():
    global CITIZEN, SEATS, BASE_EDGES

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

        #alpha = random_alpha()
        #beta = (1 - min_beta[income]) * random.random() + min_beta[income]

        gender = 0 if random.random() < 0.49 else 1
        size_gender[gender] += 1
        
        if gender == 0:   # uomo
            alpha = random.uniform(0.0, 0.4)
        else:             # donna
            alpha = random.uniform(0.6, 1.0)

        if gender == 0: 
            beta = 1
        else:
            beta = female_min

        CITIZEN.append(Citizen(i, income, gender, geo, position, size_com, income_class, alpha, beta))

    df_attr = pd.read_csv("node_attributes_g0.csv")  # creato dallo script 1

    # id -> 0/1
    gender_map = dict(zip(df_attr["nodo"].astype(int),
                      df_attr["genere"].map({"M": 0, "F": 1}).astype(int)))

    # (opzionale) controllo: devono essere 100000
    assert len(gender_map) == N_c

    # assegno i generi corretti ai cittadini (quelli usati per costruire la rete)
    for c in CITIZEN:
        c.gender = gender_map[c.ID]

    for c in CITIZEN:
        c.beta = 1.0 if c.gender == 0 else female_min
        
    for c in CITIZEN:
        #c.alpha = random_alpha()
        c.alpha = random.uniform(0.0, 0.4) if c.gender == 0 else random.uniform(0.6, 1.0)
        
    male_sum = 0.0
    female_sum = 0.0
    male_count = 0
    female_count = 0

    for c in CITIZEN:
        if c.gender == 0:
            male_sum += c.alpha
            male_count += 1
        else:
            female_sum += c.alpha
            female_count += 1

    male_mean = male_sum / male_count if male_count > 0 else 0.0
    female_mean = female_sum / female_count if female_count > 0 else 0.0

    print(f"Alpha medio iniziale uomini = {male_mean:.4f}")
    print(f"Alpha medio iniziale donne  = {female_mean:.4f}")

    # --- SEGGI ---
    SEATS = []
    for i in range(N_s):
        geo = exact_geo_seats(i, N_s)
        SEATS.append(Seat(i, geo, True))

    # --- BASE EDGES ---
    BASE_EDGES = load_edges(BASE_EDGE_FILE)
    build_neighbors(CITIZEN, BASE_EDGES)


def worker_rep(task):
    """
    Esegue UNA singola replica per un dato SIGMA.
    task = (SIGMA, rep_id)

    Ritorna:
      (SIGMA, payload) dove payload =
        (green_seats, all_avg, income_avg[5], comm_avg[20], gender_avg[2])
      oppure (SIGMA, None) se giant vuota.
    """
    SIGMA, rep_id = task
    global CITIZEN, SEATS, BASE_EDGES

    # 1) crea un nuovo grafo rewired
    rewired_edges = rewire_edges(BASE_EDGES, N_c, REWIRE_P, 10)

    # 2) aggiorna neighbors
    build_neighbors(CITIZEN, rewired_edges)

    # 3) giant component del grafo rewired
    gset = giant_component(CITIZEN)
    GIANT_CITIZEN = [CITIZEN[i] for i in gset]
    if len(GIANT_CITIZEN) == 0:
        return (SIGMA, None)

    # conteggi per medie nella giant
    tot_income = [0] * 5
    tot_comm = [0] * 20
    for p in GIANT_CITIZEN:
        tot_income[income_index[p.income]] += 1
        tot_comm[community_index[p.geo]] += 1

    # 4) reset alpha/beta e seggi
    for p in CITIZEN:
        #p.alpha = random_alpha()
        if p.gender == 0:   # uomo
            p.alpha = random.uniform(0.0, 0.4)
        else:             # donna
            p.alpha = random.uniform(0.6, 1.0)
        #p.beta = (1 - min_beta[p.income]) * random.random() + min_beta[p.income]
        if p.gender == 0:
            p.beta = 1
        else:
            p.beta = female_min
    for s in SEATS:
        s.vote = True

    # 5) SIMULAZIONE COMPLETA (su GIANT_CITIZEN)
    for _ in range(election):

        # alpha medio per regione (solo giant)
        alpha_community = [0.0] * 20
        size_community = [0.0] * 20
        for cit in GIANT_CITIZEN:
            idx = community_index[cit.geo]
            size_community[idx] += 1.0
            alpha_community[idx] += cit.alpha
        for i in range(20):
            if size_community[i] > 0:
                alpha_community[i] /= size_community[i]

        # elezione seggi
        for i in range(N_s):
            community = SEATS[i].geo
            SEATS[i].vote = (random.random() < alpha_community[community_index[community]])

        # cicli di policy
        for _policy in range(policy_x_election):

            # votazione policy
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

    # 6) MISURE FINALI (UNA replica)
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

    # ====== GENERE (NUOVO): medie finali per sesso nella giant ======
    alpha_gender_sum = [0.0, 0.0]  # 0=male, 1=female
    tot_gender = [0, 0]
    for p in GIANT_CITIZEN:
        g = p.gender
        alpha_gender_sum[g] += p.alpha
        tot_gender[g] += 1

    gender_avg = [0.0, 0.0]
    for g in (0, 1):
        if tot_gender[g] > 0:
            gender_avg[g] = alpha_gender_sum[g] / float(tot_gender[g])

    return (SIGMA, (green_seats, all_avg, income_avg, comm_avg, gender_avg))


def main():
    out1 = f"{POLICY_NAME}01_g0_REGRESSIVE_alfaF.txt"
    out2 = f"{POLICY_NAME}012_g0_REGRESSIVE_alfaF.txt"
    out3 = f"{POLICY_NAME}013_g0_REGRESSIVE_alfaF.txt"   # ====== NUOVO FILE 3 ======

    header1 = "income\tPP\tpolicy\telection\talpha_mean\talpha_std\talpha_se\tpolicy_type\tstep\tgreen_seats_mean\tgreen_seats_std\tgreen_seats_se\tsigma\tgamma\tbeta\tgreen_policy\n"
    header2 = "CCAA\tPP\tpolicy\telection\talpha_mean\talpha_std\talpha_se\tpolicy_type\tstep\tgreen_seats_mean\tgreen_seats_std\tgreen_seats_se\tsigma\tgamma\tbeta\n"
    header3 = "gender\tPP\tpolicy\telection\talpha_mean\talpha_std\talpha_se\tpolicy_type\tstep\tgreen_seats_mean\tgreen_seats_std\tgreen_seats_se\tsigma\tgamma\tbeta\n"

    nproc = 12

    print("Policy scelta:", POLICY_NAME, pol_eff_incG)
    print("SIGMA_VALUES:", SIGMA_VALUES)
    print("REPETITIONS:", REPETITIONS, "nproc:", nproc)
    print("BASE_EDGE_FILE:", BASE_EDGE_FILE)

    tasks = [(s, r) for s in SIGMA_VALUES for r in range(REPETITIONS)]

    green_vals  = {s: [] for s in SIGMA_VALUES}
    all_vals    = {s: [] for s in SIGMA_VALUES}
    income_vals = {s: [[] for _ in range(5)] for s in SIGMA_VALUES}
    comm_vals   = {s: [[] for _ in range(20)] for s in SIGMA_VALUES}

    # ====== NUOVO: contenitore per genere ======
    gender_vals = {s: [[] for _ in range(2)] for s in SIGMA_VALUES}  # [ [male reps], [female reps] ]

    rep_done = {s: 0 for s in SIGMA_VALUES}

    t0 = perf_counter()

    with Pool(processes=nproc, initializer=init_process) as pool:
        for sigma, payload in pool.imap_unordered(worker_rep, tasks, chunksize=1):
            rep_done[sigma] += 1
            print(f"replica {rep_done[sigma]}/{REPETITIONS} per sigma = {sigma} completata", flush=True)

            if payload is None:
                continue

            g, a_all, inc_avg, com_avg, gen_avg = payload
            green_vals[sigma].append(g)
            all_vals[sigma].append(a_all)

            for j in range(5):
                income_vals[sigma][j].append(inc_avg[j])
            for i in range(20):
                comm_vals[sigma][i].append(com_avg[i])

            # ====== NUOVO: salva medie genere (replica) ======
            gender_vals[sigma][0].append(gen_avg[0])  # male
            gender_vals[sigma][1].append(gen_avg[1])  # female

    elapsed_min = (perf_counter() - t0) / 60.0
    print(f"Tutte le repliche finite. Tempo totale: {elapsed_min:.1f} minuti")

    # =========================
    # CALCOLO STATISTICHE + SCRITTURA FILE
    # =========================
    with open(out1, "w") as f, open(out2, "w") as f2, open(out3, "w") as f3:
        f.write(header1)
        f2.write(header2)
        f3.write(header3)

        step = FINAL_STEP
        policy_type_out = "X"

        region_keys = list(community_index.keys())
        income_keys = list(income_index.keys())

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

            # ====== NUOVO: statistiche genere ======
            male_mean, male_std, male_se, _ = mean_std_se(gender_vals[SIGMA][0])
            fem_mean,  fem_std,  fem_se,  _ = mean_std_se(gender_vals[SIGMA][1])

            # ----- FILE 1: income + ALL -----
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

            # ----- FILE 3: genere + ALL -----
            gender_labels = ["MALE", "FEMALE"]
            gender_stats = [
                (male_mean, male_std, male_se),
                (fem_mean,  fem_std,  fem_se),
            ]

            for idx in (0, 1):
                m, s, se = gender_stats[idx]
                f3.write(
                    gender_labels[idx] + "\t" +
                    str(pp_x_policy) + "\t" + str(policy_x_election) + "\t" + str(election) + "\t" +
                    str(round(m, 4)) + "\t" +
                    str(round(s, 4)) + "\t" +
                    str(round(se, 4)) + "\t" +
                    policy_type_out + "\t" +
                    str(step) + "\t" +
                    str(round(green_mean, 4)) + "\t" +
                    str(round(green_std, 4)) + "\t" +
                    str(round(green_se, 4)) + "\t" +
                    str(SIGMA) + "\t" + str(decay) + "\t" + str(BETA) + "\n"
                )

            f3.write(
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

    print("Finito. File scritti:", out1, out2, out3)


if __name__ == "__main__":
    main()
