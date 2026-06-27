import json
from pathlib import Path

from rift.core.doctor import run_doctor
from rift.core.generator import apply_object_file, generate_project, init_project


def test_init_generates_project_structure(tmp_path: Path):
    result = init_project("Hotel Admin", tmp_path, force=False)
    root = result.target_dir
    assert (root / "hotel_admin" / "api" / "main.py").exists()
    assert (root / "hotel_admin" / "api" / "database.py").exists()
    assert (root / "Dockerfile").exists()
    assert (root / "docker-compose.yml").exists()
    assert (root / "pyproject.toml").exists()
    assert not (root / "requirements.txt").exists()
    database = (root / "hotel_admin" / "api" / "database.py").read_text(encoding="utf-8")
    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
    backend_pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "from pymongo import AsyncMongoClient" in database
    assert "motor" not in database.lower()
    assert "uv sync --no-dev" in dockerfile
    assert '"pymongo>=4.11.0"' in backend_pyproject


def test_apply_object_generates_object_files_and_catalogs(tmp_path: Path):
    root = init_project("Hotel Admin", tmp_path, force=False).target_dir
    obj_file = tmp_path / "object.json"
    obj_file.write_text(
        json.dumps(
            {
                "name": "Room",
                "description": "Hotel room",
                "scope": "tenant",
                "fields": [
                    {"name": "number", "type": "string", "required": True},
                    {"name": "status", "type": "literal", "required": True, "separate_update": True},
                ],
            }
        ),
        encoding="utf-8",
    )
    assert apply_object_file(root, obj_file) == 1
    generate_project(root, force=True)
    assert (root / "hotel_admin" / "api" / "base" / "models" / "room_model.py").exists()
    assert (root / "hotel_admin" / "api" / "base" / "operations" / "room_ops.py").exists()
    assert (root / "hotel_admin" / "api" / "base" / "routes" / "room.py").exists()
    ops = (root / "hotel_admin" / "api" / "base" / "operations" / "room_ops.py").read_text(encoding="utf-8")
    route = (root / "hotel_admin" / "api" / "base" / "routes" / "room.py").read_text(encoding="utf-8")
    assert "org_id" in ops
    assert "created_by" in ops
    assert "require_any_or_own" in route
    assert "set_status" in route
    permissions = json.loads((root / ".template" / "permissions.json").read_text(encoding="utf-8"))
    keys = {item["key"] for item in permissions["permissions"]}
    assert "room:read:any" in keys
    assert "room:read:own" in keys
    assert "room:set_status:any" in keys


def test_dry_run_does_not_write_rendered_object_files(tmp_path: Path):
    root = init_project("Hotel Admin", tmp_path, force=False).target_dir
    objects_path = root / ".template" / "objects.json"
    objects_path.write_text(
        json.dumps({"objects": [{"name": "Invoice", "scope": "tenant", "fields": [{"name": "amount", "type": "float"}]}]}),
        encoding="utf-8",
    )
    result = generate_project(root, dry_run=True, force=True)
    assert result.files
    assert not (root / "hotel_admin" / "api" / "base" / "models" / "invoice_model.py").exists()


def test_doctor_passes_after_generation(tmp_path: Path):
    root = init_project("Hotel Admin", tmp_path, force=False).target_dir
    apply_object_file(root, {"name": "Task", "scope": "tenant", "fields": [{"name": "title", "type": "string"}]})
    generate_project(root, force=True)
    report = run_doctor(root)
    assert report.ok, "\n".join(report.messages)
