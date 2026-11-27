---
layout: ../../layouts/Doc.astro
title: "Lecture 2: Scoring and dedup"
---

# Lecture 2: Scoring traces and choosing training data

<p class="note">Written for v0.1.1. Everything on this page is <span class="tag ok">Implemented</span> in <code>packages/tracetune-py</code>.</p>

## Learning objectives

After this lecture you can:

1. Compute the score of a trace by hand.
2. Explain why deduplication must happen **after** scoring.
3. Name three weaknesses of the current scoring rules.

## 1. The intuition

A student keeps all their homework. To study well, they pick only the *best* attempt of each problem and ignore the sloppy ones. Scoring is how tracetune does the same: it gives every trace a number, then keeps the best.

## 2. The scoring rule

```
score = feedback_points
        - 1.0 x (number of failed tool calls)
        - 2.0 x (1 if the whole run failed, else 0)
        - 0.1 x max(0, number_of_steps - 3)
```

| Signal | Effect | Reason |
|---|---|---|
| thumbs up | +1.0 | a human liked it |
| thumbs down | -1.0 | a human did not |
| each failed tool call | -1.0 | mistakes are poor examples |
| whole run failed | -2.0 | crashes are never good examples |
| each step beyond 3 | -0.1 | prefer efficient agents |

These numbers are opinions, not laws. They live in `RewardConfig` so you can change them.

## 3. The selection pipeline

<pre class="mermaid">
flowchart TD
  A["All traces"] --> B["Score every trace"]
  B --> C["Group by identical input"]
  C --> D["Keep the best-scoring run per input"]
  C -->|"the other runs"| G["Dropped: duplicate"]
  D --> E{"score at least min score?"}
  E -->|"yes"| F["Kept: exported to dataset"]
  E -->|"no"| H["Dropped: reason recorded"]
</pre>

## 4. A worked example

Eight traces from `examples/sample_traces.jsonl`:

| Trace | What happened | Computation | Score | Result |
|---|---|---|---|---|
| t1 | thumbs up, 1 step | +1.0 | 1.0 | kept |
| t2 | no feedback, 1 step | 0 | 0.0 | kept |
| t3 | thumbs up, one failed call, then success | +1.0 - 1.0 | 0.0 | kept |
| t4 | thumbs down | -1.0 | -1.0 | dropped: negative_feedback |
| t5 | whole run crashed | -2.0 | -2.0 | dropped: trace_error |
| t6 | 7 steps, no feedback | -0.1 x 4 | -0.4 | dropped: low_score |
| t7 | thumbs up, 2 steps | +1.0 | 1.0 | kept |
| t8 | failed call, no feedback | -1.0 | -1.0 | dropped: step_error |

Four kept, four dropped. This is exactly what the test suite asserts.

## 5. The bug that taught us to dedup after scoring

Many runs share the same question. We first removed duplicates *before* scoring, keeping the first run of each question. On 60 generated traces (`--n 60 --seed 7`):

| Method | Result |
|---|---|
| A. score only, no dedup | 41 kept |
| B. dedup first (keep the first run), then score | 6 of 9 questions kept |
| C. score first, keep the best run per question | **9 of 9 questions kept** |

Method B threw away three questions for no good reason: a good run existed, but an earlier bad run had been kept instead. **Lesson: before deleting data, ask what good data you might be deleting.** Method C is the default (`--dedup best`); `--dedup none` keeps every run.

## 6. Honest weaknesses

- **No feedback looks neutral.** A trace nobody rated scores 0 and is kept, even if the answer was wrong.
- **Recovered mistakes are penalised.** An agent that fails once and then fixes itself scores below one that was right immediately. That is intended, but debatable.
- **One run per question.** Keeping only the best run discards other good approaches.

## Exercises

1. Compute the score of a trace with thumbs up, 5 steps, and one failed call. (Answer at the end.)
2. Set `positive_feedback` to 3.0 in `RewardConfig` and run the tests. Which fail, and why does that make sense?
3. Run `tracetune build` on the demo traces with `--min-score 0.5`. How many are kept? Is that better or worse, and why?

<details>
<summary>Answer to exercise 1</summary>

1.0 (thumbs up) - 1.0 (one failed call) - 0.1 x 2 (steps 4 and 5 are beyond the free 3) = -0.2. It would be dropped at the default minimum of 0.0.

</details>

## Summary

Score each trace, keep the best run per question, then apply a minimum score. Every drop has a recorded reason, so you can always see why data was removed.
