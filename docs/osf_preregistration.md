# OSF preregistration: LLM Hiring Bias Audit core study

> **Submission status:** Prepared but not yet externally registered. Submit this document before the first live model request. After submission, record the permanent OSF URL in `EXTERNAL_PREREGISTRATION_URL`.

## Title

Career Gaps, Education Pathways, and Occupational Context in LLM Resume Screening: A Matched Synthetic-Resume Audit

## Contributors

Sriramkrishnan Nandhakumar

## Research question

Holding candidate qualifications fixed, does a resume-screening language model change its fit score, interview recommendation, or confidence when the resume shows either a 12-month career gap or a non-traditional education pathway? Do those effects differ between frontline and knowledge-work occupations?

## Background and rationale

Language models may be used in tasks that resemble candidate screening, ranking, and evaluation. Career interruptions and non-traditional education pathways are common labor-market signals and may affect workforce re-entry and access to employment. Their interpretation may also depend on occupational context.

The design uses matched synthetic resumes so that experience, skills, achievements, employer history, education level, target role, formatting, and resume length remain fixed within each matched set. Only the career-gap and education-pathway treatments change.

A separate perceived-name-signal extension is excluded from this registration. Its first human pretest did not pass the locked balance and administration requirements. No name effect will be estimated in the registered core study.

## Study status at registration

- The resume-generation, execution, parsing, and analysis code has been written.
- Deterministic mock-provider placebo runs have been completed for software and estimator validation.
- The mock outputs are not live-model evidence and will not be included in the confirmatory estimates.
- No live Anthropic model response for this study has been requested, observed, or analyzed.

## Hypotheses

All confirmatory tests are two-sided.

1. A 12-month career gap changes the model's fit score or interview-recommendation probability.
2. A non-traditional education pathway changes the model's fit score or interview-recommendation probability.
3. The career-gap effect differs between frontline and knowledge-work occupations.
4. The education-pathway effect differs between frontline and knowledge-work occupations.

Null and unexpected results will be reported.

## Experimental design

### Occupational sample

The study contains eight occupations:

- four frontline or operational occupations;
- four knowledge-work occupations.

The occupations and source fields are fixed in `data/occupations/occupation_registry.csv`. The sample is purposive rather than statistically representative of the entire labor market.

### Base profiles

There are four base profiles per occupation, for 32 matched base profiles in total.

### Treatments

Each base profile is expanded into a 2 × 2 factorial design:

- career gap: 0 months or 12 months;
- education pathway: traditional or non-traditional.

This produces four treatment variants per base profile and 128 unique resumes.

### Names

One control name is held fixed across all four variants within each matched set. Names may alternate across profile slots, but no name coefficient or demographic interpretation will be produced.

### Repeated evaluations

Each of the 128 resumes will be evaluated five times using one exact model ID, one locked prompt version, and one temperature of 0.0.

Total planned evaluations:

128 resumes × 5 trials = **640 evaluations**.

## Randomization

All resume-trial jobs will be constructed before the first API request and assigned a randomized execution order using the locked seed in `config/core_audit.yaml`.

Treatments will not be executed in separate time blocks. The execution order will be retained in the output data.

## Model and prompt lock

Before execution, the researcher will record:

- the exact Anthropic model ID;
- the API/library version;
- the prompt version;
- the system prompt;
- the user-prompt template;
- the temperature;
- the maximum-token setting;
- the run date.

The exact model ID and prompt will not change during the confirmatory run.

## Primary outcomes

1. **Fit score:** numeric score from 1 to 10.
2. **Interview recommendation:** Boolean recommendation converted to 0 or 1.
3. **Confidence:** numeric score from 0 to 1.

## Secondary and diagnostic outcomes

- refusal indicator;
- parser-failure indicator;
- provider/API failure indicator;
- response length;
- latency;
- repeated-call variance;
- predefined explanation-theme counts.

Generated explanations are secondary and will not replace the structured primary outcomes.

## Exclusion and failure rules

A response is excluded from the structured primary-outcome regression only when:

- the provider request fails;
- no JSON object can be parsed;
- a required field is missing;
- fit score falls outside 1–10;
- confidence falls outside 0–1;
- recommendation is not Boolean.

Every failed response remains in the raw data. No response will be selectively rerun because of its outcome, refusal, or parsing status.

## Stopping rule

All 640 randomized observations will be attempted once.

There will be:

- no early stopping based on results;
- no sample-size increase based on observed p-values or effect sizes;
- no selective reruns;
- no change to the model, prompt, temperature, treatment definitions, or primary outcomes during the confirmatory run.

A run interrupted by an external outage will retain all completed observations. Any restart or additional attempt will be documented as a deviation before analysis, and the original failed records will not be deleted.

## Variables and coding

- `nontraditional = 1` for the non-traditional education pathway; otherwise 0.
- `has_gap = 1` for the 12-month career-gap condition; otherwise 0.
- `frontline = 1` for frontline or operational occupations; otherwise 0.
- `nontraditional × frontline` is the education-pathway interaction.
- `has_gap × frontline` is the career-gap interaction.

## Primary statistical models

Fit score and confidence will be estimated using linear regression.

Interview recommendation will be estimated using a linear probability model. A logistic regression will be reported as a robustness check when the outcome contains sufficient variation for estimation.

The locked linear specification is:

`outcome ~ nontraditional + has_gap + nontraditional:frontline + has_gap:frontline + occupation fixed effects + matched-set fixed effects + temperature fixed effects`

Standard errors will be clustered by matched resume (`resume_id`).

## Confirmatory terms

The confirmatory treatment terms are:

- `nontraditional`;
- `has_gap`;
- `nontraditional:frontline`;
- `has_gap:frontline`.

## Multiple testing

Benjamini-Hochberg false-discovery-rate correction will be applied across the preregistered treatment and interaction coefficients for the primary outcomes. Raw p-values, adjusted q-values, point estimates, clustered standard errors, and 95% confidence intervals will be reported.

## Robustness and sensitivity analyses

The following analyses are preregistered:

- logistic recommendation model when estimable;
- failed recommendations coded as not recommended;
- treatment means by frontline/knowledge-work tier;
- refusal and failure rates by treatment;
- repeated-call variance;
- occupation-specific descriptive estimates.

Occupation-specific results are descriptive and will not be presented as a large family of separately powered confirmatory tests.

## Data-quality checks

Before interpretation, the researcher will verify:

- exactly 128 unique resumes were generated;
- exactly four treatment variants exist per matched set;
- qualifications remain identical within each matched set;
- candidate name remains fixed within each matched set;
- all observation IDs are unique;
- the recorded model ID is constant across the run;
- the recorded prompt version and temperature are constant;
- execution order is randomized;
- all failures and refusals remain in the data.

## Planned figures and tables

The public report will include:

- a design-flow figure;
- treatment-effect estimates with 95% confidence intervals;
- treatment means by occupation tier;
- run-quality and failure table;
- repeated-call variance summary;
- occupation-level descriptive results.

Figures and tables not listed here will be labeled exploratory.

## Interpretation

The study estimates whether controlled resume signals change one model's outputs under one prompt, model ID, run period, and synthetic occupational sample.

It does not establish:

- employer behavior;
- unlawful discrimination;
- model intent;
- effects on actual applicants;
- representativeness across the entire labor market;
- demographic identity from a person's name.

## Data and code availability

The researcher plans to publish:

- synthetic resume permutations;
- raw model responses, subject to provider terms and removal of credentials;
- the run manifest;
- parsed outcomes and failure indicators;
- analysis tables and figures;
- code and environment specifications;
- a dated deviations log.

API credentials will never be published.

## Deviations

Any change after this registration will be dated and documented in `docs/deviations_from_preregistration.md`. Changes will be labeled confirmatory or exploratory before the affected analysis is reported.

## External registration record

After OSF submission, record:

- OSF registration URL: `PENDING`
- DOI, if public: `PENDING`
- submission date: `PENDING`
- visibility: public or embargoed

The live runner requires the permanent URL through:

```bash
export EXTERNAL_PREREGISTRATION_URL="https://osf.io/xxxxx"
```
