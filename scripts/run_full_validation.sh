#!/usr/bin/env bash
set -euo pipefail

compas-generate --config config/audit.yaml
compas-run --config config/audit.yaml --provider mock
compas-analyze --input outputs/screening_results.csv --output-dir outputs/analysis
pytest -q

echo "Validation complete. See outputs/analysis/placebo_validation_report.md"
