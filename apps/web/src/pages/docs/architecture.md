---
layout: ../../layouts/Doc.astro
title: "Lecture 1: The improvement loop"
---

# Lecture 1: The improvement loop

<p class="note">Written for v0.1.1. Steps up to the dataset are <span class="tag ok">Implemented</span>. Training, evaluation and release are <span class="tag plan">Planned</span>.</p>

## Learning objectives

After this lecture you can:

1. Explain what a **trace** is and why it is valuable.
2. Draw the continual improvement loop from memory.
3. Name each component, its language, and why that language was chosen.

## 1. The intuition

Hire a new employee. Every day they answer questions and keep a diary: what was asked, which tools they used, what they answered, and whether the customer was happy. Over months that diary shows exactly where they are strong and where they struggle.

An AI **agent** is that employee. Its diary entries are called **traces**. The idea behind this project is simple: *use the diary to coach the employee*, then check, honestly, that the coaching worked.

## 2. The loop

<pre class="mermaid">
flowchart LR
  A["Agent does its work"] --> B["Traces collected"]
  B --> C["Score and filter"]
  C --> D["Training dataset"]
  D -.-> E["Train the model"]
  E -.-> F["Evaluate on unseen tasks"]
  F -.-> G["Promote or reject"]
  G -.-> A
  classDef planned stroke-dasharray: 5 5,color:#8b91a8;
  class E,F,G planned
</pre>

Solid arrows exist today. Dashed boxes are planned. The loop repeats: each pass should leave the agent a little better, and the *evaluate* step is what stops us from fooling ourselves.

## 3. The system, component by component

<pre class="mermaid">
flowchart LR
  A["Your agent"] -->|"HTTP POST"| B["ingest (Go)"]
  B --> C[("traces.jsonl")]
  C --> D["tracecore (Rust)"]
  D --> E[("clean.jsonl")]
  E --> F["tracetune (Python)"]
  F --> G[("dataset.jsonl")]
</pre>

| Component | Language | Input | Output | Status |
|---|---|---|---|---|
| `ingest` | Go | HTTP requests with one trace each | appends lines to `traces.jsonl` | <span class="tag ok">Implemented</span> |
| `tracecore` | Rust | a JSONL file | the same file without invalid or exactly duplicated lines | <span class="tag ok">Implemented</span> |
| `tracetune` | Python | a JSONL file of traces | a scored, deduplicated training dataset | <span class="tag ok">Implemented</span> |
| trainer, evaluator, release gate | n/a | dataset | a better model, with evidence | <span class="tag plan">Planned</span> |

## 4. Design principles

1. **Files are the interface.** Each stage reads and writes plain JSONL. You can run any stage alone, inspect its output with a text editor, or replace it.
2. **We feed trainers, we do not replace them.** Tools such as TRL, Unsloth, verl and SkyRL already train well. Our value is the data and the safety around them.
3. **Zero runtime dependencies in the Python tool.** Fewer things to install, fewer things to trust.
4. **Fail loudly and helpfully.** Bad data makes bad models, so errors name the file and the line.
5. **Private by default.** Traces can contain personal data, so the `data/` folder is never committed.

## 5. Why three languages?

An honest answer: each earns its place only if the job demands it.

- **Go** for the collector, because a network service needs easy concurrency and one deployable binary.
- **Rust** for cleaning very large files, because streaming with low memory matters once files reach gigabytes.
- **Python** for scoring and export, because the machine learning ecosystem lives there.

The cost is that contributors need more than one toolchain. That is why `scripts/doctor.sh` and Docker exist.

## Common mistakes

- Thinking the project trains models. It does not yet. It prepares the data.
- Assuming more data is always better. A small set of good traces beats a large set of noisy ones.

## Exercises

1. Run `make demo`. Which component produced `data/demo_dataset.jsonl`?
2. Why does each stage write a file instead of calling the next stage directly? Name one advantage and one disadvantage.
3. Sketch the loop for a different agent (for example a travel-booking assistant). What would a trace contain?

## Summary

A trace is an agent's diary entry. The loop turns traces into a dataset, then (in future versions) into a better model, verified before release. Today, everything up to the dataset works.

Next: [Lecture 2, Scoring and dedup](../scoring/).
