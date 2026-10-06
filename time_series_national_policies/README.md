# Regional Time Series under National Policies

This directory contains the simulation used to analyse the temporal evolution of green propensity in each Italian region under a selected national climate-policy scenario.

Unlike the other national-policy simulations, which focus on final outcomes, this script records regional and national green propensity throughout the simulation.

## Files

- `regional_time_series.py`: main simulation script.
- `functions.py`: contains the model classes, demographic distributions, and auxiliary functions.
- `last_created_network_21.txt`: baseline social network used as input.

## National policy scenarios

The following national policy configurations are available:

```text
brown
uniform
regressive
progressive
bimodal
middle
```

The policy is selected through:

```python
POLICY_NAME = "uniform"
```

## Peer influence

The value of the peer-influence parameter is specified through:

```python
SIGMA_VALUES = [0.05]
```

The script is intended to analyse the temporal evolution for a selected value of `sigma`.

## Time series

The simulation contains 250 peer-influence steps, plus the initial state:

```text
step = 0, 1, ..., 250
```

At each step, the script records:

- mean green propensity for each of the 20 Italian regions;
- national mean green propensity.

The script performs 50 independent simulation repetitions and calculates, for every region and every time step:

- mean;
- standard deviation;
- standard error.

The national aggregate (`ALL`) is calculated in the same way.

## Simulation settings

The main settings are:

```text
Citizens:          100,000
Political seats:   895
Self-efficacy:     beta = 1
Repetitions:       50
Rewiring:          p = 0.1
Final step:        250
```

## Input

The script requires:

```text
functions.py
last_created_network_21.txt
```

## Output

The output file follows the naming convention:

```text
<POLICY_NAME>_region_timeseries_sigma005_fullbeta.txt
```

For example:

```text
uniform_region_timeseries_sigma005_fullbeta.txt
```

The file contains the following information:

```text
CCAA
step
election
policy
PP
alpha_mean
alpha_std
alpha_se
sigma
gamma
policy_name
repetitions
```

For each time step, the output includes one row for each of the 20 Italian regions and an additional `ALL` row representing the national population.

The resulting file can be used to plot the temporal evolution of regional green propensity under the selected national policy.

## Running the simulation

Select the desired national policy:

```python
POLICY_NAME = "uniform"
```

and the desired value of peer influence:

```python
SIGMA_VALUES = [0.05]
```

Then run:

```bash
python regional_time_series.py
```

> **Note:** The `sigma005` part of the current output filename is fixed in the script. If a value of `sigma` other than `0.05` is used, the output filename should be changed accordingly.
