#!/usr/bin/env bash
set -euo pipefail

compas-generate --config config/core_audit.yaml
compas-run --config config/core_audit.yaml --provider mock
compas-analyze-core \
  --input outputs/core/screening_results.csv \
  --output-dir outputs/core/analysis

echo "Core placebo reproduced under outputs/core/."
