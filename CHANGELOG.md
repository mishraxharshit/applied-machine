# Changelog
All notable changes go here. Format: Keep a Changelog; versions follow SemVer.

## [Unreleased]

## [0.1.1]
- tracetune: dedup now happens after scoring and keeps the best run per input (`--dedup best|none`)
- tracecore: only drops invalid lines and exact duplicate lines
- scripts/demo.sh and `make demo`: 60-second Python-only demo
- toy agent for generating practice traces; docs and learn handbook
- website: browser playground and technical documentation (lectures 1 and 2)

## [0.1.0]
- tracetune: JSONL traces to scored, filtered chat-format dataset
- tracecore (Rust): streaming dedup
- ingest (Go): HTTP trace collector
- Astro website, Docker Compose, CI
