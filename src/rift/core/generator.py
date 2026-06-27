from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rift import __version__
from rift.core.git import git_dirty, init_git
from rift.core.models import ObjectDefinition, load_objects
from rift.core.naming import snake_case
from rift.core.permissions import generate_permissions
from rift.core.renderer import RenderResult, TemplateRenderer
from rift.core.removal import write_removal_guide
from rift.core.roles import generate_roles
from rift.core.storage import generator_path, objects_path, permissions_path, read_json, roles_path, write_json


@dataclass
class InitResult:
    target_dir: Path


def init_project(product_name: str, parent: Path, force: bool = False) -> InitResult:
    package_name = snake_case(product_name)
    target = parent / package_name
    if target.exists() and any(target.iterdir()) and not force:
        raise RuntimeError(f"Target directory is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)
    write_json(
        generator_path(target),
        {
            "project_name": product_name,
            "package_name": package_name,
            "generator_version": __version__,
            "last_generated_at": None,
            "safety": {"require_clean_git": True},
        },
    )
    write_json(objects_path(target), {"objects": []})
    write_json(permissions_path(target), {"permissions": []})
    write_json(roles_path(target), generate_roles({"permissions": []}))
    write_removal_guide(target)
    generate_project(target, force=True)
    init_git(target)
    return InitResult(target_dir=target)


def apply_object_file(project: Path, source: Path | dict[str, Any]) -> int:
    current = read_json(objects_path(project), {"objects": []})
    existing = {item["name"]: item for item in current.get("objects", [])}
    if isinstance(source, dict):
        incoming = [source]
    else:
        data = json.loads(source.read_text(encoding="utf-8"))
        incoming = data.get("objects", data if isinstance(data, list) else [data])
    for item in incoming:
        obj = ObjectDefinition.from_dict(item)
        existing[obj.name] = obj.to_dict()
    write_json(objects_path(project), {"objects": list(existing.values())})
    _refresh_catalogs(project)
    return len(incoming)


def generate_project(project: Path, dry_run: bool = False, force: bool = False) -> RenderResult:
    if not dry_run and not force and git_dirty(project):
        raise RuntimeError("Refusing to generate with uncommitted changes. Use --force to override.")
    objects = load_objects(read_json(objects_path(project), {"objects": []}))
    permissions_doc = generate_permissions(objects)
    roles_doc = generate_roles(permissions_doc)
    generator = read_json(generator_path(project), {})
    package_name = generator.get("package_name") or project.name
    context = {
        "project_name": generator.get("project_name", project.name),
        "package_name": package_name,
        "objects": objects,
        "permissions": permissions_doc.get("permissions", []),
        "roles": roles_doc.get("roles", []),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    renderer = TemplateRenderer()
    files = renderer.render_all(project, context)
    changed = renderer.preview_changes(files)
    if not dry_run:
        write_json(permissions_path(project), permissions_doc)
        write_json(roles_path(project), roles_doc)
        renderer.write(files)
        generator["last_generated_at"] = context["generated_at"]
        generator["generator_version"] = __version__
        write_json(generator_path(project), generator)
        write_removal_guide(project)
    return RenderResult(files=files, changed=changed)


def _refresh_catalogs(project: Path) -> None:
    objects = load_objects(read_json(objects_path(project), {"objects": []}))
    permissions = generate_permissions(objects)
    write_json(permissions_path(project), permissions)
    write_json(roles_path(project), generate_roles(permissions))
