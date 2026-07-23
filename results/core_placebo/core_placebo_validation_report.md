# Core labor-market audit placebo validation

## Status

**Pipeline and estimator validation complete.**

This report comes from the deterministic `mock-auditor-v3` provider. It tests the
640-evaluation career-gap and education-pathway pipeline. It is not evidence about
Claude, employers, hiring behavior, or actual applicants.

## Validation scale

- Evaluations attempted: **640**
- Successful evaluations: **640**
- Failed evaluations: **0**
- Refusals: **0**
- Unique matched resumes: **128**
- Base profiles: **32**
- Occupations: **8**
- Trials per resume: **5**
- Temperature: **0.0**
- Randomized execution order: **Yes**
- Selective reruns permitted: **No**
- Perceived-name effects estimated: **No**

The mock recommendation outcome was constant, so recommendation models were correctly
reported as **not estimable** rather than interpreted from numerical noise.

## Planted-effect recovery

| Term | Planted effect | Recovered estimate | Absolute error |
|---|---:|---:|---:|
| 12-month career gap | -0.450 | -0.450 | <0.000001 |
| Non-traditional education | -0.150 | -0.150 | <0.000001 |
| Career gap × frontline | 0.000 | 0.000 | <0.000001 |
| Non-traditional × frontline | 0.000 | 0.000 | <0.000001 |

Mean absolute recovery error was below machine-reporting precision and rounds to
**0.000 fit-score points**.

## What this establishes

The core workflow can:

- generate the complete 128-resume matched design;
- hold names fixed within matched sets;
- randomize 640 evaluations;
- retain exact prompts, raw responses, failures, and run metadata;
- estimate the preregistered career-gap and education-pathway models;
- detect non-estimable outcomes;
- recover known planted fit-score effects.

It does not establish how a live model will respond. Live findings must be produced
with one exact model ID under the locked core preregistration.
