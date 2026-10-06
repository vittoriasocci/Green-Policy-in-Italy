# National Policy Scenarios: Heterogeneous Self-Efficacy

This directory contains the simulations used to analyse the national climate-policy scenarios when individual self-efficacy varies across income classes.

This analysis provides a sensitivity test of the baseline full-self-efficacy configuration.

## Files

- `main_hetebeta.py`: main simulation script.
- `functions.py`: contains the model classes, demographic distributions, and auxiliary functions.
- `last_created_network_21.txt`: baseline social network used as input.

## Heterogeneous self-efficacy

Self-efficacy depends on the citizen's income class.

The lower bounds used in the simulation are:

| Income class | Minimum beta |
|---|---:|
| H | 0.90 |
| HM | 0.80 |
| M | 0.70 |
| ML | 0.60 |
| L | 0.50 |

For each citizen, `beta` is randomly generated between the corresponding minimum value and 1.

## National policy scenarios

The following policy configurations are available:

```text
brown
uniform
regressive
progressive
bimodal
middle
```

The policy to simulate is selected through:

```python
POLICY_NAME = "brown"
```

## Peer influence

The social influence parameter is varied over:

```text
sigma = 0, 0.025, 0.05, ..., 0.975, 1
```

This allows the effect of peer influence to be compared with the full-self-efficacy case.

## Simulation settings

The main settings are:

```text
Citizens:          100,000
Political seats:   895
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
The social network used in this analysis corresponds to neutral gender mixing, i.e., lambda = 0.

No network generation is performed by this script.

## Output

For the selected policy, the script generates:

```text
<POLICY_NAME>01_hetebeta.txt
<POLICY_NAME>012_hetebeta.txt
```

The first file contains results aggregated by income class and at the national level.

The second contains results for the 20 Italian regions and at the national level.

For each value of `sigma`, the files report summary statistics across simulation repetitions.

## Running the simulation

Select the desired policy:

```python
POLICY_NAME = "progressive"
```

and run:

```bash
python main_hetebeta.py
```

The resulting outputs can be directly compared with those produced by `peer_influence_fullbeta/` to assess the effect of heterogeneous self-efficacy.
