"""CLI tests: run the real entry point against real temp git repos."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from repo_first_class.cli import main


def make_repo(path: Path) -> str:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@e.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)
    (path / "f.txt").write_text("x\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=path, check=True)
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def test_cli_verify_in_sync(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    repo = tmp_path / "r"
    head = make_repo(repo)
    rc = main(["verify", str(repo), head])
    assert rc == 0
    assert "in_sync" in capsys.readouterr().out


def test_cli_verify_diverged_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    repo = tmp_path / "r"
    make_repo(repo)
    rc = main(["verify", str(repo), "0" * 40])
    assert rc == 2
    assert "diverged" in capsys.readouterr().out


def test_cli_where(capsys: pytest.CaptureFixture) -> None:
    rc = main(["where", "toxicwind/repo-first-class"])
    assert rc == 0
    assert "repo-first-class" in capsys.readouterr().out


def test_cli_version(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "repo-first-class" in capsys.readouterr().out


def test_module_entrypoint(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    head = make_repo(repo)
    proc = subprocess.run(
        [sys.executable, "-m", "repo_first_class", "verify", str(repo), head],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "in_sync" in proc.stdout
