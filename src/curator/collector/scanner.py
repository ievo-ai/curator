"""Marketplace scanner — discovers agents and reads their evolution logs."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from curator.core.models import EvoEntry
from curator.collector.parser import parse_evolution_log

console = Console()


def scan_marketplace(marketplace_dir: Path) -> list[EvoEntry]:
    """Scan marketplace for all agents and collect their EVO entries.

    Args:
        marketplace_dir: Path to the marketplace repo root.

    Returns:
        All EVO entries from all agents, sorted by date.
    """
    agents_dir = marketplace_dir / "agents"
    if not agents_dir.exists():
        console.print(f"  [dim]No agents/ directory in {marketplace_dir}[/dim]")
        return []

    all_entries: list[EvoEntry] = []

    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir():
            continue

        agent_name = agent_dir.name
        evo_log = agent_dir / "EVOLUTION_LOG.md"

        if not evo_log.exists():
            continue

        content = evo_log.read_text(encoding="utf-8")
        if not content.strip() or content.strip() == "# Evolution Log":
            continue

        entries = parse_evolution_log(content, agent_name, str(agent_dir))

        if entries:
            console.print(f"  [green]✓[/green] {agent_name}: {len(entries)} entries")
            all_entries.extend(entries)
        else:
            console.print(f"  [dim]⊘ {agent_name}: log exists but no entries parsed[/dim]")

    return sorted(all_entries, key=lambda e: e.date)


def list_agents(marketplace_dir: Path) -> list[dict[str, str]]:
    """List all agents in the marketplace.

    Returns:
        List of dicts with 'name' and 'path' keys.
    """
    agents_dir = marketplace_dir / "agents"
    if not agents_dir.exists():
        return []

    agents = []
    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir():
            continue
        if not (agent_dir / "agent.yaml").exists():
            continue
        agents.append({
            "name": agent_dir.name,
            "path": str(agent_dir),
            "has_evo_log": (agent_dir / "EVOLUTION_LOG.md").exists(),
        })

    return agents
