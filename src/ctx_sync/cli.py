"""CLI entry point for ctx-sync."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ctx_sync.detectors import detect_configs
from ctx_sync.models import ToolFormat
from ctx_sync.scorer import score
from ctx_sync.syncer import get_output_path, sync

app = typer.Typer(
    name="ctx-sync",
    help="Sync AI coding tool configs. Score quality. Stay consistent.",
    no_args_is_help=True,
)
console = Console()

# Format choices for CLI options
FORMAT_CHOICES = {
    "claude-md": ToolFormat.CLAUDE_MD,
    "agents-md": ToolFormat.AGENTS_MD,
    "cursorrules": ToolFormat.CURSOR_RULES,
    "copilot": ToolFormat.COPILOT,
}


def _parse_formats(format_strings: list[str]) -> list[ToolFormat]:
    """Convert string format names to ToolFormat enums."""
    result = []
    for s in format_strings:
        if s in FORMAT_CHOICES:
            result.append(FORMAT_CHOICES[s])
        else:
            valid = ", ".join(FORMAT_CHOICES.keys())
            console.print(f"[red]Unknown format: {s}. Valid: {valid}[/red]")
            raise typer.Exit(1)
    return result


@app.command()
def init(
    path: Path = typer.Argument(".", help="Project root directory"),
):
    """Scan a project for AI config files."""
    project_root = path.resolve()
    console.print(f"[dim]Scanning {project_root} ...[/dim]\n")

    configs = detect_configs(project_root)

    if not configs:
        console.print("[yellow]No AI config files detected.[/yellow]")
        console.print(
            "Supported: CLAUDE.md, AGENTS.md, .cursorrules, "
            ".cursor/rules/*.mdc, .github/copilot-instructions.md"
        )
        return

    table = Table(title="Detected AI Config Files")
    table.add_column("Tool", style="cyan", min_width=30)
    table.add_column("Path", style="green")
    table.add_column("Size", justify="right")

    for fmt, config_path in configs:
        try:
            size = config_path.stat().st_size
            size_str = f"{size:,}B"
        except OSError:
            size_str = "?"
        rel_path = config_path.relative_to(project_root) if config_path.is_relative_to(project_root) else config_path
        table.add_row(fmt.display_name, str(rel_path), size_str)

    console.print(table)

    if len(configs) >= 2:
        console.print(
            f"\n[green]Found {len(configs)} config formats. "
            f"Use [bold]ctx-sync sync[/bold] to keep them synchronized.[/green]"
        )
    else:
        console.print(
            "\n[dim]Tip: Use [bold]ctx-sync sync[/bold] to generate configs for other tools.[/dim]"
        )


@app.command(name="score")
def score_command(
    path: Path = typer.Argument(".", help="Config file or project directory to score"),
):
    """Score the quality of AI config files."""
    target = path.resolve()

    # Find config files
    if target.is_dir():
        configs = detect_configs(target)
        if not configs:
            console.print("[red]No config files found in directory.[/red]")
            raise typer.Exit(1)
    elif target.is_file():
        fmt = _detect_format(target)
        configs = [(fmt, target)] if fmt else []
        if not configs:
            console.print(f"[red]Cannot determine format of: {target}[/red]")
            raise typer.Exit(1)
    else:
        console.print(f"[red]Path not found: {target}[/red]")
        raise typer.Exit(1)

    for fmt, config_path in configs:
        content = config_path.read_text(encoding="utf-8")
        report = score(content, config_path)

        grade_colors = {"A": "green", "B": "yellow", "C": "yellow", "D": "red"}
        grade_color = grade_colors.get(report.grade, "white")

        console.print()
        console.print(
            Panel(
                f"[bold]{config_path.name}[/bold]\n"
                f"Score: [bold {grade_color}]{report.total}/100[/bold {grade_color}]  "
                f"Grade: [bold {grade_color}]{report.grade}[/bold {grade_color}]",
                title=fmt.display_name,
                border_style=grade_color,
            )
        )

        # Breakdown table
        breakdown_table = Table(show_header=True, header_style="dim")
        breakdown_table.add_column("Dimension", style="dim")
        breakdown_table.add_column("Score", justify="right")
        breakdown_table.add_column("Max", justify="right", style="dim")

        dimension_max = {
            "commands": 30, "architecture": 20, "conventions": 15,
            "conciseness": 15, "freshness": 10, "security": 10,
        }
        for dim, max_pts in dimension_max.items():
            pts = report.breakdown.get(dim, 0)
            dim_color = "green" if pts >= max_pts * 0.7 else ("yellow" if pts >= max_pts * 0.4 else "red")
            breakdown_table.add_row(dim.capitalize(), f"[{dim_color}]{pts}[/{dim_color}]", str(max_pts))

        console.print(breakdown_table)

        if report.issues:
            console.print("\n[red]Issues:[/red]")
            for issue in report.issues:
                console.print(f"  [red]x[/red] {issue}")

        if report.suggestions:
            console.print("\n[blue]Suggestions:[/blue]")
            for sug in report.suggestions:
                console.print(f"  [blue]->[/blue] {sug}")


@app.command(name="sync")
def sync_command(
    source: Path = typer.Argument(..., help="Source config file to sync from"),
    targets: Optional[list[str]] = typer.Option(
        None, "--to", "-t",
        help="Target format(s): claude-md, agents-md, cursorrules, copilot. Default: all.",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n",
        help="Preview output without writing files.",
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Output directory (default: same as source file's parent).",
    ),
):
    """Sync a config file to other AI tool formats."""
    source_path = source.resolve()
    if not source_path.is_file():
        console.print(f"[red]Source file not found: {source_path}[/red]")
        raise typer.Exit(1)

    project_root = output_dir.resolve() if output_dir else source_path.parent

    if targets:
        target_formats = _parse_formats(targets)
    else:
        target_formats = list(FORMAT_CHOICES.values())

    console.print(f"[dim]Source: {source_path.name}[/dim]")

    try:
        results = sync(source_path, target_formats)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    if not results:
        console.print("[yellow]No formats to sync to (source is the only format).[/yellow]")
        return

    for fmt, rendered in results.items():
        output_path = get_output_path(fmt, project_root)

        console.print()
        console.print(f"[bold cyan]-> {fmt.display_name}[/bold cyan]")
        console.print(f"   Output: {output_path}")

        if dry_run:
            console.print("[dim]   (dry run -- not written)[/dim]")
            console.print()
            preview_lines = rendered.split("\n")[:40]
            for line in preview_lines:
                console.print(f"   {line}")
            total_lines = rendered.count("\n") + 1
            if total_lines > 40:
                console.print(f"   ... ({total_lines - 40} more lines)")
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered, encoding="utf-8")
            console.print(f"   [green]OK  Written ({len(rendered.splitlines())} lines)[/green]")


@app.command()
def diff(
    path: Path = typer.Argument(".", help="Project directory to compare configs in"),
):
    """Compare differences between config files in a project."""
    project_root = path.resolve()
    configs = detect_configs(project_root)

    if len(configs) < 2:
        console.print("[yellow]Need at least 2 config files to compare.[/yellow]")
        console.print("Use [bold]ctx-sync sync[/bold] to generate additional formats.")
        return

    from ctx_sync.parsers import get_parser

    console.print(f"[dim]Comparing {len(configs)} config files in {project_root}[/dim]\n")

    table = Table(title="Content Comparison")
    table.add_column("Section", style="bold")

    for fmt, config_path in configs:
        table.add_column(fmt.value)

    check_sections = ["commands", "architecture", "conventions", "tech_stack", "git_standards"]

    for section in check_sections:
        row = [section.capitalize()]
        for fmt, config_path in configs:
            try:
                parser = get_parser(fmt)
                content = config_path.read_text(encoding="utf-8")
                ctx = parser.parse(content, config_path)
                val = getattr(ctx, section, None)
                if isinstance(val, list) and len(val) > 0:
                    row.append(f"[green]OK ({len(val)} items)[/green]")
                elif isinstance(val, str) and val.strip():
                    row.append("[green]OK[/green]")
                else:
                    row.append("[dim]--[/dim]")
            except Exception:
                row.append("[red]?[/red]")
        table.add_row(*row)

    # Line counts
    row = ["Line count"]
    for fmt, config_path in configs:
        try:
            lines = config_path.read_text(encoding="utf-8").strip().split("\n")
            row.append(str(len(lines)))
        except Exception:
            row.append("?")
    table.add_row(*row)

    # Scores
    row = ["Quality score"]
    for fmt, config_path in configs:
        try:
            content = config_path.read_text(encoding="utf-8")
            report = score(content, config_path)
            grade_colors = {"A": "green", "B": "yellow", "C": "yellow", "D": "red"}
            color = grade_colors.get(report.grade, "white")
            row.append(f"[{color}]{report.total}/100 ({report.grade})[/{color}]")
        except Exception:
            row.append("[red]?[/red]")
    table.add_row(*row)

    console.print(table)


def _detect_format(path: Path) -> ToolFormat | None:
    """Auto-detect the format of a config file."""
    from ctx_sync.parsers import get_all_parsers

    for fmt, parser_cls in get_all_parsers().items():
        parser = parser_cls()
        if parser.can_parse(path):
            return fmt
    return None


if __name__ == "__main__":
    app()
