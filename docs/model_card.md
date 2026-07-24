# LLM Hiring Bias Audit model card

## Intended use

LLM Hiring Bias Audit measures whether one exact language model changes structured resume-screening outputs when controlled synthetic career signals change and qualifications remain fixed.

The core study tests career gaps and education pathways across frontline and knowledge-work occupations. It is a research audit and must not be used to rank real applicants or make employment decisions.

## Current model status

- Placebo provider: `mock-auditor-v2` completed for the original 1,280-evaluation software validation.
- Core placebo provider: `mock-auditor-v3` completed the 640-evaluation core pipeline and estimator validation.
- Name-extension placebo provider: `mock-auditor-v3` is used only for software validation of the blocked extension.
- Live Anthropic model: not selected or run. One exact model ID must be supplied through `ANTHROPIC_MODEL` and recorded in every row.

## External preregistration

A live Anthropic run requires a permanent OSF or AsPredicted registration URL through `EXTERNAL_PREREGISTRATION_URL`. The runner rejects missing, non-HTTPS, or unapproved-host URLs and records the accepted URL in every observation and the run manifest.

Prepared registration text is stored in:

- `docs/osf_preregistration.md`;
- `docs/aspredicted_preregistration.md`.

The external registration has not yet been submitted.

## Inputs

Synthetic resumes, a fixed target-role description, a locked system prompt, and a locked user-prompt format.

## Outputs

Primary structured outputs are fit score, interview recommendation, and confidence. Free-text explanations are secondary.

## Data retention

Every raw response, refusal, parsing failure, provider failure, error type, prompt, exact model identifier, external registration URL, timestamp, temperature, trial number, execution order, and latency is retained. Selective reruns are prohibited.

## Known limitations

Model behavior may change across exact model IDs, dates, prompts, temperatures, and providers. The occupational sample is purposive and synthetic. Audit results do not establish employer behavior, legal liability, model intent, effects on actual applicants, economy-wide effects, or actual demographic identity.
