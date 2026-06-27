from __future__ import annotations

import re
from dataclasses import dataclass


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def words(value: str) -> list[str]:
    tokens: list[str] = []
    for token in _TOKEN_RE.findall(value.replace("_", " ").replace("-", " ")):
        tokens.extend(re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", token))
    return [token.lower() for token in tokens if token]


def snake_case(value: str) -> str:
    result = "_".join(words(value))
    if not result:
        raise ValueError("Name cannot be empty.")
    if result[0].isdigit():
        result = f"_{result}"
    return result


def pascal_case(value: str) -> str:
    return "".join(part.capitalize() for part in words(value))


def pluralize(value: str) -> str:
    name = snake_case(value)
    if name.endswith("y") and (len(name) < 2 or name[-2] not in "aeiou"):
        return f"{name[:-1]}ies"
    if name.endswith(("s", "x", "z", "ch", "sh")):
        return f"{name}es"
    return f"{name}s"


def upper_snake(value: str) -> str:
    return snake_case(value).upper()


@dataclass(frozen=True)
class ObjectNames:
    raw: str
    snake: str
    pascal: str
    plural: str
    collection: str
    collection_const: str
    model: str
    create_schema: str
    update_schema: str
    response_schema: str
    filter_schema: str
    sort_schema: str
    ops: str


def object_names(name: str) -> ObjectNames:
    snake = snake_case(name)
    pascal = pascal_case(name)
    plural = pluralize(snake)
    return ObjectNames(
        raw=name,
        snake=snake,
        pascal=pascal,
        plural=plural,
        collection=plural,
        collection_const=upper_snake(plural),
        model=pascal,
        create_schema=pascal,
        update_schema=f"{pascal}Edit",
        response_schema=f"{pascal}Out",
        filter_schema=f"{pascal}Filter",
        sort_schema=f"{pascal}Sort",
        ops=f"{pascal}Ops",
    )
