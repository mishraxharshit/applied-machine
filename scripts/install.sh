#!/usr/bin/env bash
# One-shot local setup on Linux: Python venv + tracetune, then build Go/Rust if present.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e "packages/tracetune-py[dev]"
echo "python: ok  (activate with: source .venv/bin/activate)"

if command -v go >/dev/null; then
  (cd services/ingest && go build -o ../../bin/ingest .) && echo "go: built bin/ingest"
else echo "go: skipped (not installed)"; fi

if command -v cargo >/dev/null; then
  (cd crates/tracecore && cargo build --release) && echo "rust: built crates/tracecore/target/release/tracecore"
else echo "rust: skipped (not installed)"; fi
