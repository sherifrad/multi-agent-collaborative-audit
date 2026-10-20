#!/usr/bin/env bash
# ==============================================================================
# Script: bootstrap.sh
# Purpose: Non-blocking discovery, health-check, and initialization for
#          the 'delegate-skills' orchestration environment.
# ==============================================================================

set -uo pipefail

DELEGATE_DIR="${DELEGATE_SKILLS_DIR:-$HOME/.config/delegate-skills}"
REPO_FALLBACK_URL="${DELEGATE_REPO_URL:-}"
EXIT_STATUS=0

echo "🔍 [Bootstrap] Verifying 'delegate-skills' orchestration engine..."

# 1. Check directory presence
if [ ! -d "$DELEGATE_DIR" ]; then
    echo "⚠️ Directory '$DELEGATE_DIR' does not exist."
    if [ -n "$REPO_FALLBACK_URL" ] && command -v git >/dev/null 2>&1; then
        echo "🔄 Cloning from provided DELEGATE_REPO_URL: $REPO_FALLBACK_URL..."
        if git clone --depth 1 "$REPO_FALLBACK_URL" "$DELEGATE_DIR" 2>/dev/null; then
            echo "✅ Successfully cloned delegate-skills."
        else
            echo "⚠️ Clone failed. Initializing empty local workspace directory..."
            mkdir -p "$DELEGATE_DIR"
            EXIT_STATUS=2
        fi
    else
        echo "ℹ️ No remote git URL configured. Initializing local sandbox directory..."
        mkdir -p "$DELEGATE_DIR"
        EXIT_STATUS=2
    fi
else
    # 2. Directory exists, check if it's a git repo
    if [ -d "$DELEGATE_DIR/.git" ] && command -v git >/dev/null 2>&1; then
        echo "🔄 Git repository detected. Checking remote updates..."
        # Avoid hanging on interactive prompts or broken networks
        if git -C "$DELEGATE_DIR" pull --ff-only --timeout=5 origin main >/dev/null 2>&1; then
            echo "✅ 'delegate-skills' successfully updated from remote."
        else
            echo "ℹ️ Network offline, branch mismatch, or timeout. Using cached local version."
        fi
    else
        echo "ℹ️ Local non-git directory active. Using local configuration."
    fi
fi

# 3. Detect available delegate-skills relays & external model CLIs
echo "🔎 [Delegate Skills Discovery] Scanning installed delegate relays..."
FOUND_DELEGATES=0
for dskill in "claude-delegate" "opencode-delegate" "codex-delegate" "agy-delegate"; do
    if [ -d "$HOME/.agents/skills/$dskill" ] || [ -d "$HOME/.config/opencode/skills/$dskill" ]; then
        echo "  ✔️ Detected delegate skill: $dskill"
        FOUND_DELEGATES=$((FOUND_DELEGATES + 1))
    fi
done

echo "🔎 [Fleet Discovery] Scanning available engine runtimes..."
FOUND_CLIS=0

for cli in "claude" "opencode" "deepseek" "gemini" "codex" "gh"; do
    if command -v "$cli" >/dev/null 2>&1; then
        echo "  ✔️ Detected runtime CLI: $cli"
        FOUND_CLIS=$((FOUND_CLIS + 1))
    fi
done

echo "🔎 [Diagnostic Plugins Discovery] Scanning testing & profiling skills..."
for diag in "android-profiler" "android-cli" "firebase-crashlytics" "testing-setup" "a11y-debugging"; do
    if [ -d "$HOME/.gemini/config/skills/$diag" ] || [ -d "$HOME/.agents/skills/$diag" ]; then
        echo "  ✔️ Detected diagnostic skill: $diag"
    fi
done

if [ "$FOUND_CLIS" -eq 0 ]; then
    echo "ℹ️ No external model CLIs detected in PATH."
    echo "   Fleet Orchestrator will activate Tier-2 (Subagents) or Tier-3 (Single-Model Multi-Session Tabula Rasa)."
else
    echo "✅ Fleet Discovery complete: $FOUND_CLIS runtime CLI(s) and $FOUND_DELEGATES delegate skill(s) available."
fi

# 4. Final status report
if [ "$EXIT_STATUS" -eq 0 ]; then
    echo "🚀 [Bootstrap] Engine ready. Orchestrator can proceed with lane allocation."
    exit 0
else
    echo "⚠️ [Bootstrap] Degraded/Sandbox mode active (status code: $EXIT_STATUS). Proceeding with local fallbacks."
    exit 0
fi
