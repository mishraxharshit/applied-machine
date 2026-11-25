# Applied Machine

Open-source tools that turn agent production traces into better models.

```
agent --> ingest (Go) --> tracecore (Rust) --> tracetune (Python) --> train --> eval --> promote
```

| Path | Language | Role |
|---|---|---|
| `packages/tracetune-py` | Python | score, filter, export training data |
| `crates/tracecore` | Rust | fast streaming dedup of huge trace files |
| `services/ingest` | Go | HTTP collector for traces |
| `apps/web` | Astro | project website (GitHub Pages) |

## Run

```bash
make test        # needs python3, go, cargo
make up          # docker compose: ingest on :8080
make site        # website on localhost:4321
```

Send a trace:

```bash
curl -X POST localhost:8080/v1/traces -d '{"trace_id":"a","input":"hi","output":"hello"}'
```

License: Apache-2.0
