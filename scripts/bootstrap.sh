#!/usr/bin/env bash
# ==============================================================================
# Script: bootstrap.sh
# Purpose: 1. Runs One-Time First-Run Deep Diagnostic (first_run_preflight.py)
#             on initial use (or when skill scripts change), surfacing any
#             missing tools with actionable remediation steps.
#          2. Runs fast lightweight scan on subsequent runs.
# ==============================================================================

set -uo pipefail

export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.antigravity/bin:$HOME/Library/Android/sdk/platform-tools"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STAMP_FILE="$SKILL_ROOT/.first_run_verified.json"

FORCE_FIRST_RUN=0
if [ "${1:-}" = "--force-first-run" ]; then
    FORCE_FIRST_RUN=1
fi

echo "🔍 [MACA Bootstrap] Checking First-Run Verification Status..."

if [ ! -f "$STAMP_FILE" ] || [ "$FORCE_FIRST_RUN" -eq 1 ]; then
    echo "🚀 [First-Run Diagnostic] Executing one-time deep self-test of all skill files, relays, and external tools..."
    if ! python3 "$SCRIPT_DIR/first_run_preflight.py" --force; then
        echo "❌ [MACA_SCRIPT_ERROR — STOP_AND_FIX] First-run internal integrity check failed! Do NOT bypass."
        exit 2
    fi
    echo "⚠️ [Mandatory Agent Action] First-run diagnostic completed. Review 'missing_external_tools' above and inform the user of any missing tools + their remediation commands before proceeding!"
else
    echo "✅ [Fast Path] First-run deep check already verified ($STAMP_FILE). Running lightweight scan..."
    python3 "$SCRIPT_DIR/first_run_preflight.py"
fi

echo "🚀 [Bootstrap] Engine ready."
exit 0
