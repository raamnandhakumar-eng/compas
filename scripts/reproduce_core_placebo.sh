#!/usr/bin/env bash
set -euo pipefail

hiring-audit-generate --config config/core_audit.yaml
hiring-audit-run --config config/core_audit.yaml --provider mock
hiring-audit-analyze-core \
  --input outputs/core/screening_results.csv \
  --output-dir outputs/core/analysis

echo "Core placebo reproduced under outputs/core/."
