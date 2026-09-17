"""Real tests for checkout-state verification logic.

These build actual git repos in temp dirs (no gh, no network) and exercise
the parsing and verification code against them.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from repo_first_class import (
    canonical_dest,
    git_dirty,
    git_head,
    parse_ensure_output,
    verify_state,
)


def git(*args: str, cwd: Path) -> str:
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"
    return proc.stdout.strip()


@pytest.fixture()
def origin(tmp_path: Path) -> Path:
    """A real origin repo with one commit."""
    repo = tmp_path / "origin"
    repo.mkdir()
    git("init", "-q", cwd=repo)
    git("config", "user.email", "test@example.com", cwd=repo)
    git("config", "user.name", "test", cwd=repo)
    (repo / "README.md").write_text("# sample\n")
    git("add", ".", cwd=repo)
    git("commit", "-qm", "initial", cwd=repo)
    return repo


@pytest.fixture()
def clone(tmp_path: Path, origin: Path) -> Path:
    dest = tmp_path / "clone"
    git("clone", "-q", str(origin), str(dest), cwd=tmp_path)
    git("config", "user.email", "test@example.com", cwd=dest)
    git("config", "user.name", "test", cwd=dest)
    return dest


def test_parse_ensure_output_in_sync() -> None:
    text = (
        "VISIBILITY=public\n"
        "BRANCH=main\n"
        "LOCAL_HEAD=abc123\n"
        "REMOTE_HEAD=abc123\n"
        "IN_SYNC=1\n"
    )
    state = parse_ensure_output(text)
    assert state.visibility == "public"
    assert state.branch == "main"
    assert state.local_head == "abc123"
    assert state.remote_head == "abc123"
    assert state.in_sync is True
    assert state.diverged is False
    assert state.dirty == []


def test_parse_ensure_output_diverged_with_dirty() -> None:
    text = (
        "VISIBILITY=private\n"
        "BRANCH=main\n"
        "LOCAL_HEAD=abc123\n"
        "REMOTE_HEAD=def456\n"
        "DIRTY:\n"
        " M src/app.py\n"
        "?? notes.txt\n"
    )
    state = parse_ensure_output(text)
    assert state.in_sync is False
    assert state.diverged is True
    assert state.dirty == [" M src/app.py", "?? notes.txt"]


def test_verify_state_in_sync(clone: Path) -> None:
    head = git_head(clone)
    assert head
    verdict = verify_state(clone, head)
    assert verdict.status == "in_sync"
    assert verdict.ok()
    assert verdict.local_head == head


def test_verify_state_diverged(origin: Path, clone: Path) -> None:
    # New commit lands on origin; the clone is now behind.
    (origin / "CHANGELOG.md").write_text("# changes\n")
    git("add", ".", cwd=origin)
    git("commit", "-qm", "second", cwd=origin)
    remote_head = git("rev-parse", "HEAD", cwd=origin)

    verdict = verify_state(clone, remote_head)
    assert verdict.status == "diverged"
    assert not verdict.ok()
    assert verdict.local_head != remote_head


def test_verify_state_reports_dirty(clone: Path) -> None:
    (clone / "README.md").write_text("# modified\n")
    (clone / "scratch.txt").write_text("untracked\n")

    dirty = git_dirty(clone)
    assert any("README.md" in line for line in dirty)
    assert any("scratch.txt" in line for line in dirty)

    head = git_head(clone)
    assert head
    verdict = verify_state(clone, head)
    assert verdict.status == "in_sync"  # dirty does not change sync verdict
    assert len(verdict.dirty) == 2


def test_verify_state_missing(tmp_path: Path) -> None:
    verdict = verify_state(tmp_path / "nope", "abc123")
    assert verdict.status == "missing"
    assert not verdict.ok()


def test_canonical_dest() -> None:
    base = Path("/home/toxic/projects")
    assert canonical_dest("toxicwind/repo-first-class") == base / "repo-first-class"
    assert canonical_dest("repo-first-class") == base / "repo-first-class"
    assert canonical_dest("o/r", base="/tmp/x") == Path("/tmp/x/r")
