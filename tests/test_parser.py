"""Tests for EVOLUTION_LOG.md parser."""

from curator.collector.parser import parse_evolution_log
from curator.core.models import EvoEntryType, Severity


SAMPLE_LOG = """# Evolution Log

> Self-correction entries.

---

## EVO-001 — Fixed format validation

- **Date**: 2026-02-15
- **Type**: false positive
- **Trigger**: User submitted valid YAML but validator rejected it
- **Root cause**: Regex too strict for multiline values
- **Mutation**: Relaxed regex to allow multiline strings
- **Class**: format_error
- **Severity**: high
- **Tags**: yaml, validation, format

## EVO-002 — Added timeout handling

- **Date**: 2026-02-20
- **Type**: new rule
- **Trigger**: Agent hung on external API call
- **Root cause**: No timeout configured
- **Mutation**: Always set timeout to 30s for external calls
- **Confidence**: 0.85
- **Class**: timeout_error
- **Severity**: medium
- **Tags**: timeout, api, reliability
"""


MINIMAL_LOG = """# Evolution Log

## EVO-001 — Quick fix

- **Date**: 2026-01-01
- **Type**: new rule
"""


EMPTY_LOG = """# Evolution Log

> No entries yet.
"""


def test_parse_full_entries():
    entries = parse_evolution_log(SAMPLE_LOG, "agent-a", "/agents/agent-a")
    assert len(entries) == 2

    e1 = entries[0]
    assert e1.id == "EVO-001"
    assert e1.agent_name == "agent-a"
    assert e1.title == "Fixed format validation"
    assert e1.entry_type == EvoEntryType.FALSE_POSITIVE
    assert e1.error_class == "format_error"
    assert e1.severity == Severity.HIGH
    assert set(e1.tags) == {"yaml", "validation", "format"}
    assert e1.date.year == 2026
    assert e1.date.month == 2
    assert e1.date.day == 15

    e2 = entries[1]
    assert e2.id == "EVO-002"
    assert e2.entry_type == EvoEntryType.NEW_RULE
    assert e2.error_class == "timeout_error"
    assert e2.severity == Severity.MEDIUM
    assert "timeout" in e2.tags


def test_parse_minimal_entry():
    entries = parse_evolution_log(MINIMAL_LOG, "agent-b", "/agents/agent-b")
    assert len(entries) == 1
    assert entries[0].id == "EVO-001"
    assert entries[0].entry_type == EvoEntryType.NEW_RULE


def test_parse_empty_log():
    entries = parse_evolution_log(EMPTY_LOG, "agent-c", "/agents/agent-c")
    assert len(entries) == 0


def test_parse_blank_content():
    entries = parse_evolution_log("", "agent-d", "/agents/agent-d")
    assert len(entries) == 0


def test_entry_key():
    entries = parse_evolution_log(SAMPLE_LOG, "agent-a", "/agents/agent-a")
    assert entries[0].key == "agent-a:EVO-001"
    assert entries[1].key == "agent-a:EVO-002"


def test_metadata_preserved():
    entries = parse_evolution_log(SAMPLE_LOG, "agent-a", "/agents/agent-a")
    e1 = entries[0]
    assert e1.metadata["trigger"] == "User submitted valid YAML but validator rejected it"
    assert e1.metadata["root_cause"] == "Regex too strict for multiline values"
