#!/usr/bin/env bash
# One-command demo, Python only (no Go, Rust or Docker needed):
# toy agent makes 60 messy traces -> tracetune scores, dedups and exports a dataset.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data

python3 examples/toy-agent/agent.py --n 60 --seed 7 --out data/demo_traces.jsonl
echo
PYTHONPATH=packages/tracetune-py/src python3 -m tracetune.cli build \
  --traces data/demo_traces.jsonl --out data/demo_dataset.jsonl
echo
echo "First training example (data/demo_dataset.jsonl):"
head -n 1 data/demo_dataset.jsonl
