# Design history and deviations from preregistration

## Before any live model audit

No live Anthropic model output has been requested or observed for either research track.

### Initial pipeline design

The repository originally used four occupations, one base profile per occupation, two temperatures, and 1,280 placebo evaluations. Before any live result was observed, the design was expanded to:

- eight occupations;
- four base profiles per occupation;
- one locked primary temperature;
- 512 matched resumes for the full name-signal extension;
- 2,560 planned extension evaluations;
- three primary outcomes;
- a separate name-source screen and perception-pretest gate.

The original 1,280-evaluation run remains a software-validation benchmark and is not treated as a live confirmatory result.

### Submitted perception pretest reviewed on July 23, 2026

A submitted workbook contained 150 respondent IDs and 1,200 complete ratings across the eight preregistered names. It was reviewed before any live model audit.

The submission did not include consent or attention-check fields, so eligibility could not be established under the locked exclusion rules. Descriptively, every name passed the intended-group, perceived-gender, sample-size, and confidence thresholds. The preregistered balance rules failed for familiarity, perceived socioeconomic status, and unusualness.

No threshold was relaxed after viewing the data. The submitted study remains a non-approving pretest outcome.

### Core audit separated on July 23, 2026

Before any live model output was observed, the career-gap and education-pathway questions were separated into a core audit that does not estimate name effects.

Rationale:

- the failed name pretest concerns stimulus validity for the name treatment;
- career-gap and education-pathway treatments do not depend on that validation;
- holding one control name fixed within each matched set removes name variation from the core estimand;
- separating the tracks preserves the original name-validation standard rather than weakening it to unblock the entire project.

The core audit contains 128 resumes and 640 evaluations. It is governed by `docs/core_audit_preregistration.md`. The full 2,560-evaluation name-signal extension remains blocked pending a replacement procedure and successful final pretest.

This was a prospective design revision, not a response to live treatment results.

### Public project renamed on July 23, 2026

The public project name was changed from COMPAS to **LLM Hiring Bias Audit** to remove the collision with the criminal-risk assessment product and make the subject of the repository immediately clear.

The Python distribution was renamed to `llm-hiring-bias-audit`, the conda environment was renamed, and new command-line entry points use the `hiring-audit-*` prefix.

The internal import namespace `compas_audit` and legacy `compas-*` command aliases are retained solely for backward compatibility with validated historical scripts and commits. They are not used as the public research identity.

This naming change does not alter the data, treatments, outcomes, hypotheses, sample, or statistical models.

### Fellowship scope narrowed on July 23, 2026

Before any live model output was observed, the planned four-month fellowship deliverable was narrowed to:

1. external preregistration;
2. the 640-evaluation core audit;
3. the preregistered analysis and diagnostics;
4. a public reproducibility package and concise paper.

The following were explicitly removed from the four-month commitment and retained as future research:

- a replacement name-perception study;
- the live 2,560-evaluation name-signal extension;
- a human hiring-manager benchmark;
- multi-model replication.

This change reduces over-commitment but does not remove or modify a confirmatory test in the core audit.

### External preregistration gate added on July 23, 2026

Before any live model output was observed, the project added ready-to-submit OSF and AsPredicted registration documents and made an accepted external registration URL a technical precondition for live execution.

The live runner now requires `EXTERNAL_PREREGISTRATION_URL` to contain a permanent HTTPS OSF or AsPredicted URL. The URL is preserved in each live observation and the run manifest. Mock-provider validation remains executable without an external registration because it does not produce live-model evidence.

The external registration itself remains pending until the author submits it through an authenticated OSF or AsPredicted account.

## After live audit

No post-result deviations exist because neither live track has been run. Any later change must be dated, justified, and labeled confirmatory or exploratory before the affected analysis is reported.
