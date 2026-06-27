from __future__ import annotations

import subprocess
from pathlib import Path


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def git_dirty(path: Path) -> bool:
    if not is_git_repo(path):
        return False
    result = subprocess.run(["git", "status", "--short"], cwd=path, capture_output=True, text=True, check=False)
    return bool(result.stdout.strip())


def init_git(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True, text=True, check=False)
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True, text=True, check=False)
    subprocess.run(["git", "commit", "-m", "Initial RIFT generated project"], cwd=path, capture_output=True, text=True, check=False)
