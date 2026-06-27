from __future__ import annotations

from pathlib import Path

from rift.core.models import load_objects
from rift.core.storage import objects_path, read_json


def removal_markdown(project: Path) -> str:
    objects = load_objects(read_json(objects_path(project), {"objects": []}))
    lines = [
        "# RIFT Manual Removal Guide",
        "",
        "RIFT does not automatically remove generated object files.",
        "Review these files and JSON entries before deleting anything.",
        "",
    ]
    for obj in objects:
        lines.extend(
            [
                f"## {obj.names.pascal}",
                "",
                f"- Remove `{obj.name}` from `.template/objects.json`.",
                f"- Review permissions for `{obj.name}:*:*` in `.template/permissions.json`.",
                f"- Review role mappings in `.template/roles.json`.",
                f"- Review `{obj.names.snake}_model.py`, `{obj.names.snake}_ops.py`, and `{obj.names.snake}.py`.",
                "- Review route registration in generated `main.py`.",
                "",
            ]
        )
    return "\n".join(lines)


def write_removal_guide(project: Path) -> Path:
    path = project / ".template" / "removal.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(removal_markdown(project), encoding="utf-8")
    return path
