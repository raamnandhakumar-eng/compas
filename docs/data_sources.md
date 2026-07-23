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

The current names are experimental stimuli, not verified demographic identities. They are labeled `signal_a` through `signal_d` in the data and code. The repository does not infer a real person's race, ethnicity, nationality, religion, or gender from a name.

A live demographic interpretation requires a separate perception pretest with human raters. The pretest should measure:

- perceived group association;
- perceived gender;
- familiarity;
- socioeconomic connotation;
- confidence in the perception.

The U.S. Census Bureau publishes aggregate surname frequency and race/ethnicity distributions for surnames appearing at least 100 times in the 2010 Census. That dataset can support stimulus screening but cannot establish an individual's identity: https://www.census.gov/topics/population/genealogy/data/2010_surnames.html

## Synthetic outcomes

`results/placebo/` contains outcomes from `mock-auditor-v2`. The provider has explicit planted effects and balanced deterministic trial noise. These files validate the software and estimator. They are not observations from Claude, recruiters, employers, or real applicants.

## Reproducibility date

Occupational mappings and source links were checked on July 23, 2026. Model behavior can change over time, so any live audit must store the exact model identifier, date, prompt hash, configuration hash, and raw response.
