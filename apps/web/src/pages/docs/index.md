---
layout: ../../layouts/Doc.astro
title: "Applied Machine documentation"
---

# Applied Machine documentation

<p class="lead">Applied Machine is an open-source toolkit that turns the production traces of your AI agents into clean training data.</p>

A trace is the record of one agent run: the user's request, the tool calls the agent made, its final answer, and optional feedback. Applied Machine collects traces, scores them, removes duplicates, and exports a dataset you can use to improve your model.

## Product status

| Capability | Status |
|---|---|
| Collect traces over HTTP (Go service) | <span class="tag ok">Available</span> |
| Clean large trace files (Rust tool) | <span class="tag ok">Available</span> |
| Score, deduplicate, and export a dataset (Python tool) | <span class="tag ok">Available</span> |
| Import from Langfuse and OpenTelemetry | <span class="tag plan">Planned</span> |
| Train a model on the dataset | <span class="tag plan">Planned</span> |
| Evaluate a new model against the old one | <span class="tag plan">Planned</span> |
| Promote or reject a release | <span class="tag plan">Planned</span> |

<div class="callout caution"><strong>Early stage.</strong> Version 0.x. Interfaces can change between releases. Features marked Planned do not exist yet.</div>

## Documentation

| Page | Description |
|---|---|
| [How it works](architecture/) | The improvement loop, the components, and how data moves between them. |
| [Scoring and deduplication](scoring/) | How a trace becomes training data, how to tune it, and its limits. |
| [Playground](../playground/) | Paste your own traces and see the result in your browser. Nothing is uploaded. |

## Conventions

- **Available** means the feature works and has automated tests. **Planned** means it is on the roadmap and not built.
- Each release updates the affected pages in the same change as the code. The version at the top of every page is the version the page describes.
