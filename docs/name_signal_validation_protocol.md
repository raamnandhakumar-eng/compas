# Perceived-name-signal validation protocol

The configured names are experimental stimuli, not actual demographic identities. A placebo run may use neutral signal codes, but a live audit cannot use demographic interpretation until every name passes both public-source screening and a separate human perception pretest.

## 1. Public-source screening

Use **complete published tables for names occurring approximately 100 or more times** rather than a top-name list.

Record from the 2020 Census:

- first-name count;
- first-name race and Hispanic-origin shares;
- first-name sex share;
- surname count;
- surname race and Hispanic-origin shares.

Census counts and percentages are aggregate statistics and include disclosure-protection adjustments. Research files may retain negative values created by the disclosure-avoidance process. These values do not identify individuals or establish the identity of anyone with a given name.

Record SSA national first-name frequency from the locked birth-name archive. Avoid extremely rare names. Each experimental group must contain at least two names.

The populated registry is `data/name_validation/name_candidates.csv`. Passing this stage gives a row the status `source_screened_pending_pretest`; it does not approve the name for a live audit.

## 2. Lock intended perceptions before surveying

For every name, preregister the intended perceived-name-signal group. Do not choose or revise the intended label after viewing survey responses.

The analysis uses neutral codes such as `signal_a` through `signal_d`. Public reporting must say **perceived name signal**, never actual race, ethnicity, or gender.

## 3. Perception pretest

Recruit approximately 100 to 200 respondents. Show names without resumes, jobs, qualifications, treatment labels, or study hypotheses, and randomize name order.

For each name, measure:

1. perceived race or ethnicity;
2. perceived gender;
3. familiarity on a five-point scale;
4. perceived socioeconomic status on a five-point scale;
5. confidence on a five-point scale;
6. whether the name seems unusual on a five-point scale.

Collect informed consent and at least one attention check. The response schema is `data/name_validation/perception_responses.csv`.

## 4. Locked approval rules

The thresholds were fixed before collecting responses. A name is approved only when:

- public-source screening is complete;
- at least 100 valid respondents rated it;
- the modal perceived group matches the preregistered signal;
- intended-group agreement is at least 70%;
- intended-gender agreement is at least 70%;
- median confidence is at least 4/5;
- the between-group range is no more than 0.75 points for perceived socioeconomic status;
- the between-group range is no more than 0.75 points for familiarity;
- the between-group range is no more than 0.75 points for unusualness.

The balance checks reduce the risk that a nominal perceived-group comparison is driven by class, familiarity, or unusualness.

## 5. Outputs and enforcement

Run:

```bash
compas-validate-names --config config/audit.yaml
```

This writes:

- `results/name_validation/name_summary.csv`
- `results/name_validation/name_balance_tests.csv`

The current files correctly show zero respondents and no approved names because the survey has not been conducted. A live Anthropic run stops unless every configured name has `approved_for_live_audit = true`.

## Interpretation

Passing the protocol would show that respondents in the survey consistently perceived a stimulus in the preregistered way. It would not establish anyone's actual identity, guarantee the same perception in every population, or eliminate all cultural and socioeconomic associations.
