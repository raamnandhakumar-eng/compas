# COMPAS

**Candidate Outcome Measurement and Prompt Audit Suite**

COMPAS is a reproducible audit of how a language model evaluates job candidates when their qualifications remain fixed but selected career signals change.

The project focuses on three questions that matter for labor-market access:

1. Does a 12-month career gap affect a model’s assessment of an otherwise identical candidate?
2. Does a non-traditional education pathway affect that assessment?
3. Do these effects differ between frontline and knowledge-work occupations?

A separate extension examines perceived name signals. That extension remains deliberately blocked until the name stimuli pass a new human validation study.

> **Important:** This repository is unrelated to the criminal-risk assessment system also called COMPAS. It currently reports pipeline-validation results only. No live Claude findings are presented.

## Why this project matters

Language models are increasingly used in tasks that resemble screening, ranking, and candidate evaluation. Even when a model is not the final decision-maker, small shifts in scores or recommendations can influence who receives further consideration.

Career interruptions and non-traditional education are especially important signals to study. They are common among caregivers, career changers, returning workers, veterans, immigrants, and people who complete education through part-time or alternative routes. These signals may also be interpreted differently across occupations. A career gap may carry one meaning in a frontline operations role and another in a knowledge-work role.

COMPAS turns these questions into a controlled audit. Rather than comparing different applicants, it creates matched resumes in which experience, skills, achievements, employer history, education level, target role, formatting, and resume length are held constant. Only the treatment signal changes.

## Study structure

The project now has two explicitly separated research tracks.

| Track | Research question | Status | Planned scale |
|---|---|---|---:|
| Core labor-market audit | Career gap × education pathway × occupational context | Design locked and executable; live run not completed | 640 evaluations |
| Name-signal extension | Validated perceived-name signals plus the core treatments | Blocked pending a successful replacement pretest | 2,560 evaluations |

This separation was made before any live model output was observed. It allows the independently identified career-gap and education-pathway questions to proceed without weakening the validation standard for the name-signal study.

## Current status

- **Pipeline validation:** Complete
- **Core audit design:** Locked and executable
- **Core live audit:** Not run
- **Name-source screening:** Complete
- **First perception pretest:** Submitted but not approved
- **Name-signal extension:** Blocked
- **Human benchmark:** Not run

The most important completed result is methodological: the software and estimator recover known effects under a deterministic mock provider. This validates the research pipeline, not the behavior of Claude, employers, or real hiring systems.

## Core labor-market audit

The core audit estimates the effects of:

- a 12-month career gap;
- a traditional versus non-traditional education pathway;
- the interaction between each treatment and occupational context.

The design contains:

- **8 occupations**: 4 frontline or operational and 4 knowledge-work roles;
- **4 base profiles per occupation**;
- **32 matched base profiles**;
- **2 career-gap conditions**;
- **2 education-pathway conditions**;
- **128 unique matched resumes**;
- **5 repeated trials per resume**;
- **640 planned evaluations**.

A single control name is held fixed within each matched set. Names alternate across profile slots, but the core analysis does not estimate a name effect.

The full design is preregistered in [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md).

## Pipeline and estimator validation

Before running a live model audit, the complete workflow was tested using a deterministic mock provider with known planted effects.

The core placebo validation completed:

- **640 of 640 evaluations**;
- **0 failed evaluations**;
- **0 refusals**;
- **128 matched resumes**;
- **32 base profiles**;
- **8 occupations**;
- randomized execution order;
- no selective reruns.

The pipeline recovered the planted fit-score effects exactly:

| Treatment | Planted effect | Recovered effect |
|---|---:|---:|
| 12-month career gap | -0.450 | -0.450 |
| Non-traditional education | -0.150 | -0.150 |
| Career gap × frontline | 0.000 | 0.000 |
| Non-traditional education × frontline | 0.000 | 0.000 |

The mock recommendation outcome was constant, so the recommendation model was correctly reported as **not estimable** rather than interpreted from numerical noise.

See [`results/core/placebo_validation_report.md`](results/core/placebo_validation_report.md) for the full report.

These results establish that the workflow can generate the matched design, randomize evaluations, preserve raw responses and failures, estimate the preregistered models, detect non-estimable outcomes, and recover known effects. They do not establish how a live model will respond.

## Name-signal extension

The name-signal extension studies whether a model responds differently to validated perceived-name signals while qualifications remain unchanged.

The names are treated as experimental stimuli, not as evidence of anyone’s actual race, ethnicity, gender, nationality, or socioeconomic status.

Source screening uses public data from:

- the 2020 U.S. Census first-name tables by race and Hispanic origin;
- the 2020 Census first-name tables by sex;
- the 2020 Census surname tables;
- Social Security Administration national first-name frequencies.

These are aggregate public records. They help assess whether a name is common enough and whether its broad population pattern supports inclusion in a perception study. They do not turn a name into an identity label.

### What happened in the first pretest

The submitted workbook contained **150 respondent IDs** and **1,200 complete ratings**. Every respondent rated all eight names, with no duplicate respondent-name pairs and no missing rating fields.

The names were recognized strongly in the intended direction:

- intended-group agreement ranged from **88.0% to 97.3%**;
- perceived-male agreement ranged from **94.0% to 98.7%**;
- median confidence was at least **4 out of 5** for every name.

However, the pretest did not pass the locked protocol for two independent reasons.

First, the export did not include consent or attention-check fields, so respondent eligibility could not be verified. Second, the names were not sufficiently balanced on other perceptions:

| Balance measure | Observed range | Maximum allowed |
|---|---:|---:|
| Familiarity | 0.947 | 0.750 |
| Perceived socioeconomic status | 1.130 | 0.750 |
| Unusualness | 1.713 | 0.750 |

The project therefore does not relax the thresholds, relabel simulated responses as human evidence, publish participant-level data without documented permission, or proceed with an unapproved name experiment.

Instead, the failed pretest is preserved as a genuine methodological result. It shows that strong demographic recognition is not sufficient: names must also be comparable on familiarity, perceived class, and unusualness.

Aggregate results are available in:

- [`results/name_validation/submitted_survey_name_summary.csv`](results/name_validation/submitted_survey_name_summary.csv)
- [`results/name_validation/submitted_survey_balance_tests.csv`](results/name_validation/submitted_survey_balance_tests.csv)
- [`results/name_validation/submitted_survey_validation_report.md`](results/name_validation/submitted_survey_validation_report.md)
- [`data/name_validation/submitted_survey_manifest.csv`](data/name_validation/submitted_survey_manifest.csv)

Raw participant-level responses are not published because public data-sharing permission was not documented.

### Replacement-name procedure

The recovery plan is described in [`docs/name_pretest_recovery_plan.md`](docs/name_pretest_recovery_plan.md).

A future pilot will evaluate a larger pool of candidate names. The repository includes an exhaustive Python selector that searches all feasible two-name panels and minimizes the largest imbalance across familiarity, socioeconomic perception, and unusualness.

```bash
compas-select-balanced-names \
  --input results/name_validation/replacement_candidate_summary.csv
```

The selector does not guarantee approval. It exits with failure when the best available panel still violates a locked threshold.

## Outcomes and statistical analysis

The primary outcomes are:

1. fit score;
2. interview recommendation;
3. model confidence.

The analysis uses:

- matched-set fixed effects;
- occupation fixed effects;
- temperature fixed effects;
- standard errors clustered by matched resume;
- Benjamini-Hochberg correction for multiple testing;
- linear models for fit and confidence;
- a linear probability model for recommendations;
- logistic regression as a robustness check when estimable;
- failure and refusal sensitivity analyses;
- treatment means and 95% confidence intervals.

All failures and refusals remain in the raw data. The design prohibits selective reruns and records the exact model ID, API version, prompt version, temperature, trial number, latency, raw response, parser status, and error type.

## Public data and occupational design

The occupational sample is grounded in O*NET and Bureau of Labor Statistics fields stored in [`data/occupations/occupation_registry.csv`](data/occupations/occupation_registry.csv).

The sample varies in occupational setting, employment size, wages, education requirements, and frontline versus knowledge-work classification. This variation supports analysis of whether the same candidate signal is interpreted differently across labor-market contexts.

Public source files can be downloaded and rebuilt with:

```bash
python scripts/download_public_data.py
python scripts/build_name_registry.py
python scripts/build_occupation_registry.py
```

## Reproducing the project

Create an environment and run the complete validation workflow:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make reproduce
```

Reproduce only the core placebo audit:

```bash
make core-reproduce
```

Run the live core audit only after setting private credentials and locking one exact model ID:

```bash
pip install -e ".[api]"
export ANTHROPIC_API_KEY="..."
export ANTHROPIC_MODEL="exact-model-id"
make core-live
```

API credentials must never be committed to the repository.

## Repository guide

- [`FELLOWSHIP_RESEARCH_BRIEF.md`](FELLOWSHIP_RESEARCH_BRIEF.md): concise overview of the research contribution
- [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md): locked core-audit design
- [`docs/preregistration.md`](docs/preregistration.md): full name-signal design
- [`docs/deviations_from_preregistration.md`](docs/deviations_from_preregistration.md): dated design changes
- [`docs/name_pretest_recovery_plan.md`](docs/name_pretest_recovery_plan.md): replacement-name procedure
- [`docs/limitations.md`](docs/limitations.md): interpretive limits
- [`docs/ethics_statement.md`](docs/ethics_statement.md): ethical safeguards
- [`docs/model_card.md`](docs/model_card.md): system and evaluation documentation
- [`results/core/placebo_validation_report.md`](results/core/placebo_validation_report.md): core pipeline validation

## Interpretation and limits

COMPAS is an audit of model behavior under a controlled synthetic design. It does not measure employer behavior, prove intent, establish unlawful discrimination, or identify the demographic identity of any individual.

Any live result will apply only to the exact model, prompt, run period, treatment definitions, and occupational sample used in the study. Results from eight occupations should not be generalized to the entire labor market.

The project is intended to contribute evidence about workforce re-entry, credential alternatives, occupational mobility, and algorithmic gatekeeping. Its strongest commitment is methodological: preserve the design, report failures, and distinguish clearly between what the data show and what they do not.

## License

MIT. See [`LICENSE`](LICENSE).