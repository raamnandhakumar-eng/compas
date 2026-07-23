#!/usr/bin/env bash
set -euo pipefail

: "${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY before the live run.}"
: "${ANTHROPIC_MODEL:?Set ANTHROPIC_MODEL to the exact model ID.}"

compas-generate --config config/core_audit.yaml
compas-run --config config/core_audit.yaml --provider anthropic
compas-analyze-core \
  --input outputs/core/screening_results.csv \
  --output-dir outputs/core/analysis

echo "Core live audit complete. Review outputs/core/run_manifest.json before interpretation."
