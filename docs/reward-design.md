# Reward design

A reward function turns "was this run good?" into a number. tracetune keeps traces whose score is at least `--min-score` (default 0.0).

## Current rules (`filters.py`)
| Signal | Score |
|---|---|
| thumbs up | +1.0 |
| thumbs down | -1.0 |
| each failed tool call | -1.0 |
| whole run failed | -2.0 |
| each step beyond 3 | -0.1 |

All values are in `RewardConfig`.

## Honest weaknesses
- **Missing feedback is not the same as good.** A trace with no feedback scores 0 and is kept. Many such traces may be wrong answers nobody flagged.
- **Recovered errors are penalised.** An agent that fails once then fixes itself scores lower than one that got it right first time. That is intended, but debatable.
- **Feedback can be wrong or biased.** People click thumbs-down for reasons unrelated to quality.
- **Duplicates.** Several runs may share the same input. tracetune scores first, then keeps the best-scoring run per input (`--dedup best`, the default). Use `--dedup none` to keep every run. Tie-break: the first trace seen wins.

## How to tune
1. Generate data: `python3 examples/toy-agent/agent.py --n 200 --out data/toy.jsonl`.
2. Run `tracetune build` with different `--min-score` values and compare how many traces are kept and dropped, and why.
3. Read a sample of dropped and kept traces by hand. Reward design is mostly reading data.
