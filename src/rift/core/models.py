from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from rift.core.naming import ObjectNames, object_names, snake_case

FieldType = Literal["string", "integer", "float", "boolean", "datetime", "list[string]", "literal"]
ObjectScope = Literal["tenant", "system"]


@dataclass
class FieldDefinition:
    name: str
    type: FieldType = "string"
    required: bool = True
    default: Any = None
    description: str = ""
    validations: dict[str, Any] = field(default_factory=dict)
    create: bool = True
    update: bool = True
    response: bool = True
    separate_update: bool = False
    literals: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FieldDefinition":
        return cls(
            name=snake_case(str(data["name"])),
            type=data.get("type", "string"),
            required=bool(data.get("required", True)),
            default=data.get("default"),
            description=data.get("description", ""),
            validations=dict(data.get("validations", {})),
            create=bool(data.get("create", True)),
            update=bool(data.get("update", True)),
            response=bool(data.get("response", True)),
            separate_update=bool(data.get("separate_update", False)),
            literals=list(data.get("literals", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "default": self.default,
            "description": self.description,
            "validations": self.validations,
            "create": self.create,
            "update": self.update,
            "response": self.response,
            "separate_update": self.separate_update,
            "literals": self.literals,
        }


@dataclass
class ActionDefinition:
    name: str
    field: str | None = None
    value: Any = None
    own_scope: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActionDefinition":
        return cls(
            name=snake_case(str(data["name"])),
            field=snake_case(data["field"]) if data.get("field") else None,
            value=data.get("value"),
            own_scope=bool(data.get("own_scope", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "field": self.field, "value": self.value, "own_scope": self.own_scope}


@dataclass
class ObjectDefinition:
    name: str
    description: str = ""
    scope: ObjectScope = "tenant"
    owner_field: str = "created_by"
    fields: list[FieldDefinition] = field(default_factory=list)
    actions: list[ActionDefinition] = field(default_factory=list)
    names: ObjectNames = field(init=False)

    def __post_init__(self) -> None:
        self.name = snake_case(self.name)
        self.names = object_names(self.name)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ObjectDefinition":
        fields = [FieldDefinition.from_dict(item) for item in data.get("fields", [])]
        actions = [ActionDefinition.from_dict(item) for item in data.get("actions", [])]
        for field_def in fields:
            if field_def.separate_update and not any(action.field == field_def.name for action in actions):
                actions.append(ActionDefinition(name=f"set_{field_def.name}", field=field_def.name))
        return cls(
            name=str(data["name"]),
            description=data.get("description", ""),
            scope=data.get("scope", "tenant"),
            owner_field=data.get("owner_field", "created_by"),
            fields=fields,
            actions=actions,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "scope": self.scope,
            "owner_field": self.owner_field,
            "fields": [item.to_dict() for item in self.fields],
            "actions": [item.to_dict() for item in self.actions],
        }


def load_objects(data: dict[str, Any]) -> list[ObjectDefinition]:
    return [ObjectDefinition.from_dict(item) for item in data.get("objects", [])]
