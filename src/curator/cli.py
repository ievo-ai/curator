"""Curator CLI — Level 2 evolution for the iEvo marketplace."""

from __future__ import annotations

from pathlib import Path

import click

from curator.core.config import CuratorConfig
from curator.pipeline import CuratorPipeline


@click.group()
@click.version_option(version="0.1.0", prog_name="curator")
def main() -> None:
    """Curator — cross-agent pattern detection for iEvo marketplace."""


@main.command()
@click.option(
    "--config", "-c",
    default="curator.yaml",
    help="Path to curator.yaml config file.",
)
@click.option(
    "--marketplace", "-m",
    default=None,
    help="Path to marketplace repo (overrides config).",
)
@click.option(
    "--dry-run/--live",
    default=True,
    help="Dry-run mode (default) or live mode (creates PRs).",
)
def scan(config: str, marketplace: str | None, dry_run: bool) -> None:
    """Run one COLLECT → ANALYZE → PROPOSE cycle."""
    cfg = CuratorConfig.load(Path(config))
    cfg.dry_run = dry_run

    marketplace_dir = Path(marketplace) if marketplace else None

    pipeline = CuratorPipeline(cfg, marketplace_dir=marketplace_dir)
    result = pipeline.run()
    pipeline.print_summary(result)


@main.command()
@click.option("--config", "-c", default="curator.yaml")
def status(config: str) -> None:
    """Show current Curator config and marketplace status."""
    from rich.console import Console
    from rich.table import Table
    from curator.collector.scanner import list_agents

    console = Console()
    cfg = CuratorConfig.load(Path(config))

    # Config table
    table = Table(title="Curator Configuration")
    table.add_column("Setting", style="bold")
    table.add_column("Value")

    table.add_row("marketplace_repo", cfg.marketplace_repo)
    table.add_row("marketplace_path", cfg.marketplace_path or "(not set)")
    table.add_row("min_agents_for_pattern", str(cfg.min_agents_for_pattern))
    table.add_row("min_entries_for_pattern", str(cfg.min_entries_for_pattern))
    table.add_row("min_confidence", f"{cfg.min_confidence:.0%}")
    table.add_row("max_proposals_per_run", str(cfg.max_proposals_per_run))
    table.add_row("dry_run", "[yellow]true[/yellow]" if cfg.dry_run else "[green]false[/green]")

    console.print(table)

    # Agent list
    if cfg.marketplace_path:
        mp = Path(cfg.marketplace_path)
        if mp.exists():
            agents = list_agents(mp)
            console.print(f"\n[bold]Agents found:[/bold] {len(agents)}")
            for a in agents:
                evo = "[green]✓[/green]" if a["has_evo_log"] else "[dim]✗[/dim]"
                console.print(f"  {evo} {a['name']}")


@main.command()
@click.option("--output", "-o", default="curator.yaml", help="Output path.")
def init(output: str) -> None:
    """Initialize curator.yaml config file."""
    path = Path(output)
    if path.exists():
        click.confirm(f"{path} already exists. Overwrite?", abort=True)

    config = CuratorConfig()
    config.save(path)
    click.echo(f"Created {path}")


if __name__ == "__main__":
    main()
