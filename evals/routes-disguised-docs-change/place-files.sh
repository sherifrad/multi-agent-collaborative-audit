#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
[ -d dot-agents ] && mv dot-agents .agents || true
mv apply-change.sh /tmp/apply-change.$$.sh
git init -q && git add -A && git -c user.email=e@x -c user.name=eval commit -qm baseline
sh /tmp/apply-change.$$.sh && rm /tmp/apply-change.$$.sh
