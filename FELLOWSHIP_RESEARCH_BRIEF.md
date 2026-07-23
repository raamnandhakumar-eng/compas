# Fellowship research brief

## Project in one sentence

COMPAS is a reproducible labor-market audit that tests whether language-model resume
screening changes when candidate qualifications stay fixed but career continuity,
education pathway, occupational context, or validated perceived-name signals change.

## Why this project matters

Language models may increasingly influence screening, ranking, and candidate
evaluation. Small differences in model judgments can affect labor-market access,
especially for workers returning after career interruptions, candidates with
non-traditional education, and people applying across frontline and knowledge-work
occupations.

COMPAS turns that policy concern into a controlled empirical design:

- matched synthetic resumes hold qualifications constant;
- treatment allocation is complete and reproducible;
- evaluation order is randomized;
- raw responses and failures are retained;
- outcomes are analyzed with clustered inference and multiple-testing correction;
- public Census, SSA, O*NET, and BLS sources ground stimulus and occupation design;
- null, negative, and failed validation results are reported rather than hidden.

## What is already demonstrated

- A deterministic placebo benchmark validates resume generation, randomized execution,
  parsing, failure retention, and coefficient recovery.
- The new core placebo completed **640 of 640 evaluations**, with **zero failures**
  across **128 matched resumes**, **32 base profiles**, and **eight occupations**.
- The core estimator recovered the planted career-gap effect of **-0.45** and the
  non-traditional-education effect of **-0.15** with effectively zero recovery error.
- A constant mock recommendation outcome is explicitly reported as **not estimable**
  rather than interpreted from numerical noise.
- The first 150-person name-perception pretest is preserved as a non-approving result.
  It showed strong signal recognition but failed preregistered balance and
  administration requirements.
- The core career-gap and education-pathway audit is separated from the gated
  name-signal extension, allowing a clean live study without weakening the original
  name-validation standard.
- An exhaustive Python selector is included for choosing a better-balanced replacement
  name panel from a future pilot.

See the committed validation evidence in
[`results/core_placebo/core_placebo_validation_report.md`](results/core_placebo/core_placebo_validation_report.md).

## Empirical contribution

The project studies whether screening penalties depend on occupational context. A
career gap or non-traditional education pathway may be interpreted differently in
frontline and knowledge-work hiring. This interaction is directly relevant to labor
mobility, workforce re-entry, credential alternatives, and unequal access to AI-mediated
hiring systems.

## Research judgment demonstrated

The failed name pretest is a substantive result about measurement design. The project
does not relabel synthetic data as human evidence, relax thresholds after seeing the
data, publish participant-level records without documented permission, or run the
blocked name audit anyway. Instead, it records the failure, separates estimable
questions, and preregisters a recovery procedure.

## Public-output path

1. Run the 640-evaluation core audit using one exact model ID.
2. Publish raw outputs, run manifest, coefficients, confidence intervals, robustness
   checks, and a concise paper-style report.
3. Conduct the replacement-name selection pilot and final perception pretest.
4. Run the name-signal extension only after all locked validation rules pass.
5. Add a blinded human benchmark to compare model and hiring-professional judgments.

## Skills evidenced by the repository

- Python data engineering and reproducible research pipelines
- experimental design and matched audits
- econometric modeling and clustered inference
- labor-market and occupational data integration
- model evaluation, parsing, and failure analysis
- preregistration, research ethics, and transparent reporting
- translation of empirical results into policy-relevant questions
