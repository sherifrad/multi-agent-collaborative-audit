#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
[ -d dot-agents ] && mv dot-agents .agents || true
