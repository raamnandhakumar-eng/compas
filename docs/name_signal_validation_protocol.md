# Name-signal validation protocol

The current COMPAS names are candidate stimuli. They have not yet been validated for demographic interpretation.

A name can be used in the placebo pipeline without this step because the placebo tests software behavior. A live audit that describes names as perceived demographic signals is blocked until every configured name passes the process below.

## 1. Screen names with official frequency data

Use the complete government files rather than a top-name list.

### U.S. Census Bureau

Use the 2020 Census name tables to record:

- first-name frequency;
- first-name race and Hispanic-origin percentages;
- first-name sex percentages;
- surname frequency;
- surname race and Hispanic-origin percentages.

The 2020 files cover first and last names reported at least 100 times. They are aggregate data and do not identify individuals or establish the identity of anyone with a given name.

Official source page:

- https://www.census.gov/topics/population/genealogy/data/2020_names.html

The older 2010 surname files may be kept as a historical comparison:

- https://www.census.gov/data/developers/data-sets/surnames.html

### Social Security Administration

Use the national baby-name files to measure first-name frequency by year of birth:

- https://www.ssa.gov/oact/babynames/limits.html

Choose and preregister a birth-year range that is plausible for the experience level in the synthetic resumes. Sum the name count across that range and record it in `data/name_validation/name_candidates.csv`.

A name passes the source screen only after the registry contains the Census and SSA fields and `source_screen_complete` is set to `true`.

Government frequency data are a screening tool, not the final validation. They describe aggregate associations and naming patterns. They do not tell us how a name is perceived in the experiment.

## 2. Lock the intended perception before surveying

Before collecting responses, fill in these fields for every name:

- `intended_perceived_group`;
- `intended_perceived_gender`.

Do not choose the intended label after looking at the survey results.

The analysis continues to use neutral codes such as `signal_a` and `signal_b`. Public reporting should use language such as **perceived name signal**, never actual race, ethnicity, or gender.

## 3. Run a separate perception pretest

Recruit approximately 100 to 200 respondents. The sample should be appropriate for the labor market being studied and should not be drawn only from the research team or the model-audit participants.

Show names without resumes, qualifications, job titles, or experimental labels. Randomize their order.

For each name, ask respondents to report:

1. perceived race or ethnicity;
2. perceived gender;
3. familiarity with the name;
4. socioeconomic impression;
5. confidence in the classification.

Use five-point scales for familiarity, socioeconomic impression, and confidence. Include informed consent and at least one attention check.

The machine-readable response template is:

- `data/name_validation/perception_responses.csv`

## 4. Approval rules

The default thresholds are stored in `config/audit.yaml`.

A name is approved only when:

- the Census and SSA source screen is complete;
- at least 100 valid respondents rated it;
- the modal perceived group matches the preregistered intended group;
- group agreement is at least 80%;
- the modal perceived gender matches the preregistered intended gender;
- gender agreement is at least 80%;
- mean confidence is at least 3.5 out of 5;
- mean familiarity is no more than 3.0 out of 5;
- the range in mean socioeconomic impressions across signal groups is no more than 0.75 points.

The socioeconomic check reduces the risk that a nominal demographic comparison is actually driven by class impressions. Thresholds may be changed before data collection, but they must be locked and reported.

## 5. Produce the validation summary

After completing the source registry and adding survey responses, run:

```bash
compas-validate-names --config config/audit.yaml
```

This writes:

```text
outputs/name_validation_summary.csv
```

The file reports respondent counts, modal perceptions, agreement rates, familiarity, socioeconomic impression, confidence, source-screen status, and final approval for every name.

A live Anthropic run will stop with an error unless every configured name has `approved_for_live_audit = true` in that summary.

## Interpretation

Passing this protocol means that respondents consistently perceived the stimulus in the preregistered way under the survey conditions. It does not establish anyone's actual identity, prove that all audiences perceive the name the same way, or eliminate every cultural and socioeconomic association.
