# Submitted perception-survey validation report

## Status

**Not approved for the live audit.**

The submitted workbook contains 150 respondent IDs and 1,200 complete name ratings. Every respondent rated all eight names, there are no duplicate respondent-name pairs, and no rating field is missing.

The workbook does not contain the preregistered consent or attention-check fields. Therefore respondent eligibility cannot be established from the submitted export and the strict valid-respondent count remains zero. Raw participant-level rows are not committed to the public repository because data-sharing permission is not documented.

## Descriptive signal results

| Name | Intended-group agreement | Male agreement | Median confidence | Name-level thresholds |
|---|---:|---:|---:|---|
| Arjun Patel | 90.0% | 97.3% | 5 | Pass |
| Rohan Shah | 88.0% | 94.0% | 4 | Pass |
| Ethan Miller | 96.7% | 97.3% | 5 | Pass |
| Lucas Bennett | 92.7% | 97.3% | 5 | Pass |
| Jamal Reed | 97.3% | 98.0% | 5 | Pass |
| Darius Cole | 93.3% | 98.7% | 4 | Pass |
| Carlos Garcia | 94.7% | 98.0% | 5 | Pass |
| Mateo Rodriguez | 94.0% | 97.3% | 5 | Pass |

These descriptive results indicate that respondents usually perceived the stimuli in the preregistered direction. They do not establish actual demographic identity.

## Balance checks

| Metric | Observed between-group range | Maximum allowed | Result |
|---|---:|---:|---|
| Familiarity | 0.947 | 0.750 | Fail |
| Perceived socioeconomic status | 1.130 | 0.750 | Fail |
| Unusualness | 1.713 | 0.750 | Fail |

All three balance checks fail. Under the locked protocol, this blocks approval for every name even if consent and attention-check eligibility are later documented.

## Data-quality findings

- 150 unique respondent IDs.
- Eight ratings per respondent.
- 1,200 total rows.
- No duplicate respondent-name pairs.
- No missing ratings.
- All rating scales are within 1–5.
- Consent evidence is absent from the export.
- Attention-check evidence is absent from the export.
- Survey platform, recruitment source, field dates, target population, compensation, and randomization metadata are absent.

## Required next action

Do not run the live Claude audit with these name stimuli under the current confirmatory protocol.

The defensible next step is to select a better-matched set of names using the observed familiarity, socioeconomic-status, and unusualness ratings, preregister the replacement procedure as a dated design revision before any live Claude output is observed, and conduct a new perception pretest with recorded consent and attention-check fields.

The submitted results are preserved as a non-approving pretest outcome. Thresholds were not changed after viewing the data.
