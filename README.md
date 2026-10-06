# Green Policy in Italy

This repository contains the Python code used for the agent-based model developed in the study:

**"Public Acceptance of Climate Policies in Italy: The Role of Inequality, Social Influence, and Political Feedback"**

The model investigates the evolution of public support for climate mitigation policies in Italy, accounting for socioeconomic heterogeneity, geographical structure, social influence, political feedback, and gender-related mechanisms.

## Model overview

The model consists of a two-layer multiplex system:

- a **social layer** composed of 100,000 citizens distributed across the 20 Italian regions and five income classes;
- a **political layer** composed of 895 regional council seats.

Citizens interact through a stochastic block model (SBM) social network calibrated to reproduce geographical and socioeconomic proximity. Gender assortativity can also be introduced through the parameter `lambda`.

Citizens' green propensity evolves through two main mechanisms:

1. **Policy influence**, determined by the type of climate policy implemented and individual self-efficacy;
2. **Peer influence**, controlled by the social influence parameter `sigma`.

The political layer introduces feedback between citizens' support for green policies and political representation.

## Repository structure

```text
Green-Policy-in-Italy/
│
├── SBM_network_creation/
│   ├── generate_network.py
│   ├── functions.py
│   ├── distanze_regioni_centroidi_km.csv
│   ├── last_created_network_21*.txt
│   └── node_attributes_*.csv
│
├── peer_influence_fullbeta/
│   ├── main_fullbeta.py
│   ├── functions.py
│   └── last_created_network_21.txt
│
├── peer_influence_hetebeta/
│   ├── main_hetebeta.py
│   ├── functions.py
│   └── last_created_network_21.txt
│
├── gender_mechanism/
│   ├── regressive.py
│   ├── progressive.py
│   ├── middle.py
│   ├── regressive_alfaF.py
│   ├── progressive_alfaF.py
│   ├── middle_alfaF.py
│   ├── last_created_network_21*.txt
│   └── node_attributes_*.csv
│
├── regional_targeted_policies/
│   ├── run_regional_targeted_policies.py
│   ├── functions.py
│   └── last_created_network_21.txt
│
└── time_series_national_policies/
    ├── regional_time_series.py
    ├── functions.py
    └── last_created_network_21.txt
```

## Network generation

The `SBM_network_creation/` directory contains the code used to generate the social network.

The network is constructed using a stochastic block model in which connection probabilities depend on:

- geographical proximity;
- socioeconomic similarity;
- gender assortativity.

The main script is:

```text
SBM_network_creation/generate_network.py
```

The file

```text
distanze_regioni_centroidi_km.csv
```

contains the geographical distances used during network generation.

Different values of gender assortativity are represented by different network files. In the code, the variable `g` corresponds to the parameter `lambda` used in the paper:

- `lambda = 0`: neutral gender mixing;
- `lambda > 0`: gender homophily;
- `lambda < 0`: gender heterophily.

The corresponding network edge lists and node attributes are provided in the same directory.

## National policy scenarios

The directories

```text
peer_influence_fullbeta/
peer_influence_hetebeta/
```

contain the simulations used to analyse the effect of peer influence under the national policy scenarios.

The six national policy configurations are:

- Brown / no-green policy
- Uniform
- Regressive
- Progressive
- Bimodal
- Middle

The policy to simulate can be selected by changing:

```python
POLICY_NAME = "brown"
```

to one of:

```python
"brown"
"uniform"
"regressive"
"progressive"
"bimodal"
"middle"
```

The values of the peer-influence parameter are specified through:

```python
SIGMA_VALUES = [...]
```

The `peer_influence_fullbeta/` simulations assume full self-efficacy, whereas `peer_influence_hetebeta/` contains the simulations with heterogeneous self-efficacy.

## Gender mechanism

The `gender_mechanism/` directory contains the simulations used to investigate the interaction between gender differences in self-efficacy and gender assortativity in the social network.

Separate scripts are provided for the Regressive, Progressive, and Middle policy scenarios.

The female self-efficacy level can be selected through:

```python
female_min = 1
```

using the values:

```text
0, 0.25, 0.5, 0.75, 1
```

The gender assortativity parameter is controlled by selecting the corresponding network and node-attribute files.

Available network configurations include:

```text
lambda = -8, -4, -2, 0, 2, 4, 8
```

where negative values represent heterophily and positive values represent homophily.

## Regionally targeted policies

The directory

```text
regional_targeted_policies/
```

contains the simulations for policies targeted at different Italian macro-areas.

The three target areas are:

- North
- Centre
- South

Five policy profiles are available:

- Progressive
- Regressive
- Uniform
- Middle
- Bimodal

Each policy can be targeted at the North, Centre, or South, resulting in 15 possible scenarios.

The scenario is selected through:

```python
POLICY_NAME = "nord_mid"
```

For example:

```python
POLICY_NAME = "nord_prog"
POLICY_NAME = "centro_reg"
POLICY_NAME = "sud_bim"
```

correspond respectively to a Progressive policy targeted at the North, a Regressive policy targeted at the Centre, and a Bimodal policy targeted at the South.

For each value of `sigma`, the simulations record the final mean green propensity at the national, regional, and income-class levels.

## Time series of regional green propensity

The directory

```text
time_series_national_policies/
```

contains the script used to analyse the temporal evolution of green propensity under a selected national policy.

The policy is selected through:

```python
POLICY_NAME = "uniform"
```

and the social influence parameter through:

```python
SIGMA_VALUES = [0.05]
```

For each simulation step, the script records:

- mean green propensity for each of the 20 Italian regions;
- national mean green propensity;
- standard deviation across simulation repetitions;
- standard error across simulation repetitions.

The resulting output can be used to plot the temporal evolution of regional and national climate-policy support.

## Main simulation parameters

The main model parameters used in the simulations are:

| Parameter | Description |
|---|---|
| `N_c` | Number of citizens (100,000) |
| `N_s` | Number of political seats (895) |
| `sigma` | Strength of peer influence |
| `beta` | Individual self-efficacy |
| `lambda` (`g` in the network-generation code) | Gender assortativity |
| `decay` | Opinion decay parameter |
| `REWIRE_P` | Network rewiring probability |
| `REPETITIONS` | Number of independent simulation repetitions |

Unless otherwise specified in the individual scripts, the baseline configuration assumes full self-efficacy (`beta = 1`) and a neutral gender-mixing network (`lambda = 0`).

## Requirements

The simulations are implemented in Python and require the standard scientific Python libraries, and require the following external libraries:

```text
numpy
pandas
matplotlib
```

The code also uses Python's built-in multiprocessing module to parallelize independent simulation repetitions.

## Running the simulations

Each analysis can be run independently from its corresponding directory.

For example:

```bash
cd peer_influence_fullbeta
python main_fullbeta.py
```

or:

```bash
cd regional_targeted_policies
python run_regional_targeted_policies.py
```

Before running a simulation, check the configuration variables at the beginning of the corresponding script, particularly:

```python
POLICY_NAME
SIGMA_VALUES
REPETITIONS
BASE_EDGE_FILE
```

and, where applicable, the parameters controlling self-efficacy and gender assortativity.

## Reproducibility

The repository includes the network edge lists used as inputs for the simulations, allowing the analyses to be reproduced without regenerating the stochastic block model network.

The `SBM_network_creation/` directory is provided to document and reproduce the network-generation procedure itself.

Because the model contains stochastic components, individual simulation runs may differ. Results reported in the study are obtained by averaging over multiple independent simulation repetitions.

## Documentation

Each directory contains its own `README.md` file providing detailed information about the corresponding analysis.

The present README provides an overview of the complete repository, while the README files within each directory provide the information needed to reproduce the individual analyses.

## Authors

**Vittoria Socci**  
**Alberto Antonioni**  
**Francesca Lipari**  
**Chiara Mocenni**
