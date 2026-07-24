# Fellowship proposal: LLM Hiring Bias Audit

## 1. Research question

I propose to study whether a language model changes its evaluation of an otherwise identical job candidate when the resume shows either a 12-month career gap or a non-traditional education pathway, and whether those effects differ between frontline and knowledge-work occupations.

The project is deliberately narrower than a general audit of “bias in hiring AI.” It focuses on two common labor-market signals that are economically meaningful, experimentally manipulable, and feasible to study rigorously within four months.

## 2. Motivation

AI systems are increasingly used for tasks that resemble screening, ranking, and candidate evaluation. A model does not need to make the final hiring decision to affect labor-market access: small changes in fit scores or interview recommendations can alter who advances to human review.

Career gaps and non-traditional education pathways are useful signals to study because they affect many groups without mapping cleanly onto a single protected category. Career interruptions are common among caregivers, returning workers, veterans, immigrants, and people moving between industries. Non-traditional education includes part-time study and other routes used by people who cannot follow a continuous full-time pathway.

The occupational comparison is central to the economic question. Employers may interpret the same signal differently depending on the type of work. A career gap could be penalized more strongly in a knowledge-work role, where employers may infer skill depreciation, or in an operational role, where recent continuity may be treated as evidence of reliability. The direction is not obvious in advance and should be measured rather than assumed.

## 3. Empirical design

The study uses a matched synthetic-resume audit. I begin with 32 base candidate profiles covering eight occupations: four frontline or operational roles and four knowledge-work roles. Each base profile is expanded into four treatment variants:

- no career gap, traditional education;
- 12-month career gap, traditional education;
- no career gap, non-traditional education;
- 12-month career gap, non-traditional education.

Within a matched set, experience, skills, achievements, employer history, education level, target role, formatting, and resume length are held fixed. A control name is also fixed within each set. This produces 128 unique resumes. Each resume is evaluated five times at one locked temperature, for 640 planned model evaluations.

The primary outcomes are:

1. fit score from 1 to 10;
2. binary interview recommendation;
3. model confidence from 0 to 1.

The primary models estimate the career-gap effect, the education-pathway effect, and each treatment's interaction with frontline occupational status. The specifications include matched-set and occupation fixed effects, with standard errors clustered by matched resume. Multiple testing is addressed using the Benjamini-Hochberg procedure across the preregistered treatment terms.

All evaluation order is randomized before the first API request. Raw responses, failures, refusals, exact model ID, prompts, timestamps, latency, parser status, and error types are retained. No observation is selectively rerun.

## 4. Four-month work plan

### 4.1 Freeze the external preregistration

Before the first live model request, I will submit the design to OSF or AsPredicted. The repository already contains ready-to-submit registration text. The live runner is configured to refuse execution unless a valid external registration URL is supplied.

### 4.2 Run the confirmatory audit

I will execute the complete 640-evaluation design using one exact model ID, one prompt version, and one locked temperature. I will preserve the complete run manifest and raw outputs.

### 4.3 Estimate the primary models

I will estimate treatment effects on fit score, interview recommendation, and confidence. The analysis will report point estimates, clustered standard errors, 95% confidence intervals, and false-discovery-rate-adjusted q-values.

### 4.4 Complete robustness and diagnostic analysis

I will report refusal and parsing-failure rates, repeated-call variance, treatment means by occupation tier, a logistic recommendation model when estimable, and a sensitivity analysis treating failed recommendations as not recommended. Occupation-specific results will be presented descriptively rather than as a large set of underpowered confirmatory tests.

### 4.5 Publish a reproducible research output

The final output will include a concise research paper, de-identified synthetic audit data, the run manifest, analysis tables, figures, code, and a clear account of null findings, failures, and deviations. The goal is a public empirical result that can be inspected and reproduced, not only an internal demonstration.

## 5. Scope discipline

The four-month project does **not** promise:

- a new human name-perception study;
- a live perceived-name-signal experiment;
- a human hiring-manager benchmark;
- a multi-model comparison;
- a production hiring-system deployment study.

Those are reasonable extensions, but including them in the fellowship plan would make the project less credible and reduce the time available for careful analysis and writing. The perceived-name work remains documented in the repository as a separate future research track. Its first pretest failed the locked balance rules, and the project preserves that result rather than weakening the standard.

## 6. Expected contribution

The project will provide evidence on whether AI-mediated screening responds to career continuity and education pathway after qualifications are held fixed. It will also show whether those effects vary between frontline and knowledge-work roles.

The contribution is both substantive and methodological. Substantively, the study addresses workforce re-entry, credential alternatives, occupational mobility, and access to AI-mediated hiring. Methodologically, it demonstrates a reproducible way to audit language-model screening behavior while preserving raw outputs, preregistering analysis, retaining failures, and distinguishing software validation from live-model evidence.

## 7. Feasibility and risks

The resume generator, randomized runner, parser, analysis pipeline, tests, and continuous-integration workflow are already implemented. A deterministic placebo run completed all 640 evaluations and exactly recovered the planted fit-score effects. The main remaining empirical task is the live model run and interpretation.

The primary risks are model refusals, limited variation in interview recommendations, and effects that are smaller than the design can estimate precisely. These are research outcomes rather than reasons to change the design. Refusals and failures will be reported, non-estimable outcomes will be labeled as such, and null results will be treated as informative.

## 8. Deliverables

By the end of four months, I expect to deliver:

1. an externally timestamped preregistration;
2. the complete 640-evaluation audit dataset and run manifest;
3. preregistered estimates and robustness checks;
4. publication-quality figures and tables;
5. a concise empirical paper and policy-oriented summary;
6. a public, reproducible repository.
