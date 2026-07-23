# COMPAS

## Candidate Outcome Measurement and Prompt Audit Suite

A reproducible audit of demographic, education-pathway, career-gap, and occupational signals in LLM resume screening.

> This repository is unrelated to the criminal-risk assessment product commonly called COMPAS.

Hiring systems increasingly use language models to summarize, score, or rank applicants. COMPAS asks a controlled labor-market question:

> When qualifications are held constant, does changing a resume signal alter an LLM's screening decision, and is that change different for frontline and knowledge-work roles?

The repository contains a complete matched-resume generator, structured model runner, clustered econometric analysis, pre-analysis plan, human-baseline protocol, tests, and a committed placebo validation.

## Empirical status

| Stage | Status |
|---|---|
| Research design | Complete |
| 128 matched synthetic resumes | Complete |
| 1,280-evaluation placebo run | Complete |
| Parser and estimator validation | Complete |
| Clustered inference and FDR correction | Complete |
| Human-evaluator protocol | Complete |
| Live Claude audit | Ready, not yet run |

The committed results in `results/placebo/` come from `mock-auditor-v2`, a deterministic provider with transparent planted effects. They validate the software and estimation strategy. They are **not findings about Claude, employers, or real applicants**.

## Placebo validation result

The full validation completed 1,280 of 1,280 planned evaluations with zero parser failures. The clustered estimator recovered the planted fit-score coefficients with a mean absolute error below 0.001 points.

| Planted effect | Expected | Recovered |
|---|---:|---:|
| Career gap | -0.45 | -0.45 |
| Non-traditional education | -0.15 | -0.15 |
| Signal A | -0.20 | -0.20 |
| Signal C | -0.35 | -0.35 |
| Signal C × frontline | -0.20 | -0.20 |

See [`results/placebo/placebo_validation_report.md`](results/placebo/placebo_validation_report.md) for the complete table.

## Research design

Four qualification-matched templates cover two occupational tiers:

**Frontline and operational**

- Operations Manager, mapped to O*NET-SOC 11-1021.00
- Supply Chain Supervisor, mapped to O*NET-SOC 13-1081.00

**Knowledge work**

- Strategy Analyst, mapped to O*NET-SOC 13-1111.00
- Product Operations Manager, mapped to O*NET-SOC 13-1082.00

Within each template, the study holds constant experience, skills, education level, work history, and quantified achievement. It varies:

- four experimental name-signal groups;
- traditional versus non-traditional education wording;
- zero versus twelve months of career interruption;
- two temperatures;
- five repeated trials.

This produces 128 unique resumes and 1,280 evaluations per model.

![COMPAS experimental design](docs/figures/audit_design_scale.svg)

## Identification and inference

The locked model includes signal-group indicators and frontline interactions, education-pathway and career-gap effects, template fixed effects, and temperature fixed effects. Standard errors are clustered by `resume_id`. Benjamini-Hochberg q-values are included for multiple-testing control.

The confirmatory design is documented in [`docs/preregistration.md`](docs/preregistration.md).

## Reproduce the completed validation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
compas-generate --config config/audit.yaml
compas-run --config config/audit.yaml --provider mock
compas-analyze --input outputs/screening_results.csv --output-dir outputs/analysis
pytest -q
```

Or run `bash scripts/run_full_validation.sh`.

## Run the live Claude audit

```bash
pip install -e ".[api]"
export ANTHROPIC_API_KEY="your-key"
export ANTHROPIC_MODEL="your-model-id"
compas-generate --config config/audit.yaml
compas-run --config config/audit.yaml --provider anthropic
compas-analyze --input outputs/screening_results.csv --output-dir outputs/analysis
```

The runner stores model name, temperature, trial, execution order, timestamp, prompt hash, configuration hash, latency, raw response, and parser error. Lock the exact model identifier before the first paid request.

## Repository structure

```text
config/audit.yaml                         Locked experimental settings
data/templates/resume_templates.csv       O*NET-anchored synthetic templates
data/human_baseline/evaluator_schema.csv  Human baseline data schema
docs/preregistration.md                   Confirmatory analysis plan
docs/methodology.md                       Identification and limitations
docs/data_sources.md                      Source provenance
docs/human_baseline_protocol.md           Blinded evaluator protocol
src/compas_audit/generate.py              Matched resume generation
src/compas_audit/providers.py             Placebo and Anthropic providers
src/compas_audit/run_audit.py             Randomized repeated experiment
src/compas_audit/analyze.py               Clustered models and FDR correction
results/placebo/                           Committed validation outputs
tests/test_pipeline.py                    Design and recovery tests
```

## Data and ethics

All candidates are synthetic. Signal labels are experimental stimuli, not verified identities. Names require perception pretesting before demographic interpretation. This system must not be used for real hiring decisions. Null results, failures, prompts, exclusions, and model identifiers must be retained.

See [`docs/data_sources.md`](docs/data_sources.md), [`docs/human_baseline_protocol.md`](docs/human_baseline_protocol.md), and [`CITATION.cff`](CITATION.cff).

## License

MIT. See [`LICENSE`](LICENSE).
