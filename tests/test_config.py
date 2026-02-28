"""Tests for Curator configuration."""

from pathlib import Path

from curator.core.config import CuratorConfig


def test_default_config():
    cfg = CuratorConfig()
    assert cfg.marketplace_repo == "ievo-ai/marketplace"
    assert cfg.min_agents_for_pattern == 2
    assert cfg.min_entries_for_pattern == 2
    assert cfg.min_confidence == 0.3
    assert cfg.max_proposals_per_run == 5
    assert cfg.dry_run is True
    assert cfg.auto_merge is False


def test_load_missing_file():
    cfg = CuratorConfig.load(Path("/nonexistent/curator.yaml"))
    # Should return defaults when file doesn't exist
    assert cfg.dry_run is True
    assert cfg.min_agents_for_pattern == 2


def test_save_and_load(tmp_path):
    path = tmp_path / "curator.yaml"

    cfg = CuratorConfig()
    cfg.min_agents_for_pattern = 3
    cfg.min_confidence = 0.5
    cfg.save(path)

    loaded = CuratorConfig.load(path)
    assert loaded.min_agents_for_pattern == 3
    assert loaded.min_confidence == 0.5
    assert loaded.dry_run is True


def test_load_partial_config(tmp_path):
    path = tmp_path / "curator.yaml"
    path.write_text("min_confidence: 0.7\nmax_proposals_per_run: 10\n")

    cfg = CuratorConfig.load(path)
    assert cfg.min_confidence == 0.7
    assert cfg.max_proposals_per_run == 10
    # Others should be defaults
    assert cfg.min_agents_for_pattern == 2
    assert cfg.dry_run is True
