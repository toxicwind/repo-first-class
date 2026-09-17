"""Checkout-state verification logic.

This is the Python heart of the workflow. The ``ensure`` path shells out to
the packaged ``ensure_checkout.sh`` (which needs ``gh`` + ``git``); the
``verify`` path is pure git and needs neither ``gh`` nor network access.

Statuses used throughout:

* ``in_sync``  — local HEAD == remote HEAD (the goal state)
* ``diverged``  — local HEAD != remote HEAD (needs a merge, not ff-only)
* ``dirty``     — uncommitted changes present (reported alongside the verdict)
* ``missing``   — destination is not a git checkout
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

# Matches the output format printed by ensure_checkout.sh
_LINE_RE = re.compile(r"^(VISIBILITY|BRANCH|LOCAL_HEAD|REMOTE_HEAD|IN_SYNC)=(.*)$")


@dataclass
class CheckoutState:
    """Parsed result of running ensure_checkout.sh."""

    visibility: str = ""
    branch: str = ""
    local_head: str = ""
    remote_head: str = ""
    dirty: list[str] = field(default_factory=list)
    in_sync: bool = False

    @property
    def diverged(self) -> bool:
        return bool(self.local_head and self.remote_head) and self.local_head != self.remote_head


@dataclass
class Verdict:
    """Pure-git verdict for a local checkout against a known remote SHA."""

    status: str  # in_sync | diverged | missing
    local_head: str = ""
    remote_head: str = ""
    dirty: list[str] = field(default_factory=list)

    def ok(self) -> bool:
        return self.status == "in_sync"


def parse_ensure_output(text: str) -> CheckoutState:
    """Parse the KEY=VALUE output of ensure_checkout.sh into a CheckoutState.

    The script prints a ``DIRTY:`` section with up to 5 ``git status --short``
    lines after it; everything after the ``DIRTY:`` marker is captured as
    dirty lines.
    """
    state = CheckoutState()
    in_dirty = False
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if in_dirty:
            if line.strip():
                state.dirty.append(line)
            continue
        if line.strip() == "DIRTY:":
            in_dirty = True
            continue
        m = _LINE_RE.match(line.strip())
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if key == "VISIBILITY":
            state.visibility = value
        elif key == "BRANCH":
            state.branch = value
        elif key == "LOCAL_HEAD":
            state.local_head = value
        elif key == "REMOTE_HEAD":
            state.remote_head = value
        elif key == "IN_SYNC":
            state.in_sync = value == "1"
    return state


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )


def git_head(dest: Path) -> str | None:
    """Local HEAD SHA of the checkout, or None if not a git repo."""
    dest = Path(dest)
    if not (dest / ".git").exists():
        return None
    proc = _git(["rev-parse", "HEAD"], dest)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def git_dirty(dest: Path) -> list[str]:
    """Uncommitted-change lines (``git status --short``), empty if clean."""
    dest = Path(dest)
    if not (dest / ".git").exists():
        return []
    proc = _git(["status", "--short"], dest)
    if proc.returncode != 0:
        return []
    return [ln for ln in proc.stdout.splitlines() if ln.strip()]


def verify_state(dest: str | Path, remote_sha: str) -> Verdict:
    """Pure-git verdict: is the checkout at ``dest`` sitting on ``remote_sha``?

    Needs no network and no ``gh`` — just git and a SHA you already trust
    (e.g. from ``git ls-remote origin <branch>``).
    """
    dest = Path(dest)
    local = git_head(dest)
    if local is None:
        return Verdict(status="missing", remote_head=remote_sha)
    dirty = git_dirty(dest)
    status = "in_sync" if local == remote_sha else "diverged"
    return Verdict(status=status, local_head=local, remote_head=remote_sha, dirty=dirty)


def ensure_checkout(repo: str, dest: str | Path) -> CheckoutState:
    """Run the packaged ensure_checkout.sh: clone if missing, ff-only pull if present.

    Requires ``gh`` (authenticated) and ``git`` on PATH. Raises
    FileNotFoundError if the shell script's prerequisites are absent, and
    RuntimeError with the script's stderr when it exits non-zero (divergence).
    """
    for tool in ("gh", "git"):
        if shutil.which(tool) is None:
            raise FileNotFoundError(f"ensure_checkout needs {tool!r} on PATH")
    script = resources.files("repo_first_class") / "data" / "ensure_checkout.sh"
    proc = subprocess.run(
        ["bash", str(script), repo, str(dest)],
        capture_output=True,
        text=True,
        check=False,
    )
    state = parse_ensure_output(proc.stdout)
    if proc.returncode != 0:
        raise RuntimeError(
            f"ensure_checkout.sh exited {proc.returncode}: {proc.stderr.strip() or 'diverged'}"
        )
    return state


def canonical_dest(name: str, base: str = "/home/toxic/projects") -> Path:
    """Canonical box path for a repo checkout: ``<base>/<name>``.

    ``name`` may be ``owner/repo`` or just ``repo``; only the repo part is used.
    """
    repo = name.split("/")[-1]
    return Path(base) / repo
