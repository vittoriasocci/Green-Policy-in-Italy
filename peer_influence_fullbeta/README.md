# National Policy Scenarios: Full Self-Efficacy

This directory contains the simulations used to analyse the effect of peer influence under the six national climate-policy scenarios assuming full individual self-efficacy.

In this configuration, all citizens have:

```text
beta = 1
```

The analysis evaluates how the strength of social influence (`sigma`) affects green propensity, income-group differences, regional outcomes, and political representation.

## Files

- `main_fullbeta.py`: main simulation script.
- `functions.py`: contains the model classes, demographic distributions, and auxiliary functions.
- `last_created_network_21.txt`: baseline social network used as input.

## National policy scenarios

Six national policy configurations are available:

```text
brown
uniform
regressive
progressive
bimodal
middle
```

The policy is selected in `main_fullbeta.py` through:

```python
POLICY_NAME = "brown"
```

For example:

```python
POLICY_NAME = "progressive"
```

runs the Progressive policy scenario.

## Peer influence

The strength of peer influence is controlled by `sigma`.

The script currently considers:

```python
SIGMA_VALUES = [
    0, 0.025, 0.05, ..., 0.975, 1
]
```

thus covering the complete interval from 0 to 1.

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

The social network is rewired independently for each simulation repetition.

## Input

The script requires:

```text
functions.py
last_created_network_21.txt
```
The social network used in this analysis corresponds to neutral gender mixing, i.e., lambda = 0.

No network generation is performed by this script.

## Output

For the selected policy, the script generates two output files:

```text
<POLICY_NAME>01.txt
<POLICY_NAME>012.txt
```

The first contains results aggregated by income class together with the national aggregate (`ALL`).

The second contains results for each of the 20 Italian regions together with the national aggregate (`ALL`).

For each value of `sigma`, the output reports summary statistics across simulation repetitions, including the mean, standard deviation, and standard error of green propensity and green political representation.

## Running the simulation

Select the policy in:

```python
POLICY_NAME = "brown"
```

and then run:

```bash
python main_fullbeta.py
```

To reproduce all six national policy scenarios, run the script separately for each value of `POLICY_NAME`.
