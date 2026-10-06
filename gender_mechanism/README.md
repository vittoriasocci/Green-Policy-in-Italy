# Gender Mechanism

This directory contains the simulations used to investigate gender-related differences in climate-policy support.

The analysis considers two mechanisms:

1. differences in self-efficacy between men and women;
2. gender assortativity in the social network.

Additional simulations consider differences in the initial distribution of green propensity between men and women.

## Simulation scripts

Three national policy scenarios are considered:

```text
regressive.py
progressive.py
middle.py
```

These scripts assume the same initial green-propensity distribution for men and women and are used to study the interaction between gender-dependent self-efficacy and gender assortativity.

The corresponding:

```text
regressive_alfaF.py
progressive_alfaF.py
middle_alfaF.py
```

scripts introduce different initial green-propensity distributions by gender.

In these scripts, initial green propensity is generated from:

```text
Men:    alpha ~ U[0.0, 0.4]
Women:  alpha ~ U[0.6, 1.0]
```

## Gender-dependent self-efficacy

Male self-efficacy is fixed at:

```text
beta_M = 1
```

Female self-efficacy is controlled by:

```python
female_min = 1
```

and can be set to:

```text
0
0.25
0.50
0.75
1
```

Thus, `female_min = 1` represents equal self-efficacy between men and women, while lower values introduce increasing gender asymmetry.

## Gender assortativity

Gender assortativity is controlled through the social network supplied as input.

The available network configurations correspond to:

```text
lambda = -8, -4, -2, 0, 2, 4, 8
```

where:

- `lambda < 0` represents gender heterophily;
- `lambda = 0` represents neutral gender mixing;
- `lambda > 0` represents gender homophily.

The corresponding edge-list files are:

```text
last_created_network_21_negativeg8.txt
last_created_network_21_negativeg4.txt
last_created_network_21_negativeg2.txt
last_created_network_21.txt
last_created_network_21_g2.txt
last_created_network_21_g4.txt
last_created_network_21_g8.txt
```

Corresponding `node_attributes_*.csv` files contain the gender attributes used when generating each network.

When changing the value of gender assortativity, the network edge list and node-attribute file must correspond to the same network configuration.

## Peer influence

These simulations use:

```text
sigma = 0.05
```

by default.

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

Each simulation requires:

- `functions.py`;
- one `last_created_network_21*.txt` network file;
- the corresponding `node_attributes_*.csv` file.

For example, for neutral gender mixing (`lambda = 0`):

```text
last_created_network_21.txt
node_attributes_g0.csv
```

must be selected.

## Output

Each simulation generates three output files containing results aggregated by:

1. income class and national population;
2. Italian region and national population;
3. gender and national population.

The output includes the mean, standard deviation, and standard error calculated across simulation repetitions.

## Running the simulations

First select the desired policy script, for example:

```bash
python regressive.py
```

Then configure:

```python
female_min = 0.5
```

and select the appropriate network and node-attribute files for the desired value of gender assortativity.

To study gender differences in initial green propensity, use the corresponding `_alfaF.py` script, for example:

```bash
python regressive_alfaF.py
```

> **Important:** The network edge list and the node-attribute file must refer to the same value of gender assortativity.
