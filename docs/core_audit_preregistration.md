# Core labor-market audit preregistration

**Repository design locked on:** July 23, 2026  
**Externally registered:** Pending OSF or AsPredicted submission  
**Status:** No live model outputs have been observed.

## Purpose

This confirmatory study tests whether a resume-screening language model changes its judgments when a candidate has a 12-month career gap or a non-traditional education pathway, and whether those effects differ between frontline and knowledge-work occupations.

The perceived-name-signal extension is not part of this study. Its first human pretest failed the locked balance rules, so name effects remain gated pending a new study. Separating the core audit prevents an unrelated stimulus-validation failure from blocking the labor-market questions that can already be studied cleanly.

## Four-month scope

The four-month research deliverable is limited to:

1. external preregistration before the first live request;
2. the 640-evaluation core audit;
3. the analyses and diagnostics specified below;
4. a public reproducibility package and concise research paper.

A replacement name survey, the live name-signal extension, a human hiring-manager benchmark, and multi-model replication are future work and are not deliverables under this registration.

## External preregistration requirement

Before the first live API request, this design will be submitted to OSF or AsPredicted using:

- `docs/osf_preregistration.md`, or
- `docs/aspredicted_preregistration.md`.

The permanent registration URL must be supplied through `EXTERNAL_PREREGISTRATION_URL`. The live runner refuses execution when the URL is missing, is not HTTPS, or is not hosted by OSF or AsPredicted. The accepted URL is retained in every live output row and in the run manifest.

## Confirmatory hypotheses

All tests are two-sided. Null and unexpected results will be reported.

1. A 12-month career gap changes fit score or interview-recommendation probability.
2. A non-traditional education pathway changes fit score or recommendation probability.
3. The career-gap effect differs between frontline and knowledge-work occupations.
4. The education-pathway effect differs between frontline and knowledge-work occupations.

## Sample

- 8 occupations: 4 frontline or operational and 4 knowledge-work
- 4 base profiles per occupation
- 32 matched base profiles
- 2 career-gap conditions
- 2 education-pathway conditions
- 128 unique matched resumes
- 5 repeated trials per resume
- 1 locked temperature
- **640 planned evaluations**

Each base profile uses one fixed control name across its four treatment variants. Names alternate across profile slots but do not vary within a matched set. No coefficient or interpretation concerning names is produced.

## Outcomes

Primary outcomes:

1. Fit score from 1 to 10
2. Binary interview recommendation
3. Confidence score from 0 to 1

Secondary outcomes include refusals, parser failures, provider failures, response length, latency, repeated-call variance, and predefined explanation themes.

## Execution

All 640 observations will be randomized before the first API request. The exact model ID, API version, external preregistration URL, run date, prompt version, prompts, temperature, trial number, execution order, latency, raw response, parser status, and error type will be retained.

Every observation will be attempted once. Failures and refusals remain in the raw data. There will be no early stopping, selective reruns, prompt changes, model changes, sample-size changes based on observed results, or treatment-specific execution blocks.

## Exclusion and failure rules

A response is excluded from structured-outcome regression only when:

- the provider request fails;
- no JSON object can be parsed;
- a required field is missing;
- fit score is outside 1 to 10;
- confidence is outside 0 to 1;
- recommendation is not Boolean.

Every excluded response remains in the raw dataset and is included in run-quality reporting.

## Primary specification

Fit score, recommendation, and confidence are estimated using linear models with:

- non-traditional pathway indicator;
- 12-month career-gap indicator;
- non-traditional pathway × frontline interaction;
- career gap × frontline interaction;
- occupation fixed effects;
- matched-set fixed effects;
- temperature fixed effects;
- standard errors clustered by matched resume.

A logistic recommendation model is reported when the outcome has sufficient variation. Benjamini-Hochberg correction is applied across the four preregistered treatment and interaction terms for the primary outcomes.

## Robustness and sensitivity

- failed recommendations coded as not recommended;
- logistic recommendation model when estimable;
- occupation-specific descriptive estimates;
- treatment means by occupation tier;
- failure and refusal rates by treatment;
- repeated-call variance.

Occupation-specific estimates are descriptive and will not be presented as a large family of separately powered confirmatory tests.

## Planned output

The public release will include:

- the external registration record;
- synthetic resume permutations;
- the run manifest;
- raw and parsed model outputs, subject to provider terms and credential removal;
- coefficient tables and confidence intervals;
- run-quality, refusal, and failure summaries;
- publication-quality figures;
- a concise research paper;
- the code and environment specification.

## Interpretation

The audit concerns one exact model, prompt, run period, and purposive synthetic occupational sample. It does not establish employer behavior, unlawful discrimination, model intent, effects on actual applicants, or economy-wide labor-market effects. It estimates whether controlled resume signals alter screening outputs in this specific experimental setting.
