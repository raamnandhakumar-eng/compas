# Methodology

## Estimand

The primary estimand is the conditional difference in LLM screening outcomes associated with a controlled resume signal, holding the base resume template and observed qualifications constant. The main interaction asks whether this difference changes between frontline and knowledge-work roles.

## Experimental design

Each standardized base resume is permuted across:

- experimental name-signal groups;
- traditional and non-traditional education wording;
- zero and twelve months of career interruption;
- repeated trials and temperature settings.

The signal labels describe experimental stimuli. They are not verified demographic identities and must not be applied to real people.

## Outcomes

Primary outcomes are fit score, binary recommendation, model confidence, and within-resume score variance. Text outcomes such as stated risk factors should use a preregistered taxonomy or blinded coding protocol.

## Econometric specification

```text
Y_it = beta_0
     + beta_1 Signal_i
     + beta_2 Frontline_i
     + beta_3 Signal_i x Frontline_i
     + beta_4 NonTraditional_i
     + beta_5 NonTraditional_i x Frontline_i
     + beta_6 Gap_i
     + beta_7 Gap_i x Frontline_i
     + template fixed effects
     + temperature fixed effects
     + error_it
```

The default implementation reports HC1 robust standard errors. Larger studies should consider clustering by base template, model session, or prompt batch. Binary recommendations should also be checked with logit or fractional-response models.

## Reliability checks

Before drawing conclusions, test prompt paraphrases, alternative role descriptions, multiple temperatures, multiple model snapshots or providers, randomized request order, score versus pairwise-choice prompts, equal-length formatting, and parser-failure rates by group.

## Limits

This synthetic audit measures model behavior under a specific experimental configuration. It does not measure actual employer discrimination, downstream hiring outcomes, legal liability, or a person's true protected status. Results can change across model versions, dates, prompts, and provider infrastructure.

## Responsible disclosure

Reproduce any disparity with a locked configuration, estimate practical magnitude and uncertainty, test sensitivity, document the exact model and date, protect credentials and data, and avoid strong causal or legal claims unsupported by the design.
