---
layout: ../../layouts/Doc.astro
title: "Documentation"
---

# Applied Machine documentation

These pages teach the whole system from first principles. They are written like lectures: an idea, a picture, a worked example, then exercises. You do not need a degree or prior experience.

<p class="note">Every feature is marked <span class="tag ok">Implemented</span> (works today and is tested) or <span class="tag plan">Planned</span> (on the roadmap, not built). We never describe a planned feature as if it exists.</p>

## Start here

| Lecture | You will learn | Time |
|---|---|---|
| [1. The improvement loop](architecture/) | what problem we solve, and how the pieces fit | 20 min |
| [2. Scoring and dedup](scoring/) | how a trace becomes training data, and the bug that taught us to dedup after scoring | 25 min |

## Coming next

| Lecture | Status |
|---|---|
| The trace format | <span class="tag plan">Planned</span> |
| The Go collector (ingest) | <span class="tag plan">Planned</span> |
| Quickstart and how-to guides | <span class="tag plan">Planned</span> |
| API and CLI reference | <span class="tag plan">Planned</span> |
| Training, evaluation, safe release | <span class="tag plan">Planned</span>, after the features exist |

## How these docs stay correct

The version badge at the top comes from the package version. Every release updates the affected lectures in the same pull request as the code, and the release checklist in the repository (`docs/releasing.md`) makes that a required step. If you find a page that disagrees with the code, that is a bug: please open an issue.
