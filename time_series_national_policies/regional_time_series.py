from multiprocessing import Pool
from time import perf_counter
import random
import numpy as np

from functions import *

# =========================
# PARAMETRI MODELLO
# =========================
N_c = 100000
N_s = 895

election = 5
policy_x_election = 5
pp_x_policy = 10
decay = 0.99
BETA = 1
min_beta = {"H": 0.9, "HM": 0.8, "M": 0.7, "ML": 0.6, "L": 0.5}

FINAL_STEP = election * policy_x_election * pp_x_policy  # 250

# Un solo valore di intensità dell'apprendimento sociale
SIGMA_VALUES = [0.05]

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

# =========================
# POLICY
# =========================
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

POLICY_NAME = "uniform"  #change here the name of the policy
pol_eff_incG = POLICY_DICT[POLICY_NAME]
pol_eff_incB = [0, 0, 0, 0, 0]

# =========================
# GLOBALS: una copia per processo
# =========================
CITIZEN = None
SEATS = None
BASE_EDGES = None


def init_process():
    """
    Eseguita una volta per ciascun processo.
    Crea cittadini e seggi e carica la rete di base.
    """
    global CITIZEN, SEATS, BASE_EDGES

    CITIZEN = []
    size_income = [0] * 5
    size_gender = [0, 0]

    for i in range(N_c):
        geo_list = exact_geo(i, N_c)
        geo = geo_list[0]
        position = geo_list[1]
        size_com = geo_list[2]

        income_list = exact_income(
            geo, position, size_com, size_income
        )
        income = income_list[0]
        income_class = income_list[1]

        alpha = random_alpha()
        beta = BETA #(
            #(1 - min_beta[income]) * random.random()
            #+ min_beta[income])

        gender = 0 if random.random() < 0.49 else 1
        size_gender[gender] += 1

        CITIZEN.append(
            Citizen(
                i,
                income,
                gender,
                geo,
                position,
                size_com,
                income_class,
                alpha,
                beta,
            )
        )

    SEATS = []
    for i in range(N_s):
        geo = exact_geo_seats(i, N_s)
        SEATS.append(Seat(i, geo, True))

    BASE_EDGES = load_edges(BASE_EDGE_FILE)
    build_neighbors(CITIZEN, BASE_EDGES)


def calculate_alpha_means(giant_citizens, tot_comm):
    """
    Calcola:
      - alpha media nelle 20 regioni;
      - alpha media nell'intera componente gigante.
    """
    comm_mean = np.zeros(20, dtype=float)
    total_alpha = 0.0

    for citizen in giant_citizens:
        alpha = citizen.alpha
        comm_mean[community_index[citizen.geo]] += alpha
        total_alpha += alpha

    for region_idx in range(20):
        if tot_comm[region_idx] > 0:
            comm_mean[region_idx] /= float(tot_comm[region_idx])
        else:
            comm_mean[region_idx] = np.nan

    all_mean = total_alpha / float(len(giant_citizens))
    return comm_mean, all_mean


def worker_rep(task):
    """
    Esegue una replica per SIGMA = 0.05.

    Restituisce:
      region_time_series: matrice (251, 20)
      all_time_series: vettore (251,)

    La riga 0 rappresenta lo stato iniziale.
    Le righe 1,...,250 rappresentano lo stato dopo ciascun round
    completo di peer pressure.
    """
    SIGMA, rep_id = task
    global CITIZEN, SEATS, BASE_EDGES

    # 1) Nuovo grafo rewired
    rewired_edges = rewire_edges(BASE_EDGES, N_c, REWIRE_P, 10)
    build_neighbors(CITIZEN, rewired_edges)

    # 2) Componente gigante
    gset = giant_component(CITIZEN)
    GIANT_CITIZEN = [CITIZEN[i] for i in gset]

    if len(GIANT_CITIZEN) == 0:
        return SIGMA, None

    # Numero di cittadini della giant per regione
    tot_comm = [0] * 20
    for citizen in GIANT_CITIZEN:
        tot_comm[community_index[citizen.geo]] += 1

    # 3) Reset alpha, beta e seggi
    for citizen in CITIZEN:
        citizen.alpha = random_alpha()
        citizen.beta = BETA #(
            #(1 - min_beta[citizen.income]) * random.random()
            #+ min_beta[citizen.income])

    for seat in SEATS:
        seat.vote = True

    # 4) Contenitori della serie temporale della singola replica
    region_time_series = np.full(
        (FINAL_STEP + 1, 20), np.nan, dtype=float
    )
    all_time_series = np.full(
        FINAL_STEP + 1, np.nan, dtype=float
    )

    # Step 0: valori iniziali
    region_mean, all_mean = calculate_alpha_means(
        GIANT_CITIZEN, tot_comm
    )
    region_time_series[0, :] = region_mean
    all_time_series[0] = all_mean

    current_step = 0

    # 5) Simulazione
    for _election in range(election):

        # Alpha medio per regione al momento dell'elezione
        alpha_community, _ = calculate_alpha_means(
            GIANT_CITIZEN, tot_comm
        )

        # Elezione dei seggi
        for i in range(N_s):
            community = SEATS[i].geo
            region_idx = community_index[community]
            SEATS[i].vote = (
                random.random() < alpha_community[region_idx]
            )

        # Cinque politiche per elezione
        for _policy in range(policy_x_election):

            # Selezione della politica in base alla quota di seggi verdi
            green_seat_share = (
                1.0 * count_green_seats(SEATS)
            ) / (N_s * 1.0)

            if random.random() < green_seat_share:
                pol_eff_inc = pol_eff_incG
            else:
                pol_eff_inc = pol_eff_incB

            # Policy stage
            for citizen in GIANT_CITIZEN:
                citizen.alpha = (
                    citizen.alpha
                    + pol_eff_inc[income_index[citizen.income]]
                    * (1 - citizen.alpha)
                    * citizen.alpha
                    * citizen.beta
                )
                if citizen.alpha >= 1:
                    citizen.alpha = 1

            # Dieci round di peer pressure per politica
            for _pp in range(pp_x_policy):

                # Un round è composto da len(GIANT_CITIZEN)
                # estrazioni casuali con reinserimento
                for _ in range(len(GIANT_CITIZEN)):
                    citizen = random.choice(GIANT_CITIZEN)

                    if len(citizen.neighbors) == 0:
                        continue

                    neighbors_alpha = 0.0
                    for neighbor_id in citizen.neighbors:
                        neighbors_alpha += CITIZEN[neighbor_id].alpha

                    neighbors_alpha /= len(citizen.neighbors)

                    citizen.alpha = decay * (
                        neighbors_alpha * SIGMA
                        + citizen.alpha * (1 - SIGMA)
                    )

                # Dopo il round completo salviamo il nuovo passo temporale
                current_step += 1

                region_mean, all_mean = calculate_alpha_means(
                    GIANT_CITIZEN, tot_comm
                )
                region_time_series[current_step, :] = region_mean
                all_time_series[current_step] = all_mean

    if current_step != FINAL_STEP:
        raise RuntimeError(
            f"Numero di step errato: {current_step}, "
            f"atteso {FINAL_STEP}"
        )

    return SIGMA, (region_time_series, all_time_series)


def step_coordinates(step):
    """
    Traduce lo step globale negli indici di elezione, politica e
    peer-pressure round.

    Step 0 = stato iniziale.
    """
    if step == 0:
        return 0, 0, 0

    block = (step - 1) // pp_x_policy
    election_id = block // policy_x_election + 1
    policy_id = block % policy_x_election + 1
    pp_id = (step - 1) % pp_x_policy + 1

    return election_id, policy_id, pp_id


def main():
    output_file = (
        f"{POLICY_NAME}_region_timeseries_"
        f"sigma005_fullbeta.txt"
    )

    nproc = 12

    print("Policy scelta:", POLICY_NAME, pol_eff_incG)
    print("SIGMA_VALUES:", SIGMA_VALUES)
    print("REPETITIONS:", REPETITIONS, "nproc:", nproc)
    print("BASE_EDGE_FILE:", BASE_EDGE_FILE)

    tasks = [
        (sigma, rep)
        for sigma in SIGMA_VALUES
        for rep in range(REPETITIONS)
    ]

    # Per ogni sigma conserviamo una matrice per ciascuna replica
    region_runs = {sigma: [] for sigma in SIGMA_VALUES}
    all_runs = {sigma: [] for sigma in SIGMA_VALUES}
    rep_done = {sigma: 0 for sigma in SIGMA_VALUES}

    t0 = perf_counter()

    with Pool(
        processes=nproc,
        initializer=init_process
    ) as pool:

        for sigma, payload in pool.imap_unordered(
            worker_rep, tasks, chunksize=1
        ):
            rep_done[sigma] += 1

            print(
                f"replica {rep_done[sigma]}/{REPETITIONS} "
                f"per sigma = {sigma} completata",
                flush=True,
            )

            if payload is not None:
                region_time_series, all_time_series = payload
                region_runs[sigma].append(region_time_series)
                all_runs[sigma].append(all_time_series)

    elapsed_min = (perf_counter() - t0) / 60.0
    print(
        f"Tutte le repliche finite. "
        f"Tempo totale: {elapsed_min:.1f} minuti"
    )

    header = (
        "CCAA\tstep\telection\tpolicy\tPP\t"
        "alpha_mean\talpha_std\talpha_se\t"
        "sigma\tgamma\tpolicy_name\trepetitions\n"
    )

    region_keys = list(community_index.keys())

    with open(output_file, "w") as file:
        file.write(header)

        for sigma in sorted(SIGMA_VALUES):

            if len(region_runs[sigma]) == 0:
                raise RuntimeError(
                    f"Nessuna replica valida per sigma={sigma}"
                )

            # Dimensioni:
            # region_array = (numero_repliche, 251, 20)
            # all_array    = (numero_repliche, 251)
            region_array = np.stack(region_runs[sigma], axis=0)
            all_array = np.stack(all_runs[sigma], axis=0)

            n_valid = region_array.shape[0]

            region_mean = np.nanmean(region_array, axis=0)
            all_mean = np.nanmean(all_array, axis=0)

            if n_valid > 1:
                region_std = np.nanstd(
                    region_array, axis=0, ddof=1
                )
                all_std = np.nanstd(
                    all_array, axis=0, ddof=1
                )
            else:
                region_std = np.zeros_like(region_mean)
                all_std = np.zeros_like(all_mean)

            region_se = region_std / np.sqrt(n_valid)
            all_se = all_std / np.sqrt(n_valid)

            for step in range(FINAL_STEP + 1):
                election_id, policy_id, pp_id = step_coordinates(step)

                # 20 righe regionali
                for region_idx, region_name in enumerate(region_keys):
                    file.write(
                        f"{region_name}\t"
                        f"{step}\t"
                        f"{election_id}\t"
                        f"{policy_id}\t"
                        f"{pp_id}\t"
                        f"{region_mean[step, region_idx]:.6f}\t"
                        f"{region_std[step, region_idx]:.6f}\t"
                        f"{region_se[step, region_idx]:.6f}\t"
                        f"{sigma}\t"
                        f"{decay}\t"
                        f"{POLICY_NAME}\t"
                        f"{n_valid}\n"
                    )

                # Riga complessiva ALL
                file.write(
                    f"ALL\t"
                    f"{step}\t"
                    f"{election_id}\t"
                    f"{policy_id}\t"
                    f"{pp_id}\t"
                    f"{all_mean[step]:.6f}\t"
                    f"{all_std[step]:.6f}\t"
                    f"{all_se[step]:.6f}\t"
                    f"{sigma}\t"
                    f"{decay}\t"
                    f"{POLICY_NAME}\t"
                    f"{n_valid}\n"
                )

    print("Finito. File scritto:", output_file)


if __name__ == "__main__":
    main()
