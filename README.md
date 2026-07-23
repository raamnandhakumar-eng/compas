# COMPAS

**Candidate Outcome Measurement and Prompt Audit Suite**

COMPAS is a reproducible labor-market audit of whether a resume-screening language
model changes its judgments when controlled candidate signals change and qualifications
remain fixed.

> This project is unrelated to the criminal-risk assessment system also called COMPAS.
> A distinct repository name is under consideration to reduce confusion.

## Research question

**Holding qualifications fixed, do a 12-month career gap, a non-traditional education
pathway, or validated perceived-name signals change a screening model's fit score,
interview recommendation, or confidence—and do those effects differ between frontline
and knowledge-work occupations?**

## Reviewer quick start

For a concise overview of the contribution, empirical design, research judgment, and
public-output path, read [`FELLOWSHIP_RESEARCH_BRIEF.md`](FELLOWSHIP_RESEARCH_BRIEF.md).

The project now has two explicitly separated tracks:

| Track | Question | Status | Planned scale |
|---|---|---|---:|
| Core labor-market audit | Career gap × education pathway × occupational context | Ready for a live run; not yet run | 640 evaluations |
| Name-signal extension | Validated perceived-name signals plus the core treatments | Blocked pending a successful replacement pretest | 2,560 evaluations |

This separation was locked before any live model output was observed. It preserves the
failed name pretest rather than weakening its thresholds, while allowing the
independently identified labor-market questions to proceed.

## Current status

> **Pipeline validation:** Complete  
> **Core audit design:** Locked and executable  
> **Core live audit:** Not run  
> **Name-source screening:** Complete  
> **First perception pretest:** Submitted; not approved  
> **Name-signal live extension:** Blocked  
> **Human benchmark:** Not run

No live Claude findings are reported in this repository.

## Why the split is methodologically important

The first 150-person name-perception pretest strongly recognized the intended signals,
but failed the preregistered balance rules for familiarity, perceived socioeconomic
status, and unusualness. The export also lacked consent and attention-check fields.

The repository therefore does not:

- relax thresholds after seeing the results;
- relabel simulated responses as human evidence;
- publish participant-level data without documented sharing permission;
- run the name-signal audit with unapproved stimuli.

Instead, it records the non-approving outcome, defines a replacement-name recovery
procedure, and separates the estimable core audit from the gated extension.

## Core labor-market audit

The core track tests:

1. a 12-month career gap;
2. a traditional versus non-traditional education pathway;
3. whether either treatment differs between frontline and knowledge-work occupations.

The design uses:

- **8 occupations**: 4 frontline or operational and 4 knowledge-work;
- **4 base profiles per occupation**;
- **32 matched base profiles**;
- **2 career-gap conditions**;
- **2 education-pathway conditions**;
- **128 unique matched resumes**;
- **5 repeated trials per resume**;
- **640 planned evaluations**.

A single control name is held fixed within each matched set. Names alternate across
profile slots but no name coefficient is estimated. The full locked plan is in
[`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md).

### Reproduce the core placebo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make core-reproduce
```

### Run the core live audit

```bash
pip install -e ".[api]"
export ANTHROPIC_API_KEY="..."
export ANTHROPIC_MODEL="exact-model-id"
make core-live
```

The live runner records the exact model ID, API version, date, temperature, prompt
version, prompts, trial number, latency, raw response, parser status, and error type.
Evaluation order is randomized, failures and refusals are retained, and selective
reruns are prohibited.

## Pipeline validation

The deterministic mock-provider benchmark validates matched-resume generation,
randomized execution, response parsing, failure retention, estimation, and coefficient
recovery.

The original public placebo report contains:

- **1,280 of 1,280 completed evaluations**;
- **0 parser failures**;
- **128 matched resumes**;
- exact recovery of every nonzero planted fit-score effect to three decimal places.

These are engineering and estimator-validation results. They are not findings about
Claude, employers, or actual applicants.

See [`results/placebo/placebo_validation_report.md`](results/placebo/placebo_validation_report.md).

## Name-signal extension

Names are treated as **perceived name signals**, not actual demographic identities.

Source screening uses:

- complete published 2020 Census first-name tables by race and Hispanic origin;
- 2020 Census first-name tables by sex;
- complete published Census surname tables;
- SSA national first-name frequencies.

Census values are aggregate statistics and may include disclosure-protection
adjustments. They do not identify a person or establish anyone's identity.

### Locked approval rules

A final name stimulus requires:

- at least 100 valid responses;
- at least 70% intended-group agreement;
- at least 70% intended-gender agreement;
- median confidence of at least 4/5;
- between-group range no greater than 0.75 for familiarity;
- between-group range no greater than 0.75 for perceived socioeconomic status;
- between-group range no greater than 0.75 for unusualness.

Every name must have `approved_for_live_audit = true` before the name-signal extension
can run.

### Submitted pretest outcome

The submitted workbook contained **150 respondent IDs** and **1,200 complete ratings**.
Every respondent rated all eight names, with no duplicate respondent-name pairs and no
missing rating fields.

Descriptively:

- intended-group agreement ranged from **88.0% to 97.3%**;
- perceived-male agreement ranged from **94.0% to 98.7%**;
- median confidence was at least **4/5** for every name.

The study was not approved because:

1. consent and attention-check eligibility could not be verified from the export;
2. the balance ranges exceeded 0.75:
   - familiarity: **0.947**;
   - perceived socioeconomic status: **1.130**;
   - unusualness: **1.713**.

Aggregate results are stored in:

- [`results/name_validation/submitted_survey_name_summary.csv`](results/name_validation/submitted_survey_name_summary.csv)
- [`results/name_validation/submitted_survey_balance_tests.csv`](results/name_validation/submitted_survey_balance_tests.csv)
- [`results/name_validation/submitted_survey_validation_report.md`](results/name_validation/submitted_survey_validation_report.md)
- [`data/name_validation/submitted_survey_manifest.csv`](data/name_validation/submitted_survey_manifest.csv)

Raw participant-level rows are not committed because public-sharing permission is not
documented.

### Replacement-name procedure

The recovery plan is documented in
[`docs/name_pretest_recovery_plan.md`](docs/name_pretest_recovery_plan.md).

After an expanded pilot, select a balanced panel with:

```bash
compas-select-balanced-names \
  --input results/name_validation/replacement_candidate_summary.csv
```

The selector exhaustively searches feasible two-name panels, minimizes the largest
balance range, and refuses approval when the best panel still exceeds a locked limit.

## Analysis

Primary outcomes:

1. Fit score
2. Interview recommendation
3. Confidence

The analysis uses matched-set, occupation, and temperature fixed effects; standard
errors clustered by resume; Benjamini-Hochberg correction; linear models; a logistic
recommendation robustness model when estimable; failure sensitivity; treatment means;
and 95% confidence intervals.

## Public data

The occupation sample is grounded in O*NET and BLS fields stored in
[`data/occupations/occupation_registry.csv`](data/occupations/occupation_registry.csv).

Public sources can be downloaded and rebuilt with:

```bash
python scripts/download_public_data.py
python scripts/build_name_registry.py
python scripts/build_occupation_registry.py
```

## Research interpretation

The study is designed to inform questions about labor-market access, workforce
re-entry, credential alternatives, occupational mobility, and algorithmic gatekeeping.
Findings concern one model, prompt, run period, and synthetic occupational sample.
They must not be generalized into employer intent, unlawful discrimination, individual
identity, or economy-wide effects.

See:

- [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md)
- [`docs/preregistration.md`](docs/preregistration.md)
- [`docs/deviations_from_preregistration.md`](docs/deviations_from_preregistration.md)
- [`docs/limitations.md`](docs/limitations.md)
- [`docs/ethics_statement.md`](docs/ethics_statement.md)
- [`docs/model_card.md`](docs/model_card.md)

## License

MIT. See [`LICENSE`](LICENSE).
