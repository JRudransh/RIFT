from __future__ import annotations


def generate_roles(permissions: dict) -> dict:
    all_permissions = [item["key"] for item in permissions.get("permissions", [])]
    own_permissions = [key for key in all_permissions if key.endswith(":own") or ":create:" in key]
    read_permissions = [key for key in all_permissions if ":read:" in key]
    return {
        "roles": [
            {"name": "owner", "description": "Tenant owner with all permissions.", "allow": all_permissions, "deny": []},
            {"name": "member", "description": "Tenant member with own-record permissions.", "allow": own_permissions, "deny": []},
            {"name": "viewer", "description": "Read-only tenant member.", "allow": read_permissions, "deny": []},
        ]
    }
