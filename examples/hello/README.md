# hello example

A runnable end-to-end demo of the repo-first-class workflow on a scratch
sample repo. Fully offline — no GitHub account needed.

```bash
pip install git+https://github.com/toxicwind/repo-first-class.git
bash examples/hello/polish_sample.sh
```

What it does:

1. Creates a tiny sample repo in a unique temp dir (`hello.py` only).
2. Shows it failing the first-class checklist (no README, no LICENSE, ...).
3. Polishes it: README, LICENSE, `.gitignore`.
4. Verifies checkout state with `repo-first-class verify` — `in_sync`.
5. Adds a commit and verifies against the old SHA — `diverged` (exit 2),
   proving the detector actually detects.
6. Shows `repo-first-class where` resolving a canonical box path.

The script cleans up its scratch dir on exit.
