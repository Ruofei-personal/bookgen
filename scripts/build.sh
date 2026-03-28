#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
uv sync --frozen
cd "$ROOT/frontend"
npm ci
npm run build

# Next.js standalone output does not automatically include browser static assets.
# Copy them into the standalone tree so node .next/standalone/server.js can serve
# /_next/static/* correctly in native deployments.
mkdir -p .next/standalone/.next
rm -rf .next/standalone/.next/static
cp -r .next/static .next/standalone/.next/static

# Keep public assets alongside the standalone server when present.
if [ -d public ]; then
  rm -rf .next/standalone/public
  cp -r public .next/standalone/public
fi
