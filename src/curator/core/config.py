"""Curator configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class CuratorConfig:
    """Top-level Curator configuration."""

    # Marketplace repo (local path or GitHub repo)
    marketplace_path: str = ""
    marketplace_repo: str = "ievo-ai/marketplace"

    # Analysis settings
    min_agents_for_pattern: int = 2      # Minimum agents sharing a pattern
    min_entries_for_pattern: int = 2     # Minimum EVO entries to form a pattern
    min_confidence: float = 0.3          # Minimum confidence to propose
    max_proposals_per_run: int = 5       # Cap on proposals per run

    # Safety
    dry_run: bool = True                 # Default safe mode
    auto_merge: bool = False             # Never auto-merge

    # Paths
    workspace: Path = field(default_factory=lambda: Path.home() / ".curator")

    # GitHub token (for PR creation in live mode)
    github_token_env: str = "CURATOR_GITHUB_TOKEN"

    @classmethod
    def load(cls, path: Path) -> CuratorConfig:
        """Load config from curator.yaml."""
        if not path.exists():
            return cls()
        data = yaml.safe_load(path.read_text()) or {}
        config = cls()

        # Simple field mapping
        field_map = {
            "marketplace_path": str,
            "marketplace_repo": str,
            "min_agents_for_pattern": int,
            "min_entries_for_pattern": int,
            "min_confidence": float,
            "max_proposals_per_run": int,
            "dry_run": bool,
            "auto_merge": bool,
        }

        for key, typ in field_map.items():
            if key in data:
                setattr(config, key, typ(data[key]))

        return config

    def save(self, path: Path) -> None:
        """Save config to curator.yaml."""
        data = {
            "marketplace_repo": self.marketplace_repo,
            "min_agents_for_pattern": self.min_agents_for_pattern,
            "min_entries_for_pattern": self.min_entries_for_pattern,
            "min_confidence": self.min_confidence,
            "max_proposals_per_run": self.max_proposals_per_run,
            "dry_run": self.dry_run,
            "auto_merge": self.auto_merge,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
