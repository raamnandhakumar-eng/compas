# COMPAS

**Candidate Outcome Measurement and Prompt Audit Suite**

A reproducible synthetic audit of demographic and occupational bias in LLM-assisted resume screening.

> This repository is unrelated to the criminal-risk assessment product commonly called COMPAS.

## Research question

When qualifications are held constant, do LLM screening scores, recommendation probabilities, stated risk factors, or response stability differ across:

- perceived demographic signals;
- traditional versus non-traditional education pathways;
- short employment gaps;
- frontline operations versus corporate knowledge-work roles;
- interactions between candidate signals and occupational tier?

The project is designed for research and model evaluation. It must not be used to make real hiring decisions.

## Pipeline

```text
Resume templates
      |
      v
Matched synthetic permutations
      |
      v
Structured LLM screening trials
      |
      v
Validation and parsing
      |
      v
HC1-robust OLS / fractional logit analysis
      |
      v
Audit tables, stability metrics, and plots
```

## Key design choices

- **Matched-pair construction:** demographic and pathway signals vary while qualifications remain fixed.
- **Occupational comparison:** frontline operations and knowledge-work roles are audited separately.
- **Repeated trials:** repeated calls estimate response instability and temperature sensitivity.
- **Structured output:** every model response must return machine-readable JSON.
- **Robust inference:** regressions use HC1 heteroskedasticity-robust standard errors.
- **Safe default:** the repository runs end-to-end with a deterministic mock provider and no API key.

## Repository structure

```text
config/audit.yaml                 Audit design and model settings
data/templates/resume_templates.csv  Standardized base resumes
docs/methodology.md               Identification strategy and limitations
src/compas_audit/generate.py      Matched resume permutations
src/compas_audit/providers.py     Mock and Anthropic providers
src/compas_audit/run_audit.py     Screening experiment runner
src/compas_audit/analyze.py       Econometric analysis and plots
tests/                            Unit tests
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 1. Generate matched synthetic resumes
compas-generate --config config/audit.yaml

# 2. Run a cost-free deterministic mock audit
compas-run --config config/audit.yaml --provider mock

# 3. Estimate disparities and create outputs
compas-analyze --input outputs/screening_results.csv --output-dir outputs/analysis

# 4. Run tests
pytest
```

## Run with Claude

Set your key locally. Never commit it.

```bash
pip install -e ".[api]"
cp .env.example .env
export ANTHROPIC_API_KEY="your-key"
compas-run --config config/audit.yaml --provider anthropic
```

The model name is configurable through `config/audit.yaml` or the `ANTHROPIC_MODEL` environment variable. Review current model availability before running a paid audit.

## Main estimating equation

For candidate permutation `i` in trial `t`:

```text
FitScore_it = beta_0
            + beta_1 SignalGroup_i
            + beta_2 Frontline_i
            + beta_3 SignalGroup_i x Frontline_i
            + gamma' Controls_i
            + epsilon_it
```

The interaction coefficient tests whether a signal-associated disparity changes for frontline roles relative to knowledge-work roles. The analysis also models recommendation probability and within-resume score variance.

## Outputs

The analysis command produces:

- `descriptive_summary.csv`
- `group_disparities.csv`
- `ols_fit_score_hc1.txt`
- `ols_recommendation_hc1.txt`
- `model_coefficients.csv`
- `fit_score_by_group.png`
- `recommendation_rate_by_group.png`
- `trial_stability.csv`

## Interpretation rules

A statistically significant coefficient is not automatically evidence of unlawful discrimination or model intent. Results depend on the audit design, prompt, model version, sampling settings, name-signal validity, and multiple-testing choices. Treat the estimates as evidence about a specific experimental configuration.

## Ethics

- Use synthetic candidates only.
- Do not infer a real person's race, ethnicity, gender, disability, or other protected status from a name or resume.
- Do not deploy the screening prompt in production hiring.
- Report null results and sensitivity checks.
- Record model identifiers, dates, prompts, parameters, failures, and exclusions.
- Obtain legal and institutional review before any field experiment involving employers or real applicants.

## License

MIT. See [LICENSE](LICENSE).
