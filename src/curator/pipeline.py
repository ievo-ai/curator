"""Curator pipeline — COLLECT → ANALYZE → PROPOSE."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.table import Table

from curator.core.config import CuratorConfig
from curator.core.models import CrossAgentPattern, EvoEntry, Proposal
from curator.collector.scanner import scan_marketplace
from curator.analyzer.detector import CrossAgentDetector
from curator.proposer.engine import ProposalEngine

console = Console()


@dataclass
class CuratorRun:
    """Result of a single Curator pipeline run."""

    entries: list[EvoEntry] = field(default_factory=list)
    patterns: list[CrossAgentPattern] = field(default_factory=list)
    proposals: list[Proposal] = field(default_factory=list)


class CuratorPipeline:
    """The main Curator pipeline: COLLECT → ANALYZE → PROPOSE.

    ```
    ┌─────────────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
    │   Marketplace    │───▶│   EVO    │───▶│  Cross-   │───▶│ Proposals│
    │   agents/*/      │    │ Entries  │    │  Agent    │    │ Shared   │
    │ EVOLUTION_LOG.md │    │ parsed   │    │ Patterns  │    │ skills   │
    └─────────────────┘    └──────────┘    └───────────┘    └──────────┘
                                                                  │
                                                                  ▼
                                                            Human Review
                                                                  │
                                                                  ▼
                                                             Merge / Reject
    ```
    """

    def __init__(self, config: CuratorConfig, marketplace_dir: Path | None = None) -> None:
        self.config = config
        self.marketplace_dir = marketplace_dir or Path(config.marketplace_path)
        self.detector = CrossAgentDetector(
            min_agents=config.min_agents_for_pattern,
            min_entries=config.min_entries_for_pattern,
        )
        self.proposer = ProposalEngine(
            max_per_run=config.max_proposals_per_run,
            min_confidence=config.min_confidence,
        )

    def run(self) -> CuratorRun:
        """Execute one full COLLECT → ANALYZE → PROPOSE cycle.

        Returns:
            CuratorRun with all entries, patterns, and proposals.
        """
        result = CuratorRun()

        # Phase 1: COLLECT — scan marketplace agents' evolution logs
        console.print("\n[bold cyan]Phase 1: COLLECT[/bold cyan]")
        console.print(f"  Scanning: {self.marketplace_dir}")

        if not self.marketplace_dir.exists():
            console.print(f"  [red]✗ Marketplace not found: {self.marketplace_dir}[/red]")
            return result

        result.entries = scan_marketplace(self.marketplace_dir)

        if not result.entries:
            console.print("  [dim]No EVO entries found across marketplace agents.[/dim]")
            return result

        console.print(f"  Total entries: {len(result.entries)}")

        # Phase 2: ANALYZE — detect cross-agent patterns
        console.print("\n[bold cyan]Phase 2: ANALYZE[/bold cyan]")
        result.patterns = self.detector.analyze(result.entries)
        console.print(f"  Patterns detected: {len(result.patterns)}")

        for p in result.patterns:
            console.print(
                f"  [{_severity_color(p.severity)}]●[/{_severity_color(p.severity)}] "
                f"{p.title} — {p.agent_count} agents "
                f"[dim](confidence: {p.confidence:.0%})[/dim]"
            )

        if not result.patterns:
            console.print("  [dim]No cross-agent patterns detected.[/dim]")
            return result

        # Phase 3: PROPOSE — generate shared skill/template proposals
        console.print("\n[bold cyan]Phase 3: PROPOSE[/bold cyan]")
        result.proposals = self.proposer.generate(result.patterns)
        console.print(f"  Proposals generated: {len(result.proposals)}")

        if self.config.dry_run:
            console.print("  [yellow]⚠ DRY RUN — no PRs created[/yellow]")

        for p in result.proposals:
            console.print(
                f"  [bold]{p.id}[/bold] [{p.type.value}] {p.title[:60]} "
                f"[dim]→ {p.target_path}[/dim]"
            )

        return result

    def print_summary(self, run: CuratorRun) -> None:
        """Print a summary table of the run."""
        console.print("\n")
        table = Table(title="Curator Run Summary")
        table.add_column("Metric", style="bold")
        table.add_column("Count", justify="right")

        table.add_row("EVO entries collected", str(len(run.entries)))
        table.add_row("Agents with entries", str(len({e.agent_name for e in run.entries})))
        table.add_row("Cross-agent patterns", str(len(run.patterns)))
        table.add_row("Proposals generated", str(len(run.proposals)))
        table.add_row(
            "Mode",
            "[yellow]dry-run[/yellow]" if self.config.dry_run else "[green]live[/green]",
        )

        console.print(table)
        console.print()


def _severity_color(s) -> str:
    from curator.core.models import Severity
    return {
        Severity.CRITICAL: "red bold",
        Severity.HIGH: "red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "cyan",
        Severity.INFO: "dim",
    }.get(s, "white")
