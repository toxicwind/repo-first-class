# repo-first-class

[![CI](https://github.com/toxicwind/repo-first-class/actions/workflows/ci.yml/badge.svg)](https://github.com/toxicwind/repo-first-class/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Make any GitHub repo **first-class**: a canonical, current checkout, maximally
polished — README, docs, committed, pushed, remote SHA verified.

One job: `owner/repo` → verified checkout → polished tree → committed →
pushed → remote SHA verified. Nothing in this README is aspirational; every
claim below is exercised by the test suite or the runnable example.

## 30-second quickstart

```bash
pip install git+https://github.com/toxicwind/repo-first-class.git

# 1. Ensure a repo is checked out at its canonical path (needs `gh` auth):
repo-first-class ensure toxicwind/repo-first-class
# visibility : public
# branch     : main
# local_head : 9f2c...
# remote_head: 9f2c...
# in_sync    : True

# 2. Or verify any local checkout against a known SHA — no network, no `gh`:
repo-first-class verify /home/toxic/projects/repo-first-class 9f2c...

# 3. Where does a repo belong on this box?
repo-first-class where toxicwind/repo-first-class
# /home/toxic/projects/repo-first-class
```

No GitHub account handy? Watch the whole workflow run on a scratch repo,
fully offline:

```bash
bash examples/hello/polish_sample.sh
```

It builds a tiny sample repo, shows it failing the first-class checklist,
polishes it (README, LICENSE, `.gitignore`), verifies `in_sync`, then
deliberately diverges it to prove the detector detects.

## The workflow

1. **Resolve.** `gh repo view <owner>/<repo>` — record visibility (private
   stays private) and the default branch.
2. **Checkout.** Clone if missing, `git pull --ff-only` if present, at the
   canonical path. Never switch branches inside a shared clone — unique
   worktrees and scratch dirs only.
3. **Audit.** Compare local HEAD to the remote HEAD; surface dirty files.
4. **Polish** (patch-forward only): README, `docs/`, sane `.gitignore`,
   no secrets anywhere. Known gaps go in `docs/ROADMAP.md` as roadmap
   items, never as shipped features.
5. **Ship.** Commit, push. If the branch diverged: preserve `origin/main`
   as `backup/<date>` first, merge forward — never force-push.
6. **Verify.** Remote HEAD must equal local HEAD. Report both.

## Layout

```
src/repo_first_class/
  checkout.py        # checkout-state verification logic (the heart)
  cli.py             # `repo-first-class` entry point
  data/ensure_checkout.sh   # original workflow script, shipped verbatim
tests/               # real tests: temp git repos, parsed output, CLI
examples/hello/      # runnable offline demo (polish_sample.sh)
docs/
  DESIGN.md          # two-layer architecture + verdict semantics
  ROADMAP.md         # known gaps, stated honestly
.github/workflows/  # CI: pytest + ruff on 3.9–3.12, plus the example
```

## Safety guarantees

- **Additive only.** The tool never deletes repos, branches, or uncommitted
  work. Divergence exits non-zero and asks for a merge — it never force-pushes.
- **No secrets.** Nothing here reads or writes credentials; `gh` owns auth.
- **Private stays private.** Visibility is reported on every `ensure` and the
  workflow never flips it.
- **Honest claims.** `docs/ROADMAP.md` lists what isn't done. The example and
  CI exist so the README can't drift from reality.

## Development

```bash
pip install -e . pytest ruff
pytest -q
ruff check .
bash examples/hello/polish_sample.sh
```

## License

MIT — see [LICENSE](LICENSE).
