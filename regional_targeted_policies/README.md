# Regionally Targeted Policy Scenarios

This directory contains the simulations used to investigate regionally differentiated climate-policy designs.

Unlike the national policy scenarios, these policies assign different policy intensities depending on whether a citizen belongs to the targeted macro-area or to the rest of the country.

## Files

- `run_regional_targeted_policies.py`: main simulation script.
- `functions.py`: contains the model classes, demographic distributions, and auxiliary functions.
- `last_created_network_21.txt`: baseline social network used as input.

## Italian macro-areas

The 20 Italian regions are grouped into three macro-areas:

### North

```text
PIE, AOS, LIG, LOMB, TREN, VEN, FRIU, EMI
```

### Centre

```text
TOSC, UMB, MAR, LAZ, ABR, MOL
```

### South

```text
CAMP, PUGL, BAS, CAL, SIC, SAR
```

## Policy scenarios

Five policy profiles are considered:

```text
Progressive
Regressive
Uniform
Middle
Bimodal
```

Each policy can target one of the three macro-areas:

```text
North
Centre
South
```

This results in 15 regionally targeted policy scenarios.

The available identifiers are:

```text
nord_prog
centro_prog
sud_prog

nord_reg
centro_reg
sud_reg

nord_uni
centro_uni
sud_uni

nord_mid
centro_mid
sud_mid

nord_bim
centro_bim
sud_bim
```

The scenario is selected through:

```python
POLICY_NAME = "nord_mid"
```

For example:

```python
POLICY_NAME = "sud_prog"
```

selects a Progressive policy targeted at the South.

## Peer influence

The script evaluates:

```text
sigma = 0, 0.05, 0.10, ..., 0.95, 1
```

## Simulation settings

The main settings are:

```text
Citizens:          100,000
Political seats:   895
Self-efficacy:     beta = 1
Repetitions:       100
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

For the selected scenario, two output files are generated:

```text
<POLICY_NAME>01_2.txt
<POLICY_NAME>012_2.txt
```

The first contains results aggregated by income class together with the national aggregate.

The second contains results for each of the 20 Italian regions together with the national aggregate.

For each value of `sigma`, the output reports summary statistics across simulation repetitions, including mean green propensity and green political representation.

## Running the simulation

Select the desired scenario:

```python
POLICY_NAME = "nord_mid"
```

and run:

```bash
python run_regional_targeted_policies.py
```

To reproduce all regionally targeted scenarios, run the script separately for each of the 15 values of `POLICY_NAME`.
