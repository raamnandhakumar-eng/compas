# LLM Hiring Bias Audit: fellowship research brief

## Project in one sentence

I will run a preregistered matched-resume audit testing whether a language model penalizes a 12-month career gap or a non-traditional education pathway, and whether those effects differ between frontline and knowledge-work occupations.

## Why this project matters

Language models may increasingly influence candidate screening and ranking. Small changes in model scores or interview recommendations can affect who advances to human review.

Career interruptions and non-traditional education pathways are economically important because they affect caregivers, returning workers, veterans, immigrants, career changers, and people who cannot follow a continuous full-time education path. The same signal may also be interpreted differently across occupations, which makes the frontline-versus-knowledge-work interaction an empirical question rather than a rhetorical assumption.

## The design

The study uses 32 synthetic base candidate profiles across eight occupations. Each profile is expanded into a 2 × 2 design:

- no career gap versus a 12-month career gap;
- traditional versus non-traditional education.

Qualifications remain fixed within each matched set. The design produces **128 unique resumes** and **640 planned evaluations** at one locked temperature using one exact model ID.

Primary outcomes are fit score, interview recommendation, and model confidence. The analysis includes matched-set and occupation fixed effects, standard errors clustered by matched resume, and Benjamini-Hochberg correction across preregistered treatment terms.

## What is already demonstrated

- The resume generator, randomized runner, parser, analysis pipeline, tests, and CI workflow are implemented.
- The deterministic core placebo completed **640 of 640 evaluations**, with **zero failures** across **128 matched resumes**, **32 base profiles**, and **eight occupations**.
- The estimator exactly recovered the planted career-gap effect of **-0.45** and non-traditional-education effect of **-0.15**.
- A constant mock recommendation outcome was correctly reported as **not estimable** rather than interpreted from numerical noise.
- The first name-perception pretest is preserved as a failed validation result rather than used to justify a demographic claim.

See [`results/core/placebo_validation_report.md`](results/core/placebo_validation_report.md).

## Four-month deliverable

The fellowship project is limited to:

1. submit an external OSF or AsPredicted preregistration before the first live request;
2. run the complete 640-evaluation core audit with one exact model ID;
3. estimate the preregistered models and robustness checks;
4. publish raw outputs, a run manifest, tables, figures, and reproducible code;
5. write a concise empirical paper and policy-oriented summary.

The live runner will refuse to start unless a valid external registration URL is supplied.

## What I am not promising in four months

The following are future research rather than fellowship deliverables:

- a new name-perception survey;
- the 2,560-evaluation perceived-name-signal extension;
- a human hiring-manager benchmark;
- multi-model replication.

Narrowing the scope protects the quality of the core study and leaves enough time for careful interpretation, writing, and public release.

## Research judgment

The failed name pretest is not hidden or redefined. The names were recognized strongly in the intended direction, but they were not balanced on familiarity, perceived socioeconomic status, and unusualness, and the export lacked consent and attention-check fields. The project therefore does not relax the thresholds, relabel simulated data as human evidence, or run the blocked extension anyway.

That decision is part of the contribution: the repository distinguishes pipeline validation, stimulus validation, and live-model evidence rather than collapsing them into one claim.

## Expected contribution

The project will provide controlled evidence on workforce re-entry, credential alternatives, occupational mobility, and AI-mediated gatekeeping. It will also provide a reusable empirical framework for auditing LLM screening behavior while preserving raw outputs, preregistering analysis, retaining failures, and reporting null or non-estimable results honestly.

## Skills evidenced by the repository

- Python data engineering and reproducible research pipelines
- matched experimental audit design
- econometric modeling and clustered inference
- labor-market and occupational data integration
- model evaluation, parsing, and failure analysis
- external preregistration and research transparency
- policy-oriented interpretation of empirical results
