#!/usr/bin/env bash
# MACA fleet review: send ONE identical brief to several vendor CLIs through the vendored relays,
# read-only, then print a comparison table. Run this in a normal terminal where the CLIs are installed.
# Usage: fleet_review.sh --brief FILE --cd REPO [--out DIR] --lane opencode:<provider/model> --lane codex --lane gemini ...
#        fleet_review.sh --detect        (only print which CLIs are installed)
#        fleet_review.sh --self-test
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
RELAYS="$HERE/vendor/delegate-skills/skills"
export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin"
BRIEF=""; REPO="$PWD"; OUT=""; LANES=(); MODE="run"
while [ $# -gt 0 ]; do case "$1" in
  --brief) BRIEF="$2"; shift 2;; --cd) REPO="$2"; shift 2;; --out) OUT="$2"; shift 2;;
  --lane) LANES+=("$2"); shift 2;; --detect) MODE="detect"; shift;; --self-test) MODE="self"; shift;;
  *) echo "unknown arg $1"; exit 2;; esac; done
bin_of() { case "$1" in opencode) echo opencode;; codex) echo codex;; gemini) echo gemini;; agy) echo agy;; claude) echo claude;; *) echo "";; esac; }
echo "== Fleet detection (vendors found on PATH) =="
for v in opencode codex agy claude; do
  p="$(command -v "$v" 2>/dev/null)"; printf '  %-9s %s\n' "$v" "${p:-MISSING}"; done
[ "$MODE" = detect ] && exit 0
if [ "$MODE" = self ]; then
  for v in opencode codex agy claude; do
    node "$RELAYS/$v-delegate/scripts/relay.mjs" --help >/dev/null 2>&1 && echo "relay $v: OK" || { echo "relay $v: FAIL"; exit 1; }
  done; exit 0; fi
[ -n "$BRIEF" ] && [ ${#LANES[@]} -gt 0 ] || { echo "need --brief and at least one --lane"; exit 2; }
OUT="${OUT:-$REPO/.agents/fleet-runs/$(date +%Y%m%d-%H%M%S)}"; mkdir -p "$OUT"
for lane in "${LANES[@]}"; do
  v="${lane%%:*}"; m=""; [ "$lane" != "$v" ] && m="${lane#*:}"
  label="$(echo "$lane" | tr '/: ' '___')"
  if ! command -v "$v" >/dev/null 2>&1; then echo "[$lane] SKIPPED: $v not installed"; echo "{\"lane\":\"$lane\",\"status\":\"missing\"}" > "$OUT/$label.result.json"; continue; fi
  echo "[$lane] running (read-only, up to 5 min)..."
  args=(--brief "$BRIEF" --cd "$REPO" --read-only --out-dir "$OUT/$label"); [ "$v" != gemini ] && args+=(--timeout 10m); [ -n "$m" ] && args+=(--model "$m")
  node "$RELAYS/$v-delegate/scripts/relay.mjs" "${args[@]}" >/dev/null 2>"$OUT/$label.stderr"
done
python3 - "$OUT" <<'PY'
import json,glob,os,sys
out=sys.argv[1]; print("\n== Fleet result table ==")
print(f"{'lane':34} {'status':22} {'exit':5} {'files changed':13} {'chars'}")
for d in sorted(glob.glob(out+"/*/result.json")):
    r=json.load(open(d)); lane=os.path.basename(os.path.dirname(d)); sp=r.get("finalPath") or ""; msg=(open(sp).read().strip() if sp and os.path.exists(sp) else (r.get("finalMessage","") or ""))
    if r.get("status")!="completed": msg=msg or ("FAILED: "+str(r.get("stderrTail",""))[-400:])
    open(os.path.join(out,lane+".md"),"w").write(msg)
    print(f"{lane:34} {str(r.get('status')):22} {str(r.get('exitCode')):5} {len(r.get('touchedFiles',[])):<13} {len(msg)}")
for f in glob.glob(out+"/*.result.json"): print(f"{os.path.basename(f)[:-12]:34} missing")
print("\nFindings text per lane: <lane>.md in", out)
PY
