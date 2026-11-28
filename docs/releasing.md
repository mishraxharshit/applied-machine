# Release checklist

Docs ship with the code. A release is not done until these are ticked.

- [ ] Bump `version` in `packages/tracetune-py/pyproject.toml` and `__version__` in `src/tracetune/__init__.py`. (The docs badge reads the pyproject version automatically.)
- [ ] Move the `[Unreleased]` notes in `CHANGELOG.md` under the new version.
- [ ] For every user-visible change, update the matching page in `apps/web/src/pages/docs/`.
- [ ] Any feature that is not built yet is marked **Planned**, never described as working.
- [ ] Add or update a diagram if the architecture changed.
- [ ] `make test` passes.
- [ ] `cd apps/web && npm run build` succeeds.
- [ ] Open a PR, merge, then tag: `git tag vX.Y.Z && git push --tags`.
