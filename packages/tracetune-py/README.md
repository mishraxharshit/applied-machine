# tracetune

> Turn your agent's production traces into a better model, safely, with open-source tooling.

**The problem.** Teams running LLM agents in production collect real traces every day
(user requests, tool calls, outcomes). That data could improve their model, but turning
traces into clean training data, scoring them, retraining and deploying safely is manual
and scattered. Most small teams never do it.

**What tracetune does.** An open-source pipeline for the whole loop:

```
traces (.jsonl) -> score + filter -> training dataset -> train (your tool) -> eval -> promote / reject
   [v0.1: done]      [v0.1: done]      [v0.1: done]        [planned]        [planned]   [planned]
```

It does not replace trainers like TRL, Unsloth, verl or SkyRL. It feeds them.

## Quickstart

```bash
pip install -e .
tracetune build --traces examples/sample_traces.jsonl --out out/dataset.jsonl
```

Output:

```
traces read : 8
kept        : 4  -> out/dataset.jsonl
dropped     : 4
  - low_score: 1
  - negative_feedback: 1
  - step_error: 1
  - trace_error: 1
```

## Trace format

One JSON object per line:

```json
{"trace_id": "t1", "input": "How many customers are in Delhi?",
 "steps": [{"name": "run_sql", "args": {"query": "..."}, "result": "42"}],
 "output": "There are 42 customers in Delhi.", "feedback": 1}
```

`feedback` is `1`, `-1` or omitted. `error` on a step or on the whole trace marks failures.

## How scoring works

Each trace gets a score: thumbs up/down, minus penalties for failed tool calls, failed runs
and wandering (too many steps). Traces below `--min-score` (default `0.0`) are dropped.
All weights are in `RewardConfig` (`src/tracetune/filters.py`).

## Roadmap

- [x] v0.1: JSONL traces -> scored, filtered chat-format dataset
- [ ] v0.2: importers for Langfuse and OpenTelemetry exports
- [ ] v0.3: LoRA training recipe on a small model + before/after eval report
- [ ] v0.4: promote / reject decision with regression checks

## Development

```bash
pip install -e ".[dev]"
pytest          # or: python -m unittest
```

## License

Apache-2.0 (see `LICENSE`).
