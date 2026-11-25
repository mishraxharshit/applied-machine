# Contributing

Thanks for helping. Small, focused pull requests are easiest to review.

## Setup
```bash
bash scripts/doctor.sh     # see what you have
make install            # venv + builds
make test
```

## Workflow
1. Open an issue first for anything big, so we agree on direction.
2. Fork, create a branch (`feat/importer-langfuse`), make your change.
3. Add or update tests. A change without a test is hard to trust.
4. Run `make test`. CI must be green.
5. Open a PR using the template.

## Style
- Python: type hints, small functions, errors that say what to fix.
- Go: `gofmt`, `go vet`. Rust: `cargo fmt`, `cargo clippy`.
- Commits: short imperative subject ("add langfuse importer").

## Licensing
By contributing you agree your work is licensed under Apache-2.0.
