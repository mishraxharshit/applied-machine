---
layout: ../../layouts/Doc.astro
title: "How it works"
---

# How it works

<p class="lead">Applied Machine turns agent traces into training data in four stages. Each stage reads and writes plain JSONL files.</p>

## The improvement loop

An agent produces traces as it works. Applied Machine selects the good traces and prepares them as training data. In a complete loop, you train on that data, evaluate the new model, and release it only if it is better.

<pre class="mermaid">
flowchart LR
  A["Agent runs"] --> B["Collect traces"]
  B --> C["Score and filter"]
  C --> D["Training dataset"]
  D -.-> E["Train"]
  E -.-> F["Evaluate"]
  F -.-> G["Promote or reject"]
  G -.-> A
  classDef planned stroke-dasharray: 5 5,color:#8b91a8;
  class E,F,G planned
</pre>

Solid arrows are <span class="tag ok">Available</span>. Dashed arrows are <span class="tag plan">Planned</span>.

## Components

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
| `ingest` | Go | One trace per HTTP request | Lines appended to `traces.jsonl` | <span class="tag ok">Available</span> |
| `tracecore` | Rust | A JSONL file | The same file without invalid or exactly duplicated lines | <span class="tag ok">Available</span> |
| `tracetune` | Python | A JSONL file of traces | A scored, deduplicated training dataset | <span class="tag ok">Available</span> |

You can run any component on its own. Each one only needs the file produced by the previous stage.

## Design principles

- **Files are the interface.** Stages communicate through JSONL files. You can inspect any intermediate file in a text editor or replace a stage with your own tool.
- **Use existing trainers.** Applied Machine prepares data for tools such as TRL, Unsloth, verl, and SkyRL. It does not replace them.
- **No runtime dependencies in the Python tool.** It runs on the Python standard library.
- **Errors name the file and line.** Invalid input is reported precisely instead of being skipped silently.
- **Data stays local.** The tools run on your machine. The repository never commits the `data/` folder.

## Choice of languages

| Language | Used for | Reason |
|---|---|---|
| Go | Collector service | Simple concurrency and a single deployable binary. |
| Rust | File cleaning | Low-memory streaming for files that reach gigabytes. |
| Python | Scoring and export | The machine learning ecosystem is Python-based. |

Working on all components requires Go, Rust, and Python. Run `bash scripts/doctor.sh` to check your environment, or use Docker.

## Limitations

- Applied Machine does not train models. It prepares the data.
- Traces must use the [trace format](https://github.com/mishraxharshit/applied-machine/blob/main/docs/trace-format.md). Importers for other formats are planned.

## What's next

- [Scoring and deduplication](../scoring/): how the `tracetune` stage chooses which traces to keep.
