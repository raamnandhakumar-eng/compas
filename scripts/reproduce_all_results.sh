#!/usr/bin/env bash
set -euo pipefail

python -m pip install -e ".[dev]"
ruff check .
pytest -q
python scripts/power_analysis.py
compas-validate-names --config config/audit.yaml
compas-generate --config config/audit.yaml
compas-run --config config/audit.yaml --provider mock
compas-analyze \
  --input outputs/screening_results.csv \
  --output-dir outputs/analysis
python scripts/make_result_figures.py

printf 'Reproduced validation outputs. Live and human results remain separate.\n'
