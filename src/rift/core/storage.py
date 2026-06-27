from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
