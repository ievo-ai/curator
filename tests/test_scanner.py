"""Tests for marketplace scanner."""

from pathlib import Path

from curator.collector.scanner import scan_marketplace, list_agents


SAMPLE_EVO_LOG = """# Evolution Log

## EVO-001 — Test fix

- **Date**: 2026-02-28
- **Type**: new rule
- **Class**: test_error
- **Severity**: medium
- **Tags**: test
"""


def _setup_marketplace(tmp_path: Path, agents: dict[str, str | None]) -> Path:
    """Create a fake marketplace directory structure.

    Args:
        agents: Dict of agent_name -> evo_log_content (None = no log file).
    """
    marketplace = tmp_path / "marketplace"
    agents_dir = marketplace / "agents"

    for name, content in agents.items():
        agent_dir = agents_dir / name
        agent_dir.mkdir(parents=True)
        (agent_dir / "agent.yaml").write_text(f"name: {name}\n")

        if content is not None:
            (agent_dir / "EVOLUTION_LOG.md").write_text(content)

    return marketplace


def test_scan_finds_entries(tmp_path):
    mp = _setup_marketplace(tmp_path, {
        "agent-a": SAMPLE_EVO_LOG,
        "agent-b": SAMPLE_EVO_LOG,
    })
    entries = scan_marketplace(mp)
    assert len(entries) == 2
    agents = {e.agent_name for e in entries}
    assert agents == {"agent-a", "agent-b"}


def test_scan_skips_empty_logs(tmp_path):
    mp = _setup_marketplace(tmp_path, {
        "agent-a": SAMPLE_EVO_LOG,
        "agent-b": "# Evolution Log\n",
    })
    entries = scan_marketplace(mp)
    assert len(entries) == 1
    assert entries[0].agent_name == "agent-a"


def test_scan_skips_missing_logs(tmp_path):
    mp = _setup_marketplace(tmp_path, {
        "agent-a": SAMPLE_EVO_LOG,
        "agent-b": None,
    })
    entries = scan_marketplace(mp)
    assert len(entries) == 1


def test_scan_empty_marketplace(tmp_path):
    mp = tmp_path / "marketplace"
    mp.mkdir()
    entries = scan_marketplace(mp)
    assert len(entries) == 0


def test_list_agents(tmp_path):
    mp = _setup_marketplace(tmp_path, {
        "agent-a": SAMPLE_EVO_LOG,
        "agent-b": None,
    })
    agents = list_agents(mp)
    assert len(agents) == 2
    names = {a["name"] for a in agents}
    assert names == {"agent-a", "agent-b"}

    agent_a = next(a for a in agents if a["name"] == "agent-a")
    assert agent_a["has_evo_log"] is True

    agent_b = next(a for a in agents if a["name"] == "agent-b")
    assert agent_b["has_evo_log"] is False
