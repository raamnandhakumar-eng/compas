# Pre-analysis plan

## Research question

Holding stated qualifications constant, do controlled resume signals change an LLM's fit score or interview recommendation, and do those changes differ between frontline and knowledge-work roles?

## Confirmatory hypotheses

1. At least one name-signal group differs from the locked reference group (`signal_b`) in mean fit score.
2. A 12-month career gap lowers mean fit score and recommendation probability.
3. Non-traditional education wording lowers mean fit score and recommendation probability.
4. At least one signal penalty differs between frontline and knowledge-work templates.

All hypotheses are two-sided. Null results will be reported.

## Name-signal validation lock

The configured names are neutral experimental signals until they pass a separate validation stage.

Before a live model run:

1. screen first and last names with the complete 2020 Census name files;
2. record first-name frequency by the preregistered birth-year range using SSA data;
3. lock the intended perceived group and perceived gender for each name;
4. collect approximately 100 to 200 perception ratings per name;
5. apply the thresholds in `config/audit.yaml` without changing them after seeing results.

The pretest measures perceived race or ethnicity, perceived gender, familiarity, socioeconomic impression, and classification confidence. Every configured name must receive `approved_for_live_audit = true` from `compas-validate-names` before a live run.

The full procedure is in [`docs/name_signal_validation_protocol.md`](name_signal_validation_protocol.md).

## Design

- 4 qualification-matched role templates
- 8 synthetic candidate names across 4 signal groups
- 2 education-pathway conditions
- 2 career-gap conditions
- 128 unique resumes
- 2 temperatures
- 5 repeated trials per resume-temperature cell
- 1,280 planned evaluations per model

Execution order is randomized with the locked seed. The prompt and configuration are hashed. Malformed responses are retained as failures and excluded from outcome regressions only under the documented parsing rule.

## Primary outcomes

1. Fit score from 1 to 10
2. Binary interview recommendation

Secondary outcomes are model confidence, parser-failure rate, within-resume score variance, and coded risk-factor language.

## Estimation

The locked linear specification includes:

- signal-group indicators, with `signal_b` as the reference;
- signal-group by frontline interactions;
- non-traditional education and its frontline interaction;
- career gap and its frontline interaction;
- template fixed effects;
- temperature fixed effects.

Standard errors are clustered by `resume_id` because each matched resume is evaluated repeatedly. Benjamini-Hochberg q-values control the false discovery rate across reported coefficients. Binary recommendations are estimated with a linear probability model for interpretability; logit is a robustness check when convergence permits.

## Exclusions

A trial is excluded from outcome estimation only if:

- the provider request failed;
- no JSON object can be parsed;
- a required field is missing;
- fit score is outside 1 to 10;
- confidence is outside 0 to 1;
- recommendation is not Boolean.

Failure rates are still reported by signal group and occupational tier.

## Interpretation rule

A detected coefficient is evidence about the specified model, prompt, date, and synthetic stimuli. It is not proof of unlawful discrimination, intent, employer behavior, or a person's actual protected identity.

Name-based coefficients may be described using demographic language only when the name stimuli have passed the preregistered perception pretest. Otherwise, they remain `signal_a` through `signal_d`.

## Status

The placebo validation is complete. The current names have not completed source screening or the perception pretest. The live-model confirmatory analysis has not been run in this repository as of July 23, 2026.
