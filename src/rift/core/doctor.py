from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from rift.core.models import load_objects
from rift.core.storage import generator_path, is_initialized_project, objects_path, permissions_path, read_json, roles_path


@dataclass
class DoctorReport:
    ok: bool
    messages: list[str]


def run_doctor(project: Path) -> DoctorReport:
    if not is_initialized_project(project):
        return DoctorReport(
            ok=False,
            messages=[
                f"RIFT project is not initialized at {project}.",
                "Run `rift init <project_name>` first, or pass `--project` pointing to an initialized RIFT project.",
            ],
        )

    messages: list[str] = []
    errors = 0

    for path in [objects_path(project), permissions_path(project), roles_path(project), generator_path(project)]:
        if path.exists():
            messages.append(f"OK {path}")
        else:
            messages.append(f"ERROR missing {path}")
            errors += 1

    generator = read_json(generator_path(project), {})
    package_name = generator.get("package_name")
    if not package_name:
        messages.append("ERROR generator.json missing package_name")
        errors += 1

    objects = load_objects(read_json(objects_path(project), {"objects": []}))
    object_names = [obj.name for obj in objects]
    if len(object_names) != len(set(object_names)):
        messages.append("ERROR duplicate object names")
        errors += 1

    permissions = read_json(permissions_path(project), {"permissions": []})
    for permission in permissions.get("permissions", []):
        if not re.match(r"^[a-z_][a-z0-9_]*:[a-z_][a-z0-9_]*:(any|own|system)$", permission.get("key", "")):
            messages.append(f"ERROR invalid permission key {permission.get('key')}")
            errors += 1

    if package_name:
        for obj in objects:
            expected = [
                project / package_name / "api" / "base" / "models" / f"{obj.names.snake}_model.py",
                project / package_name / "api" / "base" / "operations" / f"{obj.names.snake}_ops.py",
                project / package_name / "api" / "base" / "routes" / f"{obj.names.snake}.py",
            ]
            for path in expected:
                if not path.exists():
                    messages.append(f"ERROR missing generated file {path}")
                    errors += 1
            ops_path = expected[1]
            if obj.scope == "tenant" and ops_path.exists():
                text = ops_path.read_text(encoding="utf-8")
                if "org_id" not in text:
                    messages.append(f"ERROR missing org_id enforcement marker in {ops_path}")
                    errors += 1
                if obj.owner_field not in text:
                    messages.append(f"ERROR missing ownership marker in {ops_path}")
                    errors += 1

    if errors == 0:
        messages.append("RIFT doctor passed.")
    return DoctorReport(ok=errors == 0, messages=messages)
