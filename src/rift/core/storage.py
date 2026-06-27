from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rift.core.errors import ProjectNotInitializedError


REQUIRED_SOURCE_FILES = ("objects.json", "permissions.json", "roles.json", "generator.json")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def template_dir(project: Path) -> Path:
    return project / ".template"


def objects_path(project: Path) -> Path:
    return template_dir(project) / "objects.json"


def permissions_path(project: Path) -> Path:
    return template_dir(project) / "permissions.json"


def roles_path(project: Path) -> Path:
    return template_dir(project) / "roles.json"


def generator_path(project: Path) -> Path:
    return template_dir(project) / "generator.json"


def is_initialized_project(project: Path) -> bool:
    source_dir = template_dir(project)
    if not source_dir.is_dir():
        return False
    return all((source_dir / filename).is_file() for filename in REQUIRED_SOURCE_FILES)


def ensure_initialized_project(project: Path) -> None:
    if not is_initialized_project(project):
        raise ProjectNotInitializedError(project)
