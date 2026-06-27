from __future__ import annotations

from rift.core.models import ObjectDefinition


BASE_ACTIONS = ("create", "read", "update", "delete")


def permission_key(object_name: str, action: str, scope: str) -> str:
    return f"{object_name}:{action}:{scope}"


def generate_permissions(objects: list[ObjectDefinition]) -> dict:
    catalog: dict[str, dict] = {"permissions": []}
    seen: set[str] = set()
    for obj in objects:
        scopes = ["system"] if obj.scope == "system" else ["any", "own"]
        for action in BASE_ACTIONS:
            for scope in scopes:
                if action == "create" and scope == "own":
                    continue
                key = permission_key(obj.name, action, scope)
                if key not in seen:
                    catalog["permissions"].append({"key": key, "object": obj.name, "action": action, "scope": scope})
                    seen.add(key)
        for action in obj.actions:
            for scope in scopes:
                key = permission_key(obj.name, action.name, scope)
                if key not in seen:
                    catalog["permissions"].append({"key": key, "object": obj.name, "action": action.name, "scope": scope})
                    seen.add(key)
    return catalog
