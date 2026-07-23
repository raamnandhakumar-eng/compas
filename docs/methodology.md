# Methodology

## Estimand

The primary estimand is the conditional difference in screening outcomes associated with a controlled resume signal, holding the base template and stated qualifications constant. The main interaction asks whether that difference changes between frontline and knowledge-work roles.

## Experimental design

Each standardized base resume is permuted across name-signal group, education pathway, career-gap condition, repeated trial, and temperature. The signal labels describe experimental stimuli. They are not verified demographic identities and must not be applied to real people.

## Outcomes

Primary outcomes are fit score and binary recommendation. Secondary outcomes are model confidence, within-resume score variance, response failure, and coded risk-factor language.

## Econometric specification

```text
Y_it = beta_0
     + signal-group indicators
     + signal-group x frontline interactions
     + non-traditional education
     + non-traditional education x frontline
     + career gap
     + career gap x frontline
     + template fixed effects
     + temperature fixed effects
     + error_it
```

Standard errors are clustered by `resume_id`, the repeated experimental unit. Benjamini-Hochberg q-values control the false discovery rate across reported coefficients. The binary outcome is reported as a linear probability model for direct percentage-point interpretation, with logit as a robustness check when feasible.

## Placebo validation

`mock-auditor-v2` contains transparent planted score effects and balanced deterministic trial noise. Its purpose is to verify exact recovery of the locked estimand, parsing behavior, repeated-trial handling, and output generation. Placebo p-values are not substantive findings.

## Reliability checks

A live study should test prompt paraphrases, alternative role descriptions, multiple model snapshots, randomized request order, equal-length formatting, score versus pairwise-choice prompts, and parser-failure rates by group.

## Limits

This synthetic audit measures model behavior under a specific configuration. It does not measure actual employer discrimination, downstream hiring outcomes, legal liability, or a person's true protected status. Results can change across models, dates, prompts, and provider infrastructure.

## Responsible disclosure

Reproduce disparities with a locked configuration, estimate practical magnitude and uncertainty, test sensitivity, document the exact model and date, protect credentials and raw data, and avoid causal or legal claims unsupported by the design.
