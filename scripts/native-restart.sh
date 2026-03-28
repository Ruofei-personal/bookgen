#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/scripts/native-stop.sh"
"$ROOT/scripts/native-start.sh"
