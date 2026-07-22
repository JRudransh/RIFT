from __future__ import annotations

import difflib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, StrictUndefined


@dataclass
class RenderedFile:
    path: Path
    content: str


@dataclass
class RenderResult:
    files: list[RenderedFile]
    changed: list[str]


class TemplateRenderer:
    def __init__(self) -> None:
        self.env = Environment(
            loader=PackageLoader("rift", "templates"),
            trim_blocks=False,
            lstrip_blocks=False,
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )

    def render_all(self, target: Path, context: dict[str, Any]) -> list[RenderedFile]:
        rendered: list[RenderedFile] = []
        root = files("rift").joinpath("templates")
        for item in self._walk(root):
            if not item.is_file():
                continue
            rel = Path(str(item.relative_to(root)))
            template_name = rel.as_posix()
            template = self.env.get_template(template_name)
            if template_name.startswith("_object/"):
                for obj in context["objects"]:
                    item_context = {**context, "obj": obj}
                    output_rel = self._render_path(template_name.removeprefix("_object/"), item_context)
                    content = template.render(**item_context)
                    if output_rel.endswith(".j2"):
                        output_rel = output_rel[:-3]
                    rendered.append(RenderedFile(path=target / output_rel, content=content))
                continue
            output_rel = self._render_path(template_name, context)
            content = template.render(**context)
            if output_rel.endswith(".j2"):
                output_rel = output_rel[:-3]
            rendered.append(RenderedFile(path=target / output_rel, content=content))
        return rendered

    def preview_changes(self, files_to_write: list[RenderedFile]) -> list[str]:
        changes: list[str] = []
        for rendered in files_to_write:
            old = rendered.path.read_text(encoding="utf-8") if rendered.path.exists() else ""
            if old == rendered.content:
                continue
            if not rendered.path.exists():
                changes.append(f"A {rendered.path}")
                continue
            diff = difflib.unified_diff(
                old.splitlines(),
                rendered.content.splitlines(),
                fromfile=str(rendered.path),
                tofile=f"{rendered.path} (generated)",
                lineterm="",
            )
            changes.extend(diff)
        return changes

    def write(self, files_to_write: list[RenderedFile]) -> None:
        for rendered in files_to_write:
            rendered.path.parent.mkdir(parents=True, exist_ok=True)
            rendered.path.write_text(rendered.content, encoding="utf-8")

    def _render_path(self, template_name: str, context: dict[str, Any]) -> str:
        return self.env.from_string(template_name).render(**context)

    def _walk(self, root: Any) -> list[Any]:
        items: list[Any] = []
        for child in root.iterdir():
            if child.is_dir():
                items.extend(self._walk(child))
            else:
                items.append(child)
        return items

