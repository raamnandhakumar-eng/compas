# Placebo validation report

This report evaluates the measurement pipeline against a deterministic provider with transparent planted effects. It is **not evidence about Claude or any deployed hiring system**.

## Validation scale

- Successful evaluations: **1,280**
- Unique matched resumes: **128**
- Occupational templates: **4**
- Temperatures: **2**
- Repeated trials per resume-temperature cell: **5**
- Parsing failures: **0**

## Estimation

The analysis uses template and temperature fixed effects. Standard errors are clustered by matched resume because each resume is evaluated repeatedly. Benjamini-Hochberg q-values control the false discovery rate across reported coefficients.

## Recovery result

Mean absolute coefficient recovery error: **0.000 fit-score points**.

Because the placebo uses balanced deterministic trial noise, its inferential p-values are not interpreted. The validation target is coefficient recovery.

| Planted term | Expected | Estimated | Absolute error |
|---|---:|---:|---:|
| `has_gap` | -0.45 | -0.450 | 0.000 |
| `has_gap:frontline` | 0.00 | -0.000 | 0.000 |
| `nontraditional` | -0.15 | -0.150 | 0.000 |
| `nontraditional:frontline` | 0.00 | -0.000 | 0.000 |
| `signal_a` | -0.20 | -0.200 | 0.000 |
| `signal_a_frontline` | 0.00 | -0.000 | 0.000 |
| `signal_c` | -0.35 | -0.350 | 0.000 |
| `signal_c_frontline` | -0.20 | -0.200 | 0.000 |
| `signal_d` | 0.00 | -0.000 | 0.000 |
| `signal_d_frontline` | 0.00 | 0.000 | 0.000 |

## Interpretation

The purpose of this stage is estimator validation. A live-model run should use the same locked configuration, retain null results, and be reported separately from this placebo benchmark.

## Group means

| signal_group   | occupation_tier   |   mean_fit_score |   recommendation_rate |   mean_confidence |   observations |   unique_resumes |
|:---------------|:------------------|-----------------:|----------------------:|------------------:|---------------:|-----------------:|
| signal_a       | frontline         |             6.85 |                 0.925 |          0.757125 |            160 |               16 |
| signal_a       | knowledge         |             6.75 |                 0.8   |          0.762188 |            160 |               16 |
| signal_b       | frontline         |             7.05 |                 1     |          0.762375 |            160 |               16 |
| signal_b       | knowledge         |             6.95 |                 1     |          0.765188 |            160 |               16 |
| signal_c       | frontline         |             6.5  |                 0.5   |          0.761    |            160 |               16 |
| signal_c       | knowledge         |             6.6  |                 0.575 |          0.757    |            160 |               16 |
| signal_d       | frontline         |             7.05 |                 1     |          0.761625 |            160 |               16 |
| signal_d       | knowledge         |             6.95 |                 1     |          0.761813 |            160 |               16 |
