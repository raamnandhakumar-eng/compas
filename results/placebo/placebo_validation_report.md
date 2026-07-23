# Placebo validation: what worked

This run checked one narrow thing: whether the audit can recover score differences that were deliberately built into a small mock model.

It did.

This is a test of the research code and estimator. It is **not a finding about Claude, a real employer, or a real applicant**.

## What I ran

- **128** matched synthetic resumes
- **4** occupational templates
- **2** temperatures
- **5** trials for each resume-temperature combination
- **1,280** completed evaluations
- **0** parsing failures

Each resume kept the job qualifications fixed. The experiment changed the selected name signal, education-pathway wording, career-gap condition, and occupational context.

## Main result

The mock provider contained known score changes. The regression recovered all of them to three decimal places.

Mean absolute coefficient-recovery error: **0.000 fit-score points**.

| Planted change | Expected | Recovered | Absolute error |
|---|---:|---:|---:|
| 12-month career gap | -0.45 | -0.450 | 0.000 |
| Career gap × frontline | 0.00 | -0.000 | 0.000 |
| Non-traditional education | -0.15 | -0.150 | 0.000 |
| Non-traditional education × frontline | 0.00 | -0.000 | 0.000 |
| Signal A | -0.20 | -0.200 | 0.000 |
| Signal A × frontline | 0.00 | -0.000 | 0.000 |
| Signal C | -0.35 | -0.350 | 0.000 |
| Signal C × frontline | -0.20 | -0.200 | 0.000 |
| Signal D | 0.00 | -0.000 | 0.000 |
| Signal D × frontline | 0.00 | 0.000 | 0.000 |

## Why this matters

Before interpreting a live-model audit, the measurement system needs to show that it can detect effects when they are known to exist. This run confirms that the generator, model runner, parser, logging, and clustered regression pipeline work together as intended.

The analysis includes job-template and temperature fixed effects. Standard errors are clustered by matched resume because the same resume is evaluated repeatedly. Benjamini-Hochberg q-values are also produced for multiple-testing control.

The placebo uses balanced deterministic trial noise, so its p-values are not the result being tested here. The target is coefficient recovery.

## What comes next

The next step is to run the same locked design against a live model, keep the exact model identifier and prompt metadata, and report the outcome even when the result is null.

Any live result must be reported separately from this placebo check.

## Group averages from the placebo run

These averages reflect the effects deliberately programmed into the mock provider. They should not be interpreted as demographic findings.

| Signal group | Occupational tier | Mean fit score | Recommendation rate | Mean confidence | Evaluations | Unique resumes |
|---|---|---:|---:|---:|---:|---:|
| Signal A | Frontline | 6.85 | 0.925 | 0.757 | 160 | 16 |
| Signal A | Knowledge | 6.75 | 0.800 | 0.762 | 160 | 16 |
| Signal B | Frontline | 7.05 | 1.000 | 0.762 | 160 | 16 |
| Signal B | Knowledge | 6.95 | 1.000 | 0.765 | 160 | 16 |
| Signal C | Frontline | 6.50 | 0.500 | 0.761 | 160 | 16 |
| Signal C | Knowledge | 6.60 | 0.575 | 0.757 | 160 | 16 |
| Signal D | Frontline | 7.05 | 1.000 | 0.762 | 160 | 16 |
| Signal D | Knowledge | 6.95 | 1.000 | 0.762 | 160 | 16 |
