# Roadmap

Honest list of known gaps. Items here are *not* shipped features.

- [ ] `ensure` for private repos: currently works (visibility is reported and
      preserved), but there is no integration test proving private stays
      private through the flow.
- [ ] Conflict detection: the audit step ("other workers own files in the
      tree") is still a manual checklist, not automated.
- [ ] Windows support: `ensure_checkout.sh` assumes a POSIX shell; the
      `verify` path is already cross-platform.
- [ ] PyPI release: install is currently `pip install git+https://...` only.
- [ ] `push` + remote-SHA verification as a CLI subcommand (currently done
      with `git push` + `git ls-remote`, per the workflow's ship step).
