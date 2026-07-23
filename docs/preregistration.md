# Name-signal extension preregistration

**Status:** Blocked pending a successful replacement perception pretest.  
**Live model outputs observed:** None.

This plan governs the confirmatory perceived-name-signal extension. The independently
executable career-gap and education-pathway study is governed by
[`core_audit_preregistration.md`](core_audit_preregistration.md).

## Primary research question

Holding qualifications fixed, do validated perceived-name signals, a 12-month career
gap, or a non-traditional education pathway change a screening model's fit score,
interview recommendation, or confidence, and do those effects differ between frontline
and knowledge-work occupations?

## Confirmatory hypotheses

All tests are two-sided and all null results will be reported.

1. At least one validated perceived-name-signal group differs from the reference group
   in fit score or recommendation probability.
2. A 12-month career gap changes fit score or recommendation probability.
3. A non-traditional education pathway changes fit score or recommendation probability.
4. At least one treatment effect differs between frontline and knowledge-work
   occupations.

## Name-validation lock

Names are experimental **perceived name signals**, not actual demographic identities.

Before a live name-signal run:

1. source-screen first and last names with complete published Census tables;
2. record SSA first-name frequency for the locked source period;
3. recruit 100 to 200 respondents for a separate final perception pretest;
4. record consent, attention checks, randomization, recruitment, dates, and exclusions;
5. measure perceived race or ethnicity, perceived gender, familiarity, perceived
   socioeconomic status, confidence, and unusualness;
6. apply the locked rules:
   - minimum 100 valid responses per name;
   - at least 70% intended-group agreement;
   - at least 70% intended-gender agreement;
   - median confidence of at least 4/5;
   - no between-group range above 0.75 for socioeconomic status, familiarity, or
     unusualness.

Every configured name must have `approved_for_live_audit = true`.

The first submitted pretest is retained as a non-approving result. Replacement
selection must follow
[`name_pretest_recovery_plan.md`](name_pretest_recovery_plan.md).

## Confirmatory sample

- 8 occupations: 4 frontline or operational and 4 knowledge-work
- 4 base profiles per occupation
- 32 matched base profiles
- 4 approved perceived-name-signal groups
- 2 career-gap conditions
- 2 education-pathway conditions
- 512 unique matched resumes
- 5 trials per resume
- 1 locked temperature
- **2,560 planned evaluations**

Within a matched set, experience, skills, achievements, employer history, education
level, job title, target role, formatting, and resume length are held fixed. Only the
assigned treatment changes.

## Outcomes

Primary outcomes:

1. Fit score from 1 to 10
2. Binary interview recommendation
3. Confidence score from 0 to 1

Secondary outcomes:

- response length;
- refusal rate;
- parser-failure rate;
- within-resume variance;
- predefined explanation themes.

Generated explanations are secondary and do not replace the structured outcomes.

## Execution and stopping rule

Evaluation order will be randomized across all treatments before the first API request.
One treatment group will not be run in a separate time block. The exact model ID, API
version, prompt version, prompts, temperature, trial number, latency, raw response,
parser status, and error type will be retained.

All 2,560 observations will be attempted once. Failures and refusals will be preserved.
The experiment will not stop early and observations will not be selectively rerun.
Prompts and model ID will not change during the confirmatory run.

## Exclusion and failure rules

A response is excluded from structured-outcome regression only when:

- the provider request fails;
- no JSON object can be parsed;
- a required field is missing;
- fit score is outside 1 to 10;
- confidence is outside 0 to 1;
- recommendation is not Boolean.

Every failed response remains in raw data. Failure and refusal rates are reported by
treatment and occupation. A sensitivity analysis codes failed recommendations as not
recommended.

## Primary model

Fit score and confidence use linear regression. Recommendation uses a linear
probability model for primary marginal-effect presentation and logistic regression as a
robustness check.

The specification includes:

- perceived-name-signal indicators, with the locked reference group;
- perceived-name-signal × frontline interactions;
- career-gap indicator and frontline interaction;
- non-traditional pathway indicator and frontline interaction;
- matched-set fixed effects;
- occupation fixed effects;
- temperature fixed effects;
- standard errors clustered by resume.

Benjamini-Hochberg correction controls false discovery across preregistered treatment
and interaction coefficients. Effects are reported with 95% confidence intervals.

## Robustness

- logistic recommendation model;
- randomization inference within matched sets;
- leave-one-occupation-out estimates;
- valid-only and failed-as-not-recommended specifications;
- repeated-call variance;
- treatment effects by occupation;
- parser-failure and refusal comparisons.

## Interpretation

Results concern one exact model, prompt, run period, and synthetic occupational sample.
They do not establish intent, unlawful discrimination, employer behavior, actual
identity, or economy-wide labor-market effects.

## Current status

The pipeline placebo is complete. The first perception pretest was reviewed on
July 23, 2026 and was not approved. The replacement-name procedure and new final
pretest have not been completed. The name-signal live extension and human benchmark
have not been run.
