# Name-signal pretest recovery plan

## Why a new pretest is required

The submitted 150-person pretest strongly recognized the intended perceived-name
signals, but it failed the locked balance rules for familiarity, perceived
socioeconomic status, and unusualness. Consent and attention-check evidence was also
missing from the export. The original eight names therefore remain ineligible for a
live name-signal audit.

No threshold will be relaxed after observing those results.

## Stage 1: expand the candidate pool

Construct a source-screened pool of at least 4 to 6 candidate names per signal group.
For every candidate retain Census and SSA source fields, the exact source files,
download dates, and screening notes. Names remain experimental stimuli and must never
be described as actual demographic identities.

## Stage 2: selection pilot

Recruit approximately 30 to 50 respondents for stimulus selection only. Record:

- informed consent;
- attention-check result;
- randomized name order;
- perceived race or ethnicity;
- perceived gender;
- familiarity;
- perceived socioeconomic status;
- confidence;
- unusualness;
- platform, recruitment source, dates, target population, and compensation.

Use `compas-select-balanced-names` to select two names per signal group. The algorithm:

1. excludes candidates below the preregistered agreement, gender, confidence, or
   valid-response thresholds;
2. evaluates every feasible two-name combination across groups;
3. minimizes the largest between-group range across familiarity, socioeconomic
   impression, and unusualness;
4. breaks ties using total imbalance and then stronger average recognition;
5. refuses approval when the best available panel exceeds any 0.75 balance limit.

The pilot selects stimuli only. It does not provide final approval.

## Stage 3: final perception pretest

Freeze the selected eight names and recruit 100 to 200 new respondents. Apply the
original locked approval rules:

- at least 100 valid responses per name;
- at least 70% intended-group agreement;
- at least 70% intended-gender agreement;
- median confidence at least 4/5;
- between-group range no greater than 0.75 for familiarity;
- between-group range no greater than 0.75 for perceived socioeconomic status;
- between-group range no greater than 0.75 for unusualness.

The final export must include consent and attention-check fields. Only a new final
pretest can set `approved_for_live_audit = true`.

## Separation from the core audit

The career-gap and education-pathway core audit may run independently under
`config/core_audit.yaml`. The perceived-name-signal extension remains blocked until
this recovery plan is completed.
