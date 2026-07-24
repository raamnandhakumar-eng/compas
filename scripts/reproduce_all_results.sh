#!/usr/bin/env bash
set -euo pipefail

python -m pip install -e ".[dev]"
ruff check .
pytest -q
python scripts/power_analysis.py
hiring-audit-validate-names --config config/audit.yaml
hiring-audit-generate --config config/audit.yaml
hiring-audit-run --config config/audit.yaml --provider mock
hiring-audit-analyze \
  --input outputs/screening_results.csv \
  --output-dir outputs/analysis
python scripts/make_result_figures.py

printf 'Reproduced validation outputs. Live and human results remain separate.\n'
