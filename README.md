# Applied Machine

Open-source tools that turn your AI agent's production traces into a better model.

> Working name. Early stage (v0.1). Collect, clean, score and export work today. Training, evaluation and safe release are on the roadmap.

## Try it in 60 seconds (Python only)

```bash
git clone https://github.com/YOUR-USERNAME/applied-machine
cd applied-machine
make demo
```

This generates 60 messy fake agent traces (retries, wrong answers, crashes), scores them, keeps the best run per question, and writes a training dataset to `data/demo_dataset.jsonl`.

## Use it on your own traces

Install the Python tool straight from GitHub (no PyPI yet):

```bash
pip install "git+https://github.com/YOUR-USERNAME/applied-machine#subdirectory=packages/tracetune-py"
tracetune build --traces my_traces.jsonl --out dataset.jsonl
```

Your traces must follow [the trace format](docs/trace-format.md) (one JSON object per line). Importers for Langfuse and OpenTelemetry exports are the next milestone (v0.2). Until then you need a small script to convert your data.

Useful flags:

| Flag | Meaning |
|---|---|
| `--min-score 0.5` | keep only traces scoring at least this (default 0.0) |
| `--dedup best` | keep the highest-scoring run per identical input (default) |
| `--dedup none` | keep every run, duplicates included |

## How it fits together

```
agent --> ingest (Go) --> tracecore (Rust) --> tracetune (Python) --> dataset --> train --> eval --> promote
                                                [works today]         [roadmap: train, eval, promote]
```

| Path | Language | Role |
|---|---|---|
| `packages/tracetune-py` | Python | score, filter, dedup, export training data |
| `crates/tracecore` | Rust | fast cleanup of huge files (invalid and exact-duplicate lines) |
| `services/ingest` | Go | HTTP collector for traces |
| `examples/toy-agent` | Python | generates practice traces |
| `apps/web` | Astro | project website |

## Full local stack

```bash
bash scripts/doctor.sh     # which tools you have
make test                  # Python, Go and Rust checks
make up                    # docker compose: collector on :8080
```

Send a trace:

```bash
curl -i -X POST localhost:8080/v1/traces -d '{"trace_id":"a","input":"hi","output":"hello"}'
```

## New here?

Read the [learn handbook](docs/learn/README.md). It explains everything from zero, and you do not need a degree or experience. See also [CONTRIBUTING.md](CONTRIBUTING.md).

## Roadmap

- [x] v0.1: traces to scored, deduplicated, chat-format dataset
- [ ] v0.2: Langfuse and OpenTelemetry importers
- [ ] v0.3: LoRA training recipe on a small model, with before/after report
- [ ] v0.4: promote or reject with regression checks

License: Apache-2.0.
