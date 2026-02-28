"""Core domain models for Curator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EvoEntryType(str, Enum):
    """Type of EVO self-correction entry."""

    FALSE_POSITIVE = "false_positive"
    MISSED_PATTERN = "missed_pattern"
    BAD_OUTPUT = "bad_output"
    STALE_RULE = "stale_rule"
    NEW_RULE = "new_rule"
    ROLE_PATCH = "role_patch"
    SKILL_UPDATE = "skill_update"


class Severity(str, Enum):
    """Severity level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ProposalType(str, Enum):
    """Type of change Curator can propose."""

    SHARED_SKILL_UPDATE = "shared_skill_update"    # Update shared/skills/*
    SHARED_SKILL_CREATE = "shared_skill_create"    # Create new shared skill
    TEMPLATE_UPDATE = "template_update"            # Update agent templates
    BEST_PRACTICE = "best_practice"                # Add to best practices doc
    AGENT_ADVISORY = "agent_advisory"              # Advisory for specific agents


@dataclass
class EvoEntry:
    """A single entry from an agent's EVOLUTION_LOG.md.

    Represents one self-correction that an agent made via its EVO skill.
    """

    id: str                        # e.g. "EVO-001"
    agent_name: str                # Which agent made this correction
    agent_path: str                # Path to agent dir in marketplace
    title: str
    entry_type: EvoEntryType
    error_class: str = ""          # Error classification (e.g. "format_error", "missing_field")
    rule_added: str = ""           # The rule that was added to ROLE.md
    severity: Severity = Severity.MEDIUM
    date: datetime = field(default_factory=datetime.utcnow)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        """Dedup key for this entry."""
        return f"{self.agent_name}:{self.id}"


@dataclass
class CrossAgentPattern:
    """A pattern detected across multiple agents' evolution logs.

    This is Curator's core output — showing that multiple agents
    independently learned the same lesson.
    """

    id: str
    title: str
    description: str
    entry_ids: list[str] = field(default_factory=list)
    affected_agents: list[str] = field(default_factory=list)
    error_class: str = ""          # Common error class
    common_tags: list[str] = field(default_factory=list)
    frequency: int = 1
    severity: Severity = Severity.MEDIUM
    confidence: float = 0.0
    suggested_action: str = ""

    @property
    def agent_count(self) -> int:
        return len(self.affected_agents)


@dataclass
class Proposal:
    """A proposed change to shared marketplace resources.

    Proposals are Curator's output — concrete changes to shared skills,
    templates, or best practices.
    """

    id: str
    type: ProposalType
    title: str
    description: str
    target_path: str               # e.g. "shared/skills/error-handling/SKILL.md"
    content: str                   # Full content or diff
    pattern_id: str = ""           # Pattern that triggered this
    affected_agents: list[str] = field(default_factory=list)
    confidence: float = 0.0
    approved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def branch_name(self) -> str:
        """Generate branch name for PR."""
        safe_id = self.id.replace(":", "-").replace("/", "-")
        return f"curator/{safe_id}"
