# Deviations from preregistration

## Before any live model audit

The repository originally used four occupations, one base profile per occupation, two
temperatures, and 1,280 placebo evaluations. Before any live Claude result was
observed, the design was expanded to:

- eight occupations;
- four base profiles per occupation;
- one locked primary temperature;
- 512 matched resumes for the full name-signal extension;
- 2,560 planned extension evaluations;
- three primary outcomes;
- a separate name-source screen and perception-pretest gate.

The original 1,280-evaluation run remains a software-validation benchmark and is not
treated as a live confirmatory result.

### Submitted perception pretest reviewed on July 23, 2026

A submitted workbook contained 150 respondent IDs and 1,200 complete ratings across
the eight preregistered names. It was reviewed before any live Claude audit.

The submission did not include consent or attention-check fields, so eligibility could
not be established under the locked exclusion rules. Descriptively, every name passed
the intended-group, perceived-gender, sample-size, and confidence thresholds. The
preregistered balance rules failed for familiarity, perceived socioeconomic status,
and unusualness.

No threshold was relaxed after viewing the data. The submitted study remains a
non-approving pretest outcome.

### Core audit separated on July 23, 2026

Before any live model output was observed, the career-gap and education-pathway
questions were separated into a core audit that does not estimate name effects.

Rationale:

- the failed name pretest concerns stimulus validity for the name treatment;
- career-gap and education-pathway treatments do not depend on that validation;
- holding one control name fixed within each matched set removes name variation from
  the core estimand;
- separating the tracks preserves the original name-validation standard rather than
  weakening it to unblock the entire project.

The core audit contains 128 resumes and 640 evaluations. It is governed by
`docs/core_audit_preregistration.md`. The full 2,560-evaluation name-signal extension
remains blocked pending the replacement procedure and successful final pretest.

This is a prospective design revision, not a response to live treatment results.

## After live audit

No post-result deviations exist because neither live track has been run. Any later
change must be dated, justified, and labeled confirmatory or exploratory before the
affected analysis is reported.
