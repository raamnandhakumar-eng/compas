# Data sources and stimulus provenance

## Occupational templates

The four role templates are synthetic. Their role definitions are anchored to current O*NET-SOC occupations so that the audit uses recognizable job families rather than invented categories.

| Audit role | O*NET-SOC | O*NET title | Source |
|---|---|---|---|
| Operations Manager | 11-1021.00 | General and Operations Managers | https://www.onetonline.org/link/summary/11-1021.00 |
| Supply Chain Supervisor | 13-1081.00 | Logisticians | https://www.onetonline.org/link/summary/13-1081.00 |
| Strategy Analyst | 13-1111.00 | Management Analysts | https://www.onetonline.org/link/summary/13-1111.00 |
| Product Operations Manager | 13-1082.00 | Project Management Specialists | https://www.onetonline.org/link/summary/13-1082.00 |

O*NET content is produced for the U.S. Department of Labor and is available under CC BY 4.0 unless otherwise noted. The resume language in this repository is newly written and does not reproduce full O*NET task lists.

## Name signals

The configured names are experimental stimuli, not verified demographic identities. They remain coded as `signal_a` through `signal_d` in the analysis.

### Census name files

The primary source screen uses the complete 2020 Census name tables:

- first names by race and Hispanic origin;
- first names by sex;
- last names by race and Hispanic origin.

The files contain national aggregate counts for names reported at least 100 times. They do not identify individuals and cannot establish the identity of a person with a given name.

Official source page:

- https://www.census.gov/topics/population/genealogy/data/2020_names.html

The 2010 surname product can be used as a historical check. It reports surname frequency and race or Hispanic-origin percentages:

- https://www.census.gov/data/developers/data-sets/surnames.html

### Social Security Administration first-name files

SSA national baby-name files provide first-name counts by birth year. COMPAS uses them to check that a first name is common enough and plausible for the preregistered age cohort represented by the synthetic resume.

- https://www.ssa.gov/oact/babynames/limits.html

SSA suppresses names with fewer than five occurrences in a geographic file for privacy. The selected birth-year range must be locked before the survey or live audit.

### Perception pretest

Census and SSA associations are not enough to label a stimulus as a demographic signal. Before a live audit, approximately 100 to 200 respondents must rate each name on:

- perceived race or ethnicity;
- perceived gender;
- familiarity;
- socioeconomic impression;
- confidence in the classification.

Only names with strong agreement and acceptable familiarity and socioeconomic balance are approved. The full procedure and thresholds are in [`docs/name_signal_validation_protocol.md`](name_signal_validation_protocol.md).

The current eight names are registered in `data/name_validation/name_candidates.csv` with validation status pending. Until the source fields and perception results are completed, they must be described only as neutral experimental name signals.

## Synthetic outcomes

`results/placebo/` contains outcomes from `mock-auditor-v2`. The provider has explicit planted effects and balanced deterministic trial noise. These files validate the software and estimator. They are not observations from Claude, recruiters, employers, or real applicants.

## Reproducibility date

Occupational mappings and source links were checked on July 23, 2026. Model behavior can change over time, so any live audit must store the exact model identifier, date, prompt hash, configuration hash, and raw response.
