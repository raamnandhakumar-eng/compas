# COMPAS

**Candidate Outcome Measurement and Prompt Audit Suite**

COMPAS is a reproducible audit of whether a resume-screening language model changes its judgments when controlled candidate signals change and qualifications remain fixed.

> This project is unrelated to the criminal-risk assessment system also called COMPAS. A distinct repository name is under consideration to reduce confusion.

## Main research question

**Holding qualifications fixed, do perceived name signals, a 12-month career gap, or a non-traditional education pathway change Claude's fit score, interview recommendation, or confidence—and do those effects differ between frontline and knowledge-work occupations?**

## Current status

> **Pipeline validation:** Complete  
> **Name-source screening:** In progress  
> **Perception pretest:** Not completed  
> **Live Claude audit:** Not run  
> **Human benchmark:** Not run

The repository currently contains completed placebo results and the locked infrastructure for the larger confirmatory study. It does not contain live Claude findings.

## Pipeline validation

The completed placebo run tested whether the software could generate matched resumes, randomize evaluations, preserve raw responses, reject malformed outputs, estimate the preregistered models, and recover known effects.

The run completed **1,280 of 1,280 evaluations**, with **0 parser failures** across **128 matched resumes**. Every nonzero planted fit-score effect was recovered to three decimal places.

These are engineering and estimator-validation results from a deterministic mock provider. They are not findings about Claude, employers, or real applicants.

Detailed placebo tables are kept in [`results/placebo/placebo_validation_report.md`](results/placebo/placebo_validation_report.md).

## Name validation

Names are treated as **perceived name signals**, not actual demographic identities.

The source registry contains two names for each of four experimental groups. It records first-name and surname counts, group shares, first-name sex shares, SSA frequency, source year, source file, and screening status.

Source screening uses:

- **complete published tables for names occurring approximately 100 or more times** in the 2020 Census;
- Census first-name tables by race and Hispanic origin;
- Census first-name tables by sex;
- Census surname tables by race and Hispanic origin;
- SSA first-name frequencies by birth year.

Census counts and percentages are aggregate statistics and include disclosure-protection adjustments. The research files may contain negative values created by the disclosure-avoidance process. These data do not identify a person or establish anyone's race, ethnicity, gender, nationality, or socioeconomic status.

The public-source registry is populated in [`data/name_validation/name_candidates.csv`](data/name_validation/name_candidates.csv), but no name is approved for the live audit until the separate human perception pretest is complete.

### Locked perception-pretest rules

Approximately 100 to 200 respondents will rate:

- perceived race or ethnicity;
- perceived gender;
- familiarity;
- perceived socioeconomic status;
- confidence;
- whether the name seems unusual.

A name requires at least 100 valid responses, at least 70% intended-group agreement, at least 70% intended-gender agreement, median confidence of at least 4/5, and no major between-group imbalance in socioeconomic status, familiarity, or unusualness.

The empty response template and current pending outputs are stored in:

- [`data/name_validation/perception_responses.csv`](data/name_validation/perception_responses.csv)
- [`results/name_validation/name_summary.csv`](results/name_validation/name_summary.csv)
- [`results/name_validation/name_balance_tests.csv`](results/name_validation/name_balance_tests.csv)

The live runner stops automatically unless every configured perceived name signal passes.

### Simulated pretest for pipeline validation

A deterministic 120-person panel simulation exercises the complete pretest workflow without being treated as participant evidence. Four simulated panel IDs fail the attention check, leaving 116 valid ratings per name. All eight names pass the preregistered agreement, confidence, familiarity, socioeconomic-status, and unusualness thresholds in this simulation.

The simulation never changes the real pretest status and forces `approved_for_live_audit = false`. Generate it with:

```bash
make simulate-name-pretest
```

The simulation method is documented in [`data/simulated/name_validation/README.md`](data/simulated/name_validation/README.md). Its summary, balance checks, and manifest are stored in [`results/simulated/name_validation/`](results/simulated/name_validation/). CI publishes the full 960-row response CSV as the `simulated-name-perception-study` artifact.

## Planned live audit

The confirmatory design uses:

- **8 occupations**: 4 frontline or operational and 4 knowledge-work;
- **4 base profiles per occupation**;
- **4 perceived-name-signal groups**;
- **2 career-gap conditions**;
- **2 education-pathway conditions**;
- **5 repeated trials per resume**;
- **512 unique matched resumes**;
- **2,560 planned evaluations**.

The occupation sample varies in wage, employment size, education requirements, industry setting, and occupational group. Public source fields are stored in [`data/occupations/occupation_registry.csv`](data/occupations/occupation_registry.csv).

Within each matched set, experience, skills, achievements, employer history, education level, job title, target role, formatting, and resume length remain fixed. Only the assigned treatment changes.

### Primary outcomes

1. Fit score
2. Interview recommendation
3. Confidence score

Response length, refusals, parser failures, repeated-call variance, and explanation themes are secondary outcomes.

### Analysis plan

The locked analysis includes matched-set, occupation, and temperature fixed effects; standard errors clustered by matched resume; Benjamini-Hochberg correction; linear models for fit and confidence; a linear probability model and logistic regression for recommendations; randomization inference; leave-one-occupation-out analysis; failed-response sensitivity checks; and 95% confidence intervals.

The complete plan is in [`docs/preregistration.md`](docs/preregistration.md), and the preregistered power assumptions are in [`docs/power_analysis.md`](docs/power_analysis.md).

## Live results

**No live Claude results are reported.**

Before a live run, the repository requires:

1. completion of the perception pretest;
2. approval of every perceived name signal;
3. an exact model ID supplied through `ANTHROPIC_MODEL`;
4. the locked prompt, sample, temperature, and stopping rule.

The runner preserves the exact model ID, API version, date, temperature, prompt version, full prompts, trial number, latency, raw response, parser status, and error type. Evaluation order is randomized, all failures and refusals are retained, and selective reruns are prohibited.

## Human benchmark

After the main live audit, the planned benchmark will recruit 3 to 5 hiring professionals or experienced managers to review approximately 100 blinded matched resumes. The comparison will measure human fit scores, recommendations, confidence, human-Claude agreement, and treatment effects in humans versus Claude.

## Reproduce the repository

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
make reproduce
```

Public source files can be downloaded and rebuilt with:

```bash
python scripts/download_public_data.py
python scripts/build_name_registry.py
python scripts/build_occupation_registry.py
```

The live run is deliberately separate:

```bash
export ANTHROPIC_API_KEY="..."
export ANTHROPIC_MODEL="exact-model-id"
make live
```

## Research interpretation

The study is designed to inform questions about labor-market access, occupational mobility, career interruptions, non-traditional education, frontline versus knowledge-work hiring, and algorithmic gatekeeping. Findings from eight occupations must not be generalized into economy-wide effects.

See [`docs/limitations.md`](docs/limitations.md), [`docs/ethics_statement.md`](docs/ethics_statement.md), [`docs/model_card.md`](docs/model_card.md), and [`docs/deviations_from_preregistration.md`](docs/deviations_from_preregistration.md).

## License

MIT. See [`LICENSE`](LICENSE).
