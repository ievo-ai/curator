"""Tests for cross-agent pattern detector."""

from datetime import datetime

from curator.analyzer.detector import CrossAgentDetector, _simplify_rule
from curator.core.models import EvoEntry, EvoEntryType, Severity


def _make_entry(
    agent: str,
    entry_id: str = "EVO-001",
    error_class: str = "",
    tags: list[str] | None = None,
    rule_added: str = "",
    severity: Severity = Severity.MEDIUM,
) -> EvoEntry:
    return EvoEntry(
        id=entry_id,
        agent_name=agent,
        agent_path=f"/agents/{agent}",
        title="Test entry",
        entry_type=EvoEntryType.NEW_RULE,
        error_class=error_class,
        rule_added=rule_added,
        severity=severity,
        date=datetime(2026, 2, 28),
        tags=tags or [],
    )


class TestErrorClassClustering:
    def test_detects_shared_error_class(self):
        entries = [
            _make_entry("agent-a", "EVO-001", error_class="format_error"),
            _make_entry("agent-b", "EVO-001", error_class="format_error"),
        ]
        detector = CrossAgentDetector(min_agents=2, min_entries=2)
        patterns = detector.analyze(entries)

        class_patterns = [p for p in patterns if p.id.startswith("class:")]
        assert len(class_patterns) == 1
        assert class_patterns[0].error_class == "format_error"
        assert set(class_patterns[0].affected_agents) == {"agent-a", "agent-b"}

    def test_ignores_single_agent_class(self):
        entries = [
            _make_entry("agent-a", "EVO-001", error_class="format_error"),
            _make_entry("agent-a", "EVO-002", error_class="format_error"),
        ]
        detector = CrossAgentDetector(min_agents=2, min_entries=2)
        patterns = detector.analyze(entries)

        class_patterns = [p for p in patterns if p.id.startswith("class:")]
        assert len(class_patterns) == 0

    def test_confidence_increases_with_agents(self):
        entries_2 = [
            _make_entry("a", error_class="err"),
            _make_entry("b", error_class="err"),
        ]
        entries_3 = entries_2 + [_make_entry("c", error_class="err")]

        d2 = CrossAgentDetector(min_agents=2)
        d3 = CrossAgentDetector(min_agents=2)
        p2 = [p for p in d2.analyze(entries_2) if p.id.startswith("class:")]
        p3 = [p for p in d3.analyze(entries_3) if p.id.startswith("class:")]

        assert p3[0].confidence > p2[0].confidence


class TestTagOverlap:
    def test_detects_shared_tags(self):
        entries = [
            _make_entry("agent-a", tags=["timeout", "api"]),
            _make_entry("agent-b", tags=["timeout", "reliability"]),
        ]
        detector = CrossAgentDetector(min_agents=2, min_entries=2)
        patterns = detector.analyze(entries)

        tag_patterns = [p for p in patterns if p.id.startswith("tag:")]
        assert len(tag_patterns) == 1
        assert tag_patterns[0].common_tags == ["timeout"]

    def test_skips_generic_tags(self):
        entries = [
            _make_entry("agent-a", tags=["fix", "evo"]),
            _make_entry("agent-b", tags=["fix", "evo"]),
        ]
        detector = CrossAgentDetector(min_agents=2, min_entries=2)
        patterns = detector.analyze(entries)

        tag_patterns = [p for p in patterns if p.id.startswith("tag:")]
        assert len(tag_patterns) == 0


class TestRuleConvergence:
    def test_detects_similar_rules(self):
        entries = [
            _make_entry("agent-a", rule_added="Always validate input before processing data"),
            _make_entry("agent-b", rule_added="Must validate input before processing data"),
        ]
        detector = CrossAgentDetector(min_agents=2, min_entries=2)
        patterns = detector.analyze(entries)

        conv_patterns = [p for p in patterns if p.id.startswith("convergence:")]
        assert len(conv_patterns) == 1
        assert "agent-a" in conv_patterns[0].affected_agents
        assert "agent-b" in conv_patterns[0].affected_agents

    def test_ignores_dissimilar_rules(self):
        entries = [
            _make_entry("agent-a", rule_added="Always validate input format"),
            _make_entry("agent-b", rule_added="Never use deprecated API endpoints"),
        ]
        detector = CrossAgentDetector(min_agents=2, min_entries=2)
        patterns = detector.analyze(entries)

        conv_patterns = [p for p in patterns if p.id.startswith("convergence:")]
        assert len(conv_patterns) == 0


class TestSimplifyRule:
    def test_removes_prefixes(self):
        assert _simplify_rule("Always validate the input data") == "validate the input data"
        assert _simplify_rule("Never skip error handling step") == "skip error handling step"

    def test_takes_first_five_words(self):
        result = _simplify_rule("check every single field before sending the response")
        words = result.split()
        assert len(words) <= 5

    def test_empty_on_short_input(self):
        assert _simplify_rule("ok") == ""
        assert _simplify_rule("") == ""
