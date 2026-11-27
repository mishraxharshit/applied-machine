# Failures and wins

Our honest log. Newest entries go at the top of each section. Add yours with [TEMPLATE-lesson.md](TEMPLATE-lesson.md).

Rule: no blame. A mistake that is written down is a gift to the next person.

## Wins

### The whole chain ran on a laptop
**Date:** 2026-11-25
We sent two traces through the Go collector, cleaned them with the Rust tool, and exported a dataset with the Python tool. Numbers matched the plan: `read 4, kept 1, dropped 3`, then one dataset row with score 1.0.
**Lesson:** a small end-to-end run, even with fake data, proves the design before you add anything big.

### All checks green on the first real machine run
Python tests (7), `go vet`, and `cargo check` all passed on a normal Linux (WSL) setup. This code had been written in an environment that could only run Python, so seeing Go and Rust compile was a real test.
**Lesson:** code is only "working" once it runs somewhere other than where it was written.

### A 4 GB laptop GPU is enough for this stage
Collecting, cleaning, scoring, and exporting are CPU work. Heavy training is the only part that needs a bigger GPU, and it can run on free cloud notebooks.
**Lesson:** design the project so the beginner's laptop can do most of the work.

## Failures and surprises

### Dedup before scoring can throw away the best run  (surprise)
**Type:** surprise | **Status:** fixed
**What happened:** 60 toy traces (`--n 60 --seed 7`) contained only 9 unique inputs. `tracecore` deduped by input and kept the first one, so a bad early run could hide a good later run of the same question.
**The numbers:**

| Method | Result |
|---|---|
| A) `tracetune` directly on all 60 | 41 kept |
| B) dedup first (first run per input), then score | 6 of 9 kept: 3 questions lost for no good reason |
| C) score first, keep the best run per input | 9 of 9 kept |

**Why:** cleanup ran before scoring, so it did not know which duplicate was best.
**What we did:** added `best_per_input` in `filters.py` (dedup after scoring, ties keep the first), a `--dedup best|none` flag, and tests. `tracecore` now only drops invalid lines and exact duplicate lines.
**Lesson:** before deleting data, ask what good data you might be deleting.

### The site build failed in 6 seconds
**Type:** failure | **Status:** fix applied, confirm in the Actions tab
**What happened:** the GitHub Pages workflow failed at the build step almost immediately.
**Most likely why:** the website had `package.json` but no `package-lock.json`. The environment that generated the repo had no internet, so it could not create the lockfile. That was a gap on our side, not the contributor's.
**What we did:** run `npm install` in `apps/web` and commit the lockfile.
**Lesson:** a build that fails in seconds usually fails in setup, not in your code. Open the red step and read the first error line. Lockfiles belong in the repo.

### Windows left `Zone.Identifier` files in the repo
**Type:** failure | **Status:** fixed
**What happened:** files named like `something:Zone.Identifier` appeared in WSL.
**Why:** Windows marks files downloaded from the internet with a hidden tag. WSL shows that tag as a separate file.
**What we did:** `find . -name "*:Zone.Identifier" -type f -delete`, and added `*:Zone.Identifier` to `.gitignore`.
**Lesson:** keep project files inside the Linux filesystem (`~/`), not under `/mnt/c`.

### A mystery folder named `{src`
**Type:** failure | **Status:** fixed
**What happened:** while generating the repo, one command created a folder literally called `{src` and skipped others.
**Why:** `mkdir -p a/{b,c}` relies on *brace expansion*, which bash does and plain `sh` does not. The command ran in `sh`.
**What we did:** deleted the junk folder, created directories explicitly, and checked the file tree.
**Lesson:** after a command that creates things, look at what it really created.

### Scripts lost their "executable" permission
**Type:** failure | **Status:** fixed
**What happened:** `./scripts/doctor.sh` said "Permission denied".
**Why:** zip files do not reliably keep the executable bit.
**What we did:** call scripts as `bash scripts/doctor.sh` everywhere.
**Lesson:** do not depend on invisible file permissions in something people download.

### `cat: data/traces.jsonl: No such file or directory`
**Type:** failure | **Status:** fixed
**What happened:** the collector had saved the file correctly, but we looked for it from the wrong folder.
**Why:** relative paths depend on the folder you run the command from. The server ran in `services/ingest`, our `cat` ran somewhere else.
**What we did:** run `pwd`, then use the path from the repo root.
**Lesson:** when "file not found", check `pwd` first.

### Pasting output as if it were commands
**Type:** failure | **Status:** fixed
**What happened:** an old error line was pasted into the terminal and ran as a command (`Command 'cat:' not found`).
**Lesson:** copy only the commands you mean to run, never the output.

### `main` was protected, direct push refused
**Type:** surprise | **Status:** fixed
**What happened:** pushing to `main` was blocked by a branch ruleset.
**What we did:** work on a branch (`git checkout -b docs/...`), push it, open a pull request, merge.
**Lesson:** protected branches are a feature. They make every change reviewable and keep `main` working.

### The test tool was missing in the build environment
**Type:** surprise | **Status:** decision made
**What happened:** `pytest` was not installed where the code was written.
**What we did:** wrote tests with Python's built-in `unittest`, which pytest can also run.
**Lesson:** fewer dependencies means fewer things that can be missing. Zero runtime dependencies is a deliberate choice in this project.
