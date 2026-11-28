---
layout: ../../layouts/Doc.astro
title: "Scoring and deduplication"
---

# Scoring and deduplication

<p class="lead"><code>tracetune</code> gives each trace a numeric score, keeps the best run for each question, and exports the traces that meet a minimum score.</p>

## How scoring works

The score of a trace is the sum of the following signals.

| Signal | Points |
|---|---|
| Positive feedback (thumbs up) | +1.0 |
| Negative feedback (thumbs down) | −1.0 |
| Each failed tool call | −1.0 |
| The whole run failed | −2.0 |
| Each step beyond the third | −0.1 |

A trace without feedback scores 0 before penalties. The values are defaults defined in `RewardConfig` in `filters.py`.

## Selection pipeline

<pre class="mermaid">
flowchart TD
  A["All traces"] --> B["Score every trace"]
  B --> C["Group by identical input"]
  C --> D["Keep the best-scoring run per input"]
  C -->|"other runs"| G["Dropped: duplicate"]
  D --> E{"score at least min score?"}
  E -->|"yes"| F["Kept: exported to dataset"]
  E -->|"no"| H["Dropped: reason recorded"]
</pre>

The tool records a reason for every dropped trace: `duplicate`, `trace_error`, `negative_feedback`, `step_error`, or `low_score`. The command prints a count for each reason.

## Example

The sample file `examples/sample_traces.jsonl` has eight traces.

| Trace | Description | Score | Result |
|---|---|---|---|
| t1 | Thumbs up, one step | 1.0 | Kept |
| t2 | No feedback, one step | 0.0 | Kept |
| t3 | Thumbs up, one failed call, then success | 0.0 | Kept |
| t4 | Thumbs down | −1.0 | Dropped: `negative_feedback` |
| t5 | Whole run failed | −2.0 | Dropped: `trace_error` |
| t6 | Seven steps, no feedback | −0.4 | Dropped: `low_score` |
| t7 | Thumbs up, two steps | 1.0 | Kept |
| t8 | One failed call, no feedback | −1.0 | Dropped: `step_error` |

## Deduplication

Several traces can share the same input. By default, `tracetune` scores all traces first and keeps only the highest-scoring trace for each input. If two traces tie, it keeps the first one.

Deduplication runs after scoring because removing duplicates first can discard the best trace. The following results come from 60 generated traces (`--n 60 --seed 7`), which contain 9 distinct inputs.

| Method | Result |
|---|---|
| Score only, no deduplication | 41 traces kept |
| Deduplicate first, keeping the first trace per input, then score | 6 of 9 inputs kept |
| Score first, keep the best trace per input (default) | 9 of 9 inputs kept |

## Configure

| Option | Default | Description |
|---|---|---|
| `--min-score` | `0.0` | Keep only traces with a score at or above this value. |
| `--dedup best` | on | Keep the highest-scoring trace for each identical input. |
| `--dedup none` | off | Keep every trace, including duplicates. |

```bash
tracetune build --traces traces.jsonl --out dataset.jsonl --min-score 0.5
```

To change the point values, edit `RewardConfig` in `packages/tracetune-py/src/tracetune/filters.py`. The Python API is not stable yet.

## Limitations

- A trace without feedback scores 0 and is kept, even if its answer was wrong.
- An agent that fails once and then recovers scores lower than one that succeeds the first time.
- Keeping one trace per input discards other good approaches to the same question.

## What's next

- [How it works](../architecture/): the full pipeline around this stage.
- [Playground](../../playground/): try scoring on your own traces.
