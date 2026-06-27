from __future__ import annotations

from pathlib import Path

import typer

from rift.core.doctor import run_doctor
from rift.core.generator import apply_object_file, generate_project, init_project
from rift.core.interactive import prompt_object_definition
from rift.core.removal import write_removal_guide

app = typer.Typer(help="RIFT backend generator.")
object_app = typer.Typer(help="Manage source-of-truth object definitions.")
app.add_typer(object_app, name="object")


@app.command()
def init(
    product_name: str = typer.Argument(..., help="Name of the generated backend project."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Parent output directory."),
    force: bool = typer.Option(False, "--force", help="Overwrite generated files when safe checks fail."),
) -> None:
    """Create a new RIFT backend project."""
    result = init_project(product_name=product_name, parent=output or Path.cwd(), force=force)
    typer.echo(f"Created RIFT project at {result.target_dir}")


@object_app.command("add")
def object_add(
    project: Path = typer.Option(Path.cwd(), "--project", "-p", help="Generated project root."),
) -> None:
    """Interactively add or replace an object definition."""
    definition = prompt_object_definition()
    apply_object_file(project, definition)
    typer.echo(f"Saved object definition: {definition['name']}")


@object_app.command("apply")
def object_apply(
    json_file: Path = typer.Argument(..., help="JSON object definition file."),
    project: Path = typer.Option(Path.cwd(), "--project", "-p", help="Generated project root."),
) -> None:
    """Apply object definitions from JSON."""
    count = apply_object_file(project, json_file)
    typer.echo(f"Applied {count} object definition(s)")


@app.command()
def generate(
    project: Path = typer.Option(Path.cwd(), "--project", "-p", help="Generated project root."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Render without writing files."),
    force: bool = typer.Option(False, "--force", help="Generate even when the git worktree is dirty."),
) -> None:
    """Generate backend files from source-of-truth JSON."""
    result = generate_project(project, dry_run=dry_run, force=force)
    prefix = "Would write" if dry_run else "Wrote"
    typer.echo(f"{prefix} {len(result.files)} file(s)")


@app.command()
def diff(
    project: Path = typer.Option(Path.cwd(), "--project", "-p", help="Generated project root."),
) -> None:
    """Preview generated file changes."""
    result = generate_project(project, dry_run=True, force=True)
    if not result.changed:
        typer.echo("No generated changes.")
        return
    for item in result.changed:
        typer.echo(item)


@app.command()
def doctor(
    project: Path = typer.Option(Path.cwd(), "--project", "-p", help="Generated project root."),
) -> None:
    """Validate generated project health."""
    report = run_doctor(project)
    for message in report.messages:
        typer.echo(message)
    if not report.ok:
        raise typer.Exit(1)


@app.command("removal-guide")
def removal_guide(
    project: Path = typer.Option(Path.cwd(), "--project", "-p", help="Generated project root."),
) -> None:
    """Write the manual generated-object removal guide."""
    path = write_removal_guide(project)
    typer.echo(f"Wrote {path}")


if __name__ == "__main__":
    app()
