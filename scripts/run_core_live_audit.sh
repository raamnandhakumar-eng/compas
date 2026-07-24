#!/usr/bin/env bash
set -euo pipefail

: "${EXTERNAL_PREREGISTRATION_URL:?Submit the OSF or AsPredicted registration, then set EXTERNAL_PREREGISTRATION_URL.}"
: "${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY before the live run.}"
: "${ANTHROPIC_MODEL:?Set ANTHROPIC_MODEL to the exact model ID.}"

hiring-audit-generate --config config/core_audit.yaml
hiring-audit-run --config config/core_audit.yaml --provider anthropic
hiring-audit-analyze-core \
  --input outputs/core/screening_results.csv \
  --output-dir outputs/core/analysis

echo "Core live audit complete. Review outputs/core/run_manifest.json before interpretation."
