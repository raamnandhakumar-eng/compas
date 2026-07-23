# Core labor-market audit preregistration

**Locked on:** July 23, 2026  
**Status:** No live model outputs have been observed.

## Purpose

This confirmatory track tests whether a resume-screening language model changes its
judgments when a candidate has a 12-month career gap or a non-traditional education
pathway, and whether those effects differ between frontline and knowledge-work
occupations.

The perceived-name-signal extension is not part of this track. The first name
perception pretest failed the locked balance rules, so name effects remain gated
pending a new pretest. Splitting the core track from the name extension prevents an
unrelated stimulus-validation failure from blocking the labor-market questions that
can already be studied cleanly.

## Confirmatory hypotheses

All tests are two-sided. Null and unexpected results will be reported.

1. A 12-month career gap changes fit score or interview-recommendation probability.
2. A non-traditional education pathway changes fit score or recommendation probability.
3. Either treatment effect differs between frontline and knowledge-work occupations.

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

Each base profile uses one fixed control name across its four treatment variants.
Names alternate across profile slots but do not vary within a matched set. No
coefficient or interpretation concerning names is produced.

## Outcomes

Primary outcomes:

1. Fit score from 1 to 10
2. Binary interview recommendation
3. Confidence score from 0 to 1

Secondary outcomes include refusals, parser failures, response length, repeated-call
variance, and explanation themes.

## Execution

All 640 observations will be randomized before the first API request. The exact model
ID, API version, run date, prompt version, prompts, temperature, trial number, latency,
raw response, parser status, and error type will be retained.

Every observation will be attempted once. Failures and refusals remain in the raw
data. There will be no early stopping, selective reruns, prompt changes, model changes,
or treatment-specific execution blocks.

## Primary specification

Fit score, recommendation, and confidence are estimated using linear models with:

- non-traditional pathway indicator;
- 12-month career-gap indicator;
- non-traditional pathway × frontline interaction;
- career gap × frontline interaction;
- occupation fixed effects;
- matched-set fixed effects;
- temperature fixed effects;
- standard errors clustered by resume.

A logistic recommendation model is reported when the outcome has sufficient
variation. Benjamini-Hochberg correction is applied across the preregistered treatment
and interaction coefficients.

## Robustness and sensitivity

- failed recommendations coded as not recommended;
- logistic recommendation model when estimable;
- occupation-specific descriptive estimates;
- treatment means by occupation tier;
- failure and refusal rates by treatment;
- repeated-call variance.

## Interpretation

The audit concerns one exact model, prompt, run period, and synthetic occupational
sample. It does not establish employer behavior, unlawful discrimination, model
intent, or economy-wide effects. It estimates whether controlled resume signals alter
screening outputs in this specific experimental setting.
