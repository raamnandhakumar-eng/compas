# Human benchmark protocol

The human benchmark comes after the main live Claude audit. It is designed to compare treatment effects and decision agreement under the same blinded information constraints.

## Sample

Recruit **3 to 5 hiring professionals or experienced managers**. Ask the group to review approximately **100 blinded matched resumes** in total. Record broad hiring experience but avoid unnecessary sensitive information.

## Assignment

- Randomly assign resumes across evaluators.
- Never show two variants from the same matched set to the same evaluator.
- Randomize resume order.
- Hide treatment labels, study hypotheses, and Claude outputs.
- Use the same role descriptions and structured outcome scales used in the live audit.

## Outcomes

Each evaluator records:

- fit score from 1 to 10;
- interview recommendation;
- confidence from 0 to 1;
- optional strengths, risks, and one-sentence reason.

## Analysis

Report:

- human treatment effects for fit score, recommendation, and confidence;
- human-Claude agreement on matched resumes;
- differences between human and Claude treatment effects;
- evaluator-level variability;
- null, negative, and unexpected results.

Estimate the same matched-set specification used for Claude outcomes. Cluster standard errors by resume and evaluator where the sample supports multiway clustering. Use a pooled model with human-versus-Claude interactions for direct effect comparisons.

## Status and ethics

This benchmark has not been run. Use synthetic resumes only, obtain informed consent, state that responses will not affect employment decisions, and seek institutional review when required by the host institution.
