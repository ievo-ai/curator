"""Tests for Curator pipeline integration."""

from pathlib import Path

from curator.core.config import CuratorConfig
from curator.pipeline import CuratorPipeline


AGENT_A_LOG = """# Evolution Log

## EVO-001 — Format validation fix

- **Date**: 2026-02-15
- **Type**: false positive
- **Class**: format_error
- **Severity**: high
- **Tags**: validation, format

## EVO-002 — Timeout handling

- **Date**: 2026-02-20
- **Type**: new rule
- **Mutation**: Always set timeout for external calls
- **Class**: timeout_error
- **Severity**: medium
- **Tags**: timeout, reliability
"""

AGENT_B_LOG = """# Evolution Log

## EVO-001 — Same format issue

- **Date**: 2026-02-16
- **Type**: missed pattern
- **Class**: format_error
- **Severity**: high
- **Tags**: validation, input

## EVO-002 — Add timeout rule

- **Date**: 2026-02-21
- **Type**: new rule
- **Mutation**: Always set timeout for external API calls
- **Class**: timeout_error
- **Severity**: medium
- **Tags**: timeout, api
"""


def _setup(tmp_path: Path) -> Path:
    mp = tmp_path / "marketplace"
    for name, content in [("agent-a", AGENT_A_LOG), ("agent-b", AGENT_B_LOG)]:
        d = mp / "agents" / name
        d.mkdir(parents=True)
        (d / "agent.yaml").write_text(f"name: {name}\n")
        (d / "EVOLUTION_LOG.md").write_text(content)
    return mp


def test_full_pipeline(tmp_path):
    mp = _setup(tmp_path)
    cfg = CuratorConfig()
    cfg.dry_run = True

    pipeline = CuratorPipeline(cfg, marketplace_dir=mp)
    result = pipeline.run()

    # Should collect entries from both agents
    assert len(result.entries) == 4
    assert len({e.agent_name for e in result.entries}) == 2

    # Should detect cross-agent patterns (format_error + timeout_error in both)
    assert len(result.patterns) > 0

    # Check we found format_error pattern
    class_patterns = [p for p in result.patterns if p.id.startswith("class:")]
    assert any(p.error_class == "format_error" for p in class_patterns)
    assert any(p.error_class == "timeout_error" for p in class_patterns)

    # Should generate proposals
    assert len(result.proposals) > 0

    # All proposals should have content
    for p in result.proposals:
        assert p.content
        assert p.target_path
        assert p.confidence >= cfg.min_confidence


def test_pipeline_empty_marketplace(tmp_path):
    mp = tmp_path / "marketplace"
    mp.mkdir()
    cfg = CuratorConfig()

    pipeline = CuratorPipeline(cfg, marketplace_dir=mp)
    result = pipeline.run()

    assert len(result.entries) == 0
    assert len(result.patterns) == 0
    assert len(result.proposals) == 0


def test_pipeline_missing_marketplace(tmp_path):
    cfg = CuratorConfig()
    pipeline = CuratorPipeline(cfg, marketplace_dir=tmp_path / "nonexistent")
    result = pipeline.run()

    assert len(result.entries) == 0
