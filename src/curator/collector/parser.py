"""Parser for agent EVOLUTION_LOG.md files."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from curator.core.models import EvoEntry, EvoEntryType, Severity

# Regex patterns for EVOLUTION_LOG.md entries
_ENTRY_HEADER = re.compile(r"^##\s+(EVO-\d+)\s*[—–-]\s*(.+)$", re.MULTILINE)
_FIELD_DATE = re.compile(r"\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})")
_FIELD_TYPE = re.compile(r"\*\*Type\*\*:\s*(.+)")
_FIELD_TRIGGER = re.compile(r"\*\*Trigger\*\*:\s*(.+)")
_FIELD_ROOT = re.compile(r"\*\*Root cause\*\*:\s*(.+)")
_FIELD_MUTATION = re.compile(r"\*\*Mutation\*\*:\s*(.+)")
_FIELD_CONFIDENCE = re.compile(r"\*\*Confidence\*\*:\s*(.+)")
_FIELD_CLASS = re.compile(r"\*\*Class\*\*:\s*(.+)")
_FIELD_SEVERITY = re.compile(r"\*\*Severity\*\*:\s*(.+)")
_FIELD_TAGS = re.compile(r"\*\*Tags\*\*:\s*(.+)")

# Type string → enum mapping
_TYPE_MAP = {
    "false positive": EvoEntryType.FALSE_POSITIVE,
    "missed pattern": EvoEntryType.MISSED_PATTERN,
    "bad output": EvoEntryType.BAD_OUTPUT,
    "stale rule": EvoEntryType.STALE_RULE,
    "new rule": EvoEntryType.NEW_RULE,
    "role patch": EvoEntryType.ROLE_PATCH,
    "skill update": EvoEntryType.SKILL_UPDATE,
}

_SEVERITY_MAP = {
    "critical": Severity.CRITICAL,
    "high": Severity.HIGH,
    "medium": Severity.MEDIUM,
    "low": Severity.LOW,
    "info": Severity.INFO,
}


def parse_evolution_log(content: str, agent_name: str, agent_path: str) -> list[EvoEntry]:
    """Parse an EVOLUTION_LOG.md file into EvoEntry objects.

    Args:
        content: Raw markdown content of the log file.
        agent_name: Name of the agent (e.g. "spec-writer").
        agent_path: Path to agent directory in marketplace.

    Returns:
        List of parsed EVO entries.
    """
    entries: list[EvoEntry] = []

    # Split by entry headers
    parts = _ENTRY_HEADER.split(content)
    # parts = [preamble, id1, title1, body1, id2, title2, body2, ...]

    if len(parts) < 4:
        return entries

    # Skip preamble (parts[0]), then process in groups of 3
    for i in range(1, len(parts), 3):
        if i + 2 >= len(parts):
            break

        entry_id = parts[i].strip()
        title = parts[i + 1].strip()
        body = parts[i + 2]

        entry = _parse_entry(entry_id, title, body, agent_name, agent_path)
        entries.append(entry)

    return entries


def _parse_entry(
    entry_id: str,
    title: str,
    body: str,
    agent_name: str,
    agent_path: str,
) -> EvoEntry:
    """Parse a single EVO entry from its body text."""
    # Extract fields
    date = _extract(_FIELD_DATE, body)
    entry_type_str = _extract(_FIELD_TYPE, body).lower().strip()
    trigger = _extract(_FIELD_TRIGGER, body)
    root_cause = _extract(_FIELD_ROOT, body)
    mutation = _extract(_FIELD_MUTATION, body)
    confidence_str = _extract(_FIELD_CONFIDENCE, body).lower().strip()
    error_class = _extract(_FIELD_CLASS, body)
    severity_str = _extract(_FIELD_SEVERITY, body).lower().strip()
    tags_str = _extract(_FIELD_TAGS, body)

    # Parse date
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()
    except ValueError:
        parsed_date = datetime.utcnow()

    # Parse type
    entry_type = _TYPE_MAP.get(entry_type_str, EvoEntryType.NEW_RULE)

    # Parse severity
    severity = _SEVERITY_MAP.get(severity_str, Severity.MEDIUM)

    # Parse tags
    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

    return EvoEntry(
        id=entry_id,
        agent_name=agent_name,
        agent_path=agent_path,
        title=title,
        entry_type=entry_type,
        error_class=error_class,
        rule_added=mutation,
        severity=severity,
        date=parsed_date,
        tags=tags,
        metadata={
            "trigger": trigger,
            "root_cause": root_cause,
            "confidence": confidence_str,
        },
    )


def _extract(pattern: re.Pattern, text: str) -> str:
    """Extract first match of pattern from text."""
    m = pattern.search(text)
    return m.group(1).strip() if m else ""
