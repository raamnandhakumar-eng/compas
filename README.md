# COMPAS

**Candidate Outcome Measurement and Prompt Audit Suite**

I built COMPAS to test a simple hiring question:

> When two resumes show the same qualifications, does an LLM score them differently because of the candidate signal, education path, career gap, or type of job?

The project creates matched synthetic resumes, sends them through the same screening prompt, checks every response, and estimates whether the scores or recommendations change. It compares frontline and operational jobs with knowledge-work jobs.

> This repository is unrelated to the criminal-risk assessment product also called COMPAS.

## What the project did

COMPAS has four parts:

1. It builds **128 synthetic resumes** from four job templates.
2. It changes only the selected experimental signals while keeping qualifications fixed.
3. It runs each resume five times at two temperatures, giving **1,280 evaluations per model**.
4. It estimates score and recommendation differences with template and temperature fixed effects, standard errors clustered by resume, and false-discovery-rate correction.

The audit varies:

- four experimental name-signal groups;
- traditional or non-traditional education wording;
- no career gap or a 12-month career gap;
- frontline or knowledge-work occupational context.

Experience, skills, education level, work history, target role, and quantified achievements stay fixed within each matched template.

![COMPAS experimental design](docs/figures/audit_design_scale.svg)

## What has actually been run

| Part | Status |
|---|---|
| Research design | Complete |
| 128 matched resumes | Complete |
| 1,280-evaluation placebo run | Complete |
| Response parser and data checks | Complete |
| Clustered regression pipeline | Complete |
| Human-evaluator protocol | Complete |
| Live Claude audit | Ready, not yet run |

The completed run used `mock-auditor-v2`, a small deterministic provider with score changes that were planted on purpose. This tests whether the code and estimator can recover effects that are already known.

It is **not evidence about Claude, employers, or real applicants**.

## Findings so far

The placebo run completed all **1,280 of 1,280 evaluations** with:

- **0 parser failures**;
- **128 unique matched resumes**;
- **4 occupational templates**;
- **2 temperatures**;
- **5 repeated trials per resume-temperature cell**.

The regression recovered every planted fit-score effect to three decimal places.

| Planted change | Expected | Recovered |
|---|---:|---:|
| 12-month career gap | -0.45 | -0.45 |
| Non-traditional education wording | -0.15 | -0.15 |
| Signal A | -0.20 | -0.20 |
| Signal C | -0.35 | -0.35 |
| Signal C in frontline roles | -0.20 extra | -0.20 extra |

The mean absolute coefficient-recovery error was below **0.001 fit-score points**.

### What this result means

The current result is methodological: the experiment runs end to end, records the required metadata, rejects malformed outputs, and recovers known score differences correctly.

### What it does not mean

The project has not yet shown that Claude or another live hiring model treats candidates differently. That conclusion requires a separate live-model run using the locked design. Live results should be reported whether they are positive, negative, or null.

The full placebo report is in [`results/placebo/placebo_validation_report.md`](results/placebo/placebo_validation_report.md).

## Roles in the audit

| Occupational group | Synthetic target role | O*NET-SOC anchor |
|---|---|---|
| Frontline / operational | Operations Manager | 11-1021.00 |
| Frontline / operational | Supply Chain Supervisor | 13-1081.00 |
| Knowledge work | Strategy Analyst | 13-1111.00 |
| Knowledge work | Product Operations Manager | 13-1082.00 |

These are standardized research templates, not real applicants or job postings.

## How the analysis works

The main models estimate fit score and recommendation outcomes using:

- candidate-signal indicators;
- signal-by-frontline interactions;
- education-pathway and career-gap terms;
- job-template fixed effects;
- temperature fixed effects;
- standard errors clustered by `resume_id`;
- Benjamini-Hochberg q-values for multiple testing.

The main labor-market question is whether the same candidate signal produces a different outcome in frontline roles than in knowledge-work roles.

The pre-analysis plan is in [`docs/preregistration.md`](docs/preregistration.md).

## Reproduce the completed validation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

compas-generate --config config/audit.yaml
compas-run --config config/audit.yaml --provider mock
compas-analyze \
  --input outputs/screening_results.csv \
  --output-dir outputs/analysis

pytest -q
```

You can also run the full sequence with:

```bash
bash scripts/run_full_validation.sh
```

## Run the live Claude audit

```bash
pip install -e ".[api]"
export ANTHROPIC_API_KEY="your-key"
export ANTHROPIC_MODEL="your-locked-model-id"

compas-generate --config config/audit.yaml
compas-run --config config/audit.yaml --provider anthropic
compas-analyze \
  --input outputs/screening_results.csv \
  --output-dir outputs/analysis
```

The runner records the model name, temperature, trial, request order, timestamp, prompt hash, configuration hash, latency, raw response, and parser error. Lock the exact model identifier before the first paid request.

## Repository map

```text
config/audit.yaml                         Experimental settings
data/templates/resume_templates.csv       Synthetic role templates
data/human_baseline/evaluator_schema.csv  Human-evaluation data format
docs/preregistration.md                   Pre-analysis plan
docs/methodology.md                       Estimation and limitations
docs/data_sources.md                      Source notes
docs/human_baseline_protocol.md           Blinded human comparison protocol
src/compas_audit/generate.py              Resume generator
src/compas_audit/providers.py             Placebo and Anthropic model clients
src/compas_audit/run_audit.py             Repeated screening run
src/compas_audit/analyze.py               Regression and result tables
results/placebo/                           Completed validation outputs
tests/test_pipeline.py                    Design and recovery tests
```

## Data and ethics

All candidates are synthetic. The signal groups describe experimental stimuli, not verified identities. Names should be perception-tested before any demographic interpretation.

Do not use this code to make real hiring decisions. Keep null results, failed responses, prompts, exclusions, model identifiers, and run dates. Any field experiment involving real applicants or employers would require separate legal and institutional review.

See [`docs/data_sources.md`](docs/data_sources.md), [`docs/human_baseline_protocol.md`](docs/human_baseline_protocol.md), and [`CITATION.cff`](CITATION.cff).

## License

MIT. See [`LICENSE`](LICENSE).
