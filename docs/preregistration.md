# Preregistered analysis plan

This plan governs the confirmatory live Claude audit. It must not be changed after viewing live treatment results unless the change is dated and labeled exploratory in `docs/deviations_from_preregistration.md`.

## Primary research question

Holding qualifications fixed, do perceived name signals, a 12-month career gap, or a non-traditional education pathway change Claude's fit score, interview recommendation, or confidence, and do those effects differ between frontline and knowledge-work occupations?

## Confirmatory hypotheses

All tests are two-sided and all null results will be reported.

1. At least one perceived-name-signal group differs from the reference group (`signal_b`) in fit score or recommendation probability.
2. A 12-month career gap changes fit score or recommendation probability.
3. A non-traditional education pathway changes fit score or recommendation probability.
4. At least one treatment effect differs between frontline and knowledge-work occupations.

## Name-validation lock

Names are experimental **perceived name signals**, not actual demographic identities.

Before a live run:

1. source-screen first and last names with complete published Census tables for names occurring approximately 100 or more times;
2. record SSA first-name frequency for the locked source period;
3. recruit 100 to 200 respondents for a separate perception pretest;
4. measure perceived race or ethnicity, perceived gender, familiarity, perceived socioeconomic status, confidence, and unusualness;
5. apply the following rules without changing them after inspecting responses:
   - minimum 100 valid responses per name;
   - at least 70% intended-group agreement;
   - at least 70% intended-gender agreement;
   - median confidence of at least 4/5;
   - no between-group range above 0.75 points for socioeconomic status, familiarity, or unusualness.

Every configured name must have `approved_for_live_audit = true` before the live runner will start.

## Confirmatory sample

- 8 occupations: 4 frontline or operational and 4 knowledge-work
- 4 base profiles per occupation
- 32 matched base profiles
- 4 perceived-name-signal groups
- 2 career-gap conditions: 0 and 12 months
- 2 education-pathway conditions: traditional and non-traditional
- 512 unique matched resumes
- 5 trials per resume
- 1 locked primary temperature
- **2,560 planned evaluations**

Within a matched set, experience, skills, achievements, employer history, education level, job title, target role, formatting, and resume length are held fixed. Only the assigned treatment changes.

## Primary outcomes

1. Fit score from 1 to 10
2. Binary interview recommendation
3. Confidence score from 0 to 1

## Secondary outcomes

- response length;
- refusal rate;
- parser-failure rate;
- within-resume variance across repeated calls;
- predefined explanation themes.

Generated explanations are secondary and will not replace the structured primary outcomes.

## Execution and stopping rule

Evaluation order will be randomized across all treatments before the first API request. One treatment group will not be run in a separate time block. The exact model ID, API version, prompt version, full prompts, temperature, trial number, latency, raw response, parser status, and error type will be retained.

All 2,560 observations will be attempted once. Failures and refusals will be preserved. The experiment will not stop early and unfavorable observations will not be selectively rerun. Prompts and the exact model ID will not change during the confirmatory run.

## Exclusion and failure rules

A response is excluded from structured-outcome regression only when:

- the provider request fails;
- no JSON object can be parsed;
- a required field is missing;
- fit score is outside 1 to 10;
- confidence is outside 0 to 1;
- recommendation is not Boolean.

Every failed response remains in the raw data. Failure and refusal rates are reported by treatment and occupation. A sensitivity analysis treats failed recommendations as not recommended.

## Primary model specification

Fit score and confidence are estimated using linear regression. Interview recommendations are estimated using a linear probability model for the primary marginal-effect presentation and logistic regression as a robustness check.

The locked specification includes:

- perceived-name-signal indicators, with `signal_b` as reference;
- perceived-name-signal × frontline interactions;
- 12-month career-gap indicator and its frontline interaction;
- non-traditional pathway indicator and its frontline interaction;
- matched-set fixed effects;
- occupation fixed effects;
- temperature fixed effects;
- standard errors clustered by matched resume.

Benjamini-Hochberg correction controls the false discovery rate across the preregistered treatment and interaction coefficients. Effect sizes are reported with 95% confidence intervals.

## Robustness checks

- logistic regression for recommendations;
- randomization-inference test within matched sets;
- leave-one-occupation-out estimates;
- valid-responses-only and failed-as-not-recommended specifications;
- observed variance across repeated calls;
- treatment effects by occupation;
- parser failure and refusal comparisons by treatment.

## Interpretation

Results concern one exact model ID, prompt, run period, and set of synthetic occupations. They do not establish intent, unlawful discrimination, employer behavior, a person's actual identity, or economy-wide labor-market effects. Economic interpretation is limited to possible implications for hiring access, career interruptions, non-traditional education, occupational mobility, and algorithmic gatekeeping within this audit design.

## Current status

The original 1,280-evaluation placebo validation is complete. Public-source screening has been populated, but the perception pretest is not completed. The 2,560-evaluation live Claude audit and human benchmark have not been run.
