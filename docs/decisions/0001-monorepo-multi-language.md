# 0001: One monorepo, several languages

**Status:** accepted

## Context
The project spans data collection, fast preprocessing, ML glue and a website. No single language is best at all four.

## Decision
Keep everything in one repository. Use Go for the network service, Rust for heavy file processing, Python for ML glue, Astro for the site. Stages communicate only through JSONL files and HTTP.

## Consequences
- (+) One place for schema, CI, docs and issues; changes land together.
- (+) Each part uses the right tool.
- (-) Contributors need more than one toolchain. `scripts/doctor.sh` shows what is missing; Docker covers the rest.
- (-) Schema changes must be made in every language that reads traces. Keep the format small and stable.

## Revisit when
A language adds more maintenance cost than value, or the components need separate release cycles.
