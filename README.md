# RIFT

RIFT is an opinionated FastAPI backend generator for building structured, multi-tenant MongoDB APIs from JSON source-of-truth files.

RIFT is strict on purpose. It generates one consistent backend style with configuration, async PyMongo database access, auth scaffolding, tenancy, RBAC, generated models, operation classes, route modules, Docker support, and repeatable regeneration.

Generated routes check permissions. Generated operations enforce tenancy and ownership.

## Features

- FastAPI backend project generation
- Async PyMongo database access
- `uv` based generated projects
- Dockerfile and Docker Compose generation
- Optional local MongoDB Compose service with a named volume
- Root `main.py` app entrypoint plus packaged `<project>/api/main.py`
- Source-of-truth JSON files under `.template/`
- Object model, operation, and route generation
- Object updates through repeated JSON apply + regenerate
- Tenant-scoped filtering through `org_id`
- Own versus any permission scopes
- Separate action endpoints for workflow fields such as `status`
- In-memory RBAC cache scaffold
- First admin/system organization seeding from environment variables
- Git-aware generation safety
- Dry-run, diff, doctor, and manual removal guide commands

## Package Name

The PyPI package is intended to be published as `rift-backend` because `rift` is already used by another project on PyPI.

The installed console command is still:

```powershell
rift
```

## Requirements

For using the generator:

- Python 3.12+
- `pipx` recommended for global CLI installation

For running generated projects:

- Python 3.12+
- `uv`
- MongoDB, either local/external or generated through Docker Compose
- Docker and Docker Compose, if using generated containers

## Installation

Install from PyPI after release:

```powershell
pipx install rift-backend
```

Install directly from GitHub:

```powershell
pipx install "git+https://github.com/JRudransh/RIFT.git"
```

Install locally while developing RIFT:

```powershell
git clone https://github.com/JRudransh/RIFT.git
cd RIFT
pipx install --editable .
```

Or run from the repository without installing:

```powershell
$env:PYTHONPATH = "src"
python -m rift.cli --help
```

## Quick Start

Create a generated backend project:

```powershell
rift init Hotel Admin
```

For scripts, avoid the interactive MongoDB prompt:

```powershell
rift init Hotel Admin --include-mongodb
rift init Hotel Admin --no-include-mongodb
```

Move into the generated project:

```powershell
cd hotel_admin
```

Install generated project dependencies:

```powershell
uv sync
```

Create a `.env` file or use environment variables. The generated `.env.example` shows all required keys:

```powershell
DEV_MODE=true
MONGO_URI=mongodb://localhost:27017
BASE_DB_NAME=hotel_admin
JWT_SECRET=change_me
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change_me_admin_password
ADMIN_NAME=Admin
```

Run the generated API locally:

```powershell
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Open the docs:

```text
http://127.0.0.1:8000/
```

## Docker Usage

If you initialized with MongoDB support:

```powershell
rift init Hotel Admin --include-mongodb
cd hotel_admin
docker compose up --build
```

The generated Compose file includes:

- API service exposed on `9000:8000`
- MongoDB service using `mongo:7`
- MongoDB named volume `mongo_data:/data/db`
- MongoDB host port `${MONGO_PORT:-27017}:27017`

If port `27017` is already used locally, choose another host port:

```powershell
$env:MONGO_PORT = "28017"
docker compose up --build
```

The API service talks to MongoDB inside Compose through:

```text
mongodb://mongo:27017
```

`.env` is optional in the generated Compose file. `.env.example` is always included.

## CLI Commands

### `rift init`

Create a new generated backend project.

```powershell
rift init <project_name>
```

Options:

```powershell
rift init Hotel Admin --output C:\projects
rift init Hotel Admin --force
rift init Hotel Admin --include-mongodb
rift init Hotel Admin --no-include-mongodb
```

What it does:

- Creates a new project folder using a normalized snake_case package name
- Writes `.template/` source files
- Generates backend files
- Generates Docker and `uv` project files
- Initializes Git in the generated project when possible

### `rift object add`

Interactively add or replace one object definition in an initialized RIFT project.

```powershell
rift object add --project C:\projects\hotel_admin
```

This updates `.template/objects.json`. Run `rift generate` afterward to regenerate backend files.

### `rift object apply`

Apply object definitions from JSON.

```powershell
rift object apply objects.json --project C:\projects\hotel_admin
```

The JSON file can contain a single object:

```json
{
  "name": "Room",
  "description": "Hotel room inventory",
  "scope": "tenant",
  "fields": [
    {"name": "number", "type": "string", "required": true},
    {"name": "floor", "type": "integer", "required": true},
    {"name": "nightly_rate", "type": "float", "required": true},
    {"name": "available", "type": "boolean", "required": false},
    {"name": "status", "type": "literal", "required": true, "separate_update": true}
  ]
}
```

Or multiple objects:

```json
{
  "objects": [
    {
      "name": "Guest Profile",
      "scope": "tenant",
      "fields": [
        {"name": "full_name", "type": "string", "required": true},
        {"name": "email", "type": "string", "required": true},
        {"name": "vip", "type": "boolean", "required": false}
      ]
    },
    {
      "name": "Booking",
      "scope": "tenant",
      "fields": [
        {"name": "guest_id", "type": "string", "required": true},
        {"name": "room_id", "type": "string", "required": true},
        {"name": "check_in", "type": "datetime", "required": true},
        {"name": "check_out", "type": "datetime", "required": true},
        {"name": "total_amount", "type": "float", "required": true},
        {"name": "status", "type": "literal", "required": true, "separate_update": true}
      ]
    }
  ]
}
```

Applying an object with the same normalized name replaces the existing source-of-truth definition. This is how existing generated object schemas are changed.

### `rift generate`

Generate backend files from `.template/*.json`.

```powershell
rift generate --project C:\projects\hotel_admin
```

Safety behavior:

- Refuses to generate in an uninitialized folder
- Refuses to overwrite a dirty Git worktree unless `--force` is used

Options:

```powershell
rift generate --project C:\projects\hotel_admin --dry-run
rift generate --project C:\projects\hotel_admin --force
```

### `rift diff`

Preview generated changes without writing files.

```powershell
rift diff --project C:\projects\hotel_admin
```

### `rift doctor`

Validate project health.

```powershell
rift doctor --project C:\projects\hotel_admin
```

Checks include:

- Required `.template` files exist
- Generator metadata is present
- Permission key format is valid
- Generated model, operation, and route files exist for configured objects
- Tenant-scoped operation files contain tenancy and ownership markers

If run outside an initialized RIFT project, it prints an initialize-first message instead of treating the folder as a broken project.

### `rift removal-guide`

Write the manual generated-object removal guide.

```powershell
rift removal-guide --project C:\projects\hotel_admin
```

RIFT does not automatically delete generated object files. The guide explains what to review manually when removing an object.

## Generated Project Structure

A generated project uses this layout:

```text
hotel_admin/
  main.py
  pyproject.toml
  uv.lock
  Dockerfile
  docker-compose.yml
  .dockerignore
  .env.example

  .template/
    objects.json
    permissions.json
    roles.json
    generator.json
    removal.md

  hotel_admin/
    __init__.py
    api/
      __init__.py
      config.py
      consts.py
      database.py
      main.py
      middleware.py
      security.py
      base/
        models/
        operations/
        routes/
        exceptions/
```

The root `main.py` re-exports the FastAPI app from the packaged app module:

```python
from hotel_admin.api.main import app
```

## Object Schema Reference

Object fields support:

- `name`: field name, normalized to snake_case
- `type`: field type
- `required`: whether the field is required
- `default`: optional default value
- `description`: optional description
- `validations`: reserved for validation metadata
- `create`: include in create schema
- `update`: include in update schema
- `response`: include in response schema
- `separate_update`: generate a dedicated action endpoint
- `literals`: optional literal values metadata

Supported field types:

- `string`
- `integer`
- `float`
- `boolean`
- `datetime`
- `list[string]`
- `literal`

Object-level keys:

- `name`
- `description`
- `scope`: `tenant` or `system`
- `owner_field`: defaults to `created_by`
- `fields`
- `actions`

Example custom actions:

```json
{
  "name": "Room",
  "scope": "tenant",
  "fields": [
    {"name": "status", "type": "literal", "required": true, "separate_update": true}
  ],
  "actions": [
    {"name": "mark_clean", "field": "status", "value": "clean"},
    {"name": "mark_maintenance", "field": "status", "value": "maintenance"}
  ]
}
```

Generated routes include endpoints such as:

```text
POST /rooms/{item_id}/set_status/
POST /rooms/{item_id}/mark_clean/
POST /rooms/{item_id}/mark_maintenance/
```

## Updating Existing Objects

To update an existing object, apply a JSON definition with the same object name and regenerate:

```powershell
rift object apply room-v2.json --project C:\projects\hotel_admin
rift generate --project C:\projects\hotel_admin --force
```

RIFT replaces the source-of-truth object entry and regenerates the object model, operations, routes, permissions, and route registration.

## Generation Safety

RIFT generation is intentionally conservative:

- Generated projects are initialized as Git repositories when possible
- `rift generate` checks for uncommitted changes
- Use `--dry-run` to preview planned output
- Use `rift diff` to inspect generated changes
- Use `--force` only when you intentionally want to overwrite generated files
- Object removal is manual through `rift removal-guide`

## Runtime Notes

Generated projects use:

- FastAPI
- Uvicorn
- async PyMongo
- Pydantic v2
- python-decouple
- loguru
- pwdlib with Argon2 support
- PyJWT
- Docker Compose with optional MongoDB

The generated app seeds the first admin/system organization from:

```text
ADMIN_EMAIL
ADMIN_PASSWORD
ADMIN_NAME
```

## Development

Install development dependencies:

```powershell
uv sync --extra dev
```

Run tests:

```powershell
python -m pytest
```

Run the CLI from source:

```powershell
$env:PYTHONPATH = "src"
python -m rift.cli --help
```

Build generated test projects manually:

```powershell
rift init Runtime Test --include-mongodb
cd runtime_test
uv sync
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

## Publishing To PyPI

The package is prepared to publish as `rift-backend` with the console command `rift`.

Before publishing:

1. Confirm the version in `pyproject.toml`.
2. Confirm `README.md` renders correctly on PyPI.
3. Confirm the package name is available or owned by you.
4. Run tests.
5. Build the package.
6. Upload to TestPyPI first.
7. Upload to PyPI.

Install build tools:

```powershell
uv tool install build
uv tool install twine
```

Build:

```powershell
python -m build
```

Check package metadata:

```powershell
twine check dist/*
```

Upload to TestPyPI:

```powershell
twine upload --repository testpypi dist/*
```

Install from TestPyPI:

```powershell
pipx install --index-url https://test.pypi.org/simple/ --pip-args="--extra-index-url https://pypi.org/simple" rift-backend
```

Upload to PyPI:

```powershell
twine upload dist/*
```

Install from PyPI:

```powershell
pipx install rift-backend
```

## Current Limitations

- No frontend/admin UI generation
- No Redis RBAC cache yet
- No migration engine yet
- No automatic generated-object deletion
- No generated test suite inside generated projects yet
- Interactive `rift object add` is basic; JSON apply is recommended for repeatable work

## Project Identity

RIFT is a strict, JSON-driven, RBAC-first, multi-tenant FastAPI and MongoDB backend generator.
