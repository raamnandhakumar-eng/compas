#!/usr/bin/env bash
set -euo pipefail

: "${EXTERNAL_PREREGISTRATION_URL:?Submit the OSF or AsPredicted registration, then set EXTERNAL_PREREGISTRATION_URL.}"
: "${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY before a live run.}"
: "${ANTHROPIC_MODEL:?Set ANTHROPIC_MODEL to the exact model ID before a live run.}"

hiring-audit-validate-names --config config/audit.yaml
hiring-audit-generate --config config/audit.yaml
hiring-audit-run --config config/audit.yaml --provider anthropic
hiring-audit-analyze \
  --input outputs/screening_results.csv \
  --output-dir results/live

printf 'Live audit completed. Preserve outputs, manifest, prompts, and raw responses.\n'
