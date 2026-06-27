from __future__ import annotations

import typer

from rift.core.naming import snake_case


def prompt_object_definition() -> dict:
    name = typer.prompt("Object name")
    description = typer.prompt("Description", default="")
    scope = typer.prompt("Scope", default="tenant")
    fields: list[dict] = []
    while True:
        field_name = typer.prompt("Field name (blank to finish)", default="")
        if not field_name:
            break
        field_type = typer.prompt("Field type", default="string")
        required = typer.confirm("Required?", default=True)
        separate_update = typer.confirm("Separate update/action endpoint?", default=False)
        fields.append(
            {
                "name": snake_case(field_name),
                "type": field_type,
                "required": required,
                "separate_update": separate_update,
            }
        )
    return {"name": snake_case(name), "description": description, "scope": scope, "fields": fields, "actions": []}
