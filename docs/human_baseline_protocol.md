# Human-evaluator baseline protocol

The human baseline is designed to answer whether model disparities are smaller than, similar to, or larger than judgments made by blinded human evaluators under the same information constraints.

## Sampling

Recruit evaluators who have experience reviewing resumes or hiring candidates. Record broad experience level, but do not collect unnecessary sensitive information.

## Assignment

- Randomly assign each evaluator a subset of resumes.
- Never show two variants from the same matched template to the same evaluator.
- Randomize resume order.
- Hide experimental labels and study hypotheses.
- Use the same role description and scoring scale used for the model audit.

## Outcomes

Each evaluator records:

- fit score from 1 to 10;
- interview recommendation;
- confidence from 0 to 1;
- up to three strengths;
- up to three risks;
- one-sentence reason.

The machine-readable schema is in `data/human_baseline/evaluator_schema.csv`.

## Analysis

Estimate the same fixed-effect specification used for model outcomes. Cluster standard errors by resume and evaluator where the sample supports multiway clustering. Compare model and human coefficients with a pooled interaction model.

## Ethics

Use synthetic resumes only. Obtain informed consent. State that responses are for research and will not affect real employment decisions. Seek institutional review before recruiting participants if required by the host institution.
