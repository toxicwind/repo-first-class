# Design

How repo-first-class is put together, and why.

## Two layers

| Layer | Lives in | Needs | Purpose |
|---|---|---|---|
| `ensure` | `src/repo_first_class/data/ensure_checkout.sh` | `gh` (authed) + `git` + network | Clone-if-missing, `git pull --ff-only` if present, print `VISIBILITY/BRANCH/LOCAL_HEAD/REMOTE_HEAD`, exit non-zero on divergence |
| `verify` | `src/repo_first_class/checkout.py` | `git` only | Compare a local checkout's HEAD against a known remote SHA — no network, no `gh` |

The shell script is the original workflow artifact, shipped verbatim as
packaged data and invoked by `ensure_checkout()` in `checkout.py`. The Python
layer adds parsing (`parse_ensure_output`), a pure-git verifier
(`verify_state`), and the CLI. Nothing in the Python layer reimplements the
shell script's clone/pull logic — it wraps it honestly.

## Why the shell script stays a shell script

The original script is battle-tested in daily use and trivially auditable at
~40 lines. Porting its `gh` interactions to Python would add a dependency
(`gh` is already required as a binary either way) and a second place to keep
in sync with `gh`'s CLI surface. The wrapper is the smaller lie.

## Verdict semantics

`verify_state(dest, remote_sha)` returns one of:

- `in_sync` — local HEAD equals the remote SHA. The goal state.
- `diverged` — local HEAD differs. Needs a merge, not ff-only.
- `missing` — `dest` is not a git checkout.

A dirty working tree is reported alongside the verdict but never changes it —
exactly like the shell script, which prints `DIRTY:` lines separately.

## Exit codes

`repo-first-class verify` exits `0` on in_sync, `2` on diverged/missing,
`1` on usage errors. `ensure` exits `2` when the script reports divergence,
matching the script's own convention.
