#!/usr/bin/env bash
set -euo pipefail

: "${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY before a live run.}"
: "${ANTHROPIC_MODEL:?Set ANTHROPIC_MODEL to the exact model ID before a live run.}"

compas-validate-names --config config/audit.yaml
compas-generate --config config/audit.yaml
compas-run --config config/audit.yaml --provider anthropic
compas-analyze \
  --input outputs/screening_results.csv \
  --output-dir results/live

printf 'Live audit completed. Preserve outputs, manifest, prompts, and raw responses.\n'
