# Social Network Generation

This directory contains the code and input data used to generate the social layer of the agent-based model.

The social network consists of 100,000 citizens distributed across the 20 Italian regions and five income classes. Connections between citizens are generated using a stochastic block model (SBM) in which link probabilities depend on geographical proximity, socioeconomic similarity, and gender assortativity.

## Files

- `generate_network.py`: generates the social network and the corresponding node attributes.
- `functions.py`: contains the classes, demographic distributions, and auxiliary functions used for network generation.
- `distanze_regioni_centroidi_km.csv`: contains the geographical distances between Italian regions.
- `last_created_network_21*.txt`: pre-generated network edge lists for different values of gender assortativity lambda = -8,-4,-2,0,2,4,8.
- `node_attributes_*.csv`: node attributes associated with the corresponding networks.

## Network parameters

The main parameters controlling network generation are:

- `theta = 56`: geographical distance parameter; FIXED
- `delta = 40`: socioeconomic distance parameter; FIXED
- `k = 1`: baseline network-density parameter; FIXED
- `g`: gender assortativity parameter, corresponding to `lambda` in the paper. To be varied in {-8,-4,-2,0,2,4,8}

The parameter `g` controls gender mixing:

- `g = 0`: neutral gender mixing;
- `g > 0`: gender homophily;
- `g < 0`: gender heterophily.

The network configurations included in this directory correspond to:

```text
g = -8, -4, -2, 0, 2, 4, 8
```

## Input

The network-generation script requires:

```text
functions.py
distanze_regioni_centroidi_km.csv
```

The geographical distance matrix present in `distanze_regioni_centroidi_km.csv` is read directly by `generate_network.py`, while the socioeconomic distributions and model functions are defined in `functions.py`.

## Output

The script generates:

- a network edge list;
- a file containing node attributes;

The pre-generated network files included in this directory can be used directly by the simulation scripts in the other directories without regenerating the network.

## Running the script

From this directory, run:

```bash
python generate_network.py
```

The parameters controlling network generation can be modified directly in the script before execution.

> **Note:** Network generation for 100,000 agents is computationally demanding. For reproducing the simulation experiments, the pre-generated network files provided in the repository can be used directly.
