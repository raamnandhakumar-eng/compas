# Power analysis

This calculation was fixed before any live Claude result was observed. It is a planning calculation, not a claim about realized model variance.

## Planned design

- 32 matched base profiles: 8 occupations × 4 profiles
- 16 treatment variants per matched profile
- 5 repeated model calls per resume
- 2,560 total live evaluations at the locked primary temperature
- two-sided alpha of 0.05 and target power of 0.80

## Assumptions

The calculation treats each base profile as the independent matched unit. It assumes that averaging five repeated calls yields a standard deviation of 0.60 fit-score points for a matched treatment contrast and 0.35 for a recommendation-rate contrast.

Under those assumptions, the planned design has approximate minimum detectable effects of:

- **0.30 fit-score points**;
- **0.17 in recommendation probability**.

Using more conservative single-call standard deviations of 0.90 fit-score points and 0.50 for recommendations, approximately three repeated calls per resume would meet target effects of 0.30 and 0.15 respectively. Five trials were selected to provide additional stability and to permit direct estimation of within-resume model-call variance.

## Limitations

These formulas are analytic approximations. The confirmatory report will show observed repeated-call variance and will distinguish the preregistered assumptions from realized precision. The sample should not be enlarged or stopped early in response to emerging treatment estimates.

Reproduce the calculation with:

```bash
python scripts/power_analysis.py
```
