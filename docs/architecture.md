# Architecture

```
agent --HTTP--> ingest (Go) --> traces.jsonl --> tracecore (Rust) --> clean.jsonl
                                                                          |
        promote / reject <-- eval <-- training (TRL/verl/...) <-- tracetune (Python) --> dataset.jsonl
           [planned]        [planned]        [planned]               [v0.1]
```

## Components

| Component | Language | Job | Why this language |
|---|---|---|---|
| `services/ingest` | Go | receive traces over HTTP, append to JSONL | easy concurrency, single static binary |
| `crates/tracecore` | Rust | fast streaming cleanup of huge files | speed and low memory on multi-GB inputs |
| `packages/tracetune-py` | Python | score, filter, export training data | the ML ecosystem lives in Python |
| `apps/web` | Astro | public website | fast static pages on GitHub Pages |

## Principles
1. **Files are the interface.** Every stage reads and writes plain JSONL. Any stage can be replaced or run alone.
2. **Do not rewrite trainers.** We feed TRL, Unsloth, verl, SkyRL. We do not compete with them.
3. **Zero runtime dependencies where possible.** Easier to install, easier to trust.
4. **Fail loudly with a useful message.** Bad data makes bad models; say which line is wrong.
5. **Never train on private data by accident.** `data/` is git-ignored.

## Known limitations (v0.1)
- `tracecore` only removes invalid lines and exact duplicate lines. Smart dedup (best score per input) happens in tracetune.
- Only one trace per identical input is kept by default, which loses alternative good runs.
- Only single-tool traces have been tested.
