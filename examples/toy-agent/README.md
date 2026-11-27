# Toy agent

A rule-based text-to-SQL "agent" that generates realistic, messy traces (retries, wrong answers, crashes, wandering) with no model and no API key. Same `--seed` gives the same data.

```bash
python3 examples/toy-agent/agent.py --n 60 --out data/toy_traces.jsonl
python3 examples/toy-agent/agent.py --n 60 --ingest http://localhost:8080/v1/traces   # via the Go service
PYTHONPATH=packages/tracetune-py/src python3 -m tracetune.cli build --traces data/toy_traces.jsonl --out data/dataset.jsonl
```
