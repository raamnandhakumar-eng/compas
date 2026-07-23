# Audit model card

## Intended use

COMPAS measures whether one exact language model changes structured resume-screening outputs when controlled synthetic signals change and qualifications remain fixed.

## Current model status

- Placebo provider: `mock-auditor-v2` completed for the original 1,280-evaluation software validation.
- Expanded placebo provider: `mock-auditor-v3` used to test the planned 2,560-evaluation pipeline.
- Live Claude model: not selected or run. The exact model ID must be supplied through `ANTHROPIC_MODEL` and recorded in every row.

## Inputs

Synthetic resumes, a fixed target-role description, a locked system prompt, and a locked user-prompt format.

## Outputs

Primary structured outputs are fit score, interview recommendation, and confidence. Free-text explanations are secondary.

## Data retention

Every raw response, refusal, parsing failure, error type, prompt, model identifier, timestamp, temperature, trial number, and latency is retained. Selective reruns are prohibited.

## Known limitations

Model behavior may change across exact model IDs, dates, prompts, temperatures, and providers. Audit results do not establish employer behavior, legal liability, intent, or actual demographic identity.
