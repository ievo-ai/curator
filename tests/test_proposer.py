"""Tests for proposal engine."""

from curator.core.models import CrossAgentPattern, ProposalType, Severity
from curator.proposer.engine import ProposalEngine


def _make_pattern(
    pid: str = "class:format_error",
    agents: list[str] | None = None,
    confidence: float = 0.6,
    severity: Severity = Severity.MEDIUM,
    error_class: str = "format_error",
    common_tags: list[str] | None = None,
) -> CrossAgentPattern:
    agents = agents or ["agent-a", "agent-b"]
    return CrossAgentPattern(
        id=pid,
        title=f"Pattern {pid}",
        description=f"Test pattern for {pid}",
        entry_ids=["a:EVO-001", "b:EVO-001"],
        affected_agents=agents,
        error_class=error_class,
        common_tags=common_tags or [],
        frequency=2,
        severity=severity,
        confidence=confidence,
        suggested_action="Fix the issue",
    )


class TestProposalGeneration:
    def test_class_pattern_creates_skill_update(self):
        engine = ProposalEngine(max_per_run=5, min_confidence=0.3)
        patterns = [_make_pattern("class:format_error")]
        proposals = engine.generate(patterns)

        assert len(proposals) == 1
        assert proposals[0].type == ProposalType.SHARED_SKILL_UPDATE
        assert "format_error" in proposals[0].title
        assert proposals[0].target_path.startswith("shared/skills/")

    def test_tag_pattern_creates_best_practice(self):
        engine = ProposalEngine(max_per_run=5, min_confidence=0.3)
        patterns = [_make_pattern("tag:timeout", common_tags=["timeout"])]
        proposals = engine.generate(patterns)

        assert len(proposals) == 1
        assert proposals[0].type == ProposalType.BEST_PRACTICE
        assert proposals[0].target_path.startswith("docs/best-practices/")

    def test_convergence_pattern_creates_new_skill(self):
        engine = ProposalEngine(max_per_run=5, min_confidence=0.3)
        patterns = [_make_pattern("convergence:validate input data")]
        proposals = engine.generate(patterns)

        assert len(proposals) == 1
        assert proposals[0].type == ProposalType.SHARED_SKILL_CREATE

    def test_respects_max_per_run(self):
        engine = ProposalEngine(max_per_run=2, min_confidence=0.3)
        patterns = [
            _make_pattern("class:err1", confidence=0.9),
            _make_pattern("class:err2", confidence=0.8, error_class="err2"),
            _make_pattern("class:err3", confidence=0.7, error_class="err3"),
        ]
        proposals = engine.generate(patterns)
        assert len(proposals) <= 2

    def test_filters_low_confidence(self):
        engine = ProposalEngine(max_per_run=5, min_confidence=0.5)
        patterns = [
            _make_pattern("class:high", confidence=0.8),
            _make_pattern("class:low", confidence=0.2, error_class="low"),
        ]
        proposals = engine.generate(patterns)
        assert len(proposals) == 1
        assert proposals[0].confidence >= 0.5

    def test_ranks_by_severity_times_confidence(self):
        engine = ProposalEngine(max_per_run=5, min_confidence=0.3)
        patterns = [
            _make_pattern("class:low", confidence=0.5, severity=Severity.LOW, error_class="low"),
            _make_pattern("class:crit", confidence=0.5, severity=Severity.CRITICAL, error_class="crit"),
        ]
        proposals = engine.generate(patterns)
        assert len(proposals) == 2
        # Critical should come first (1.0 * 0.5 > 0.3 * 0.5)
        assert "crit" in proposals[0].title


class TestProposalContent:
    def test_shared_skill_has_evidence(self):
        engine = ProposalEngine()
        patterns = [_make_pattern("class:format_error")]
        proposals = engine.generate(patterns)

        content = proposals[0].content
        assert "format_error" in content
        assert "agent-a" in content
        assert "agent-b" in content
        assert "Evidence" in content

    def test_proposal_branch_name(self):
        engine = ProposalEngine()
        patterns = [_make_pattern("class:format_error")]
        proposals = engine.generate(patterns)

        branch = proposals[0].branch_name
        assert branch.startswith("curator/")
        assert "/" not in branch[len("curator/"):]
