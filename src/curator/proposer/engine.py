"""Proposal engine — converts cross-agent patterns into concrete proposals."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from curator.core.models import CrossAgentPattern, Proposal, ProposalType, Severity


@dataclass
class ProposalEngine:
    """Generates proposals from detected cross-agent patterns.

    Each proposal is a concrete change to shared marketplace resources:
    - Shared skills (most common)
    - Agent templates
    - Best practices documentation

    Safety:
    - Never auto-merge
    - Proposals include full context for reviewer
    - Low-confidence proposals flagged for manual review
    """

    max_per_run: int = 5
    min_confidence: float = 0.3
    _counter: int = 0
    _proposals: list[Proposal] = field(default_factory=list)

    def generate(self, patterns: list[CrossAgentPattern]) -> list[Proposal]:
        """Generate proposals from cross-agent patterns.

        Args:
            patterns: Detected cross-agent patterns.

        Returns:
            List of proposals (capped at max_per_run).
        """
        proposals: list[Proposal] = []

        # Rank by severity × confidence
        ranked = sorted(
            patterns,
            key=lambda p: (_severity_weight(p.severity) * p.confidence),
            reverse=True,
        )

        for pattern in ranked:
            if len(proposals) >= self.max_per_run:
                break
            if pattern.confidence < self.min_confidence:
                continue

            new_proposals = self._pattern_to_proposals(pattern)
            proposals.extend(new_proposals)

        self._proposals.extend(proposals)
        return proposals[:self.max_per_run]

    def _pattern_to_proposals(self, pattern: CrossAgentPattern) -> list[Proposal]:
        """Convert a pattern into one or more proposals."""
        proposals: list[Proposal] = []

        if pattern.id.startswith("class:"):
            # Error class cluster → shared skill for error handling
            self._counter += 1
            proposals.append(Proposal(
                id=f"prop-{self._counter:04d}",
                type=ProposalType.SHARED_SKILL_UPDATE,
                title=f"Shared skill for '{pattern.error_class}' errors",
                description=(
                    f"Error class '{pattern.error_class}' triggered independent "
                    f"EVO corrections in {pattern.agent_count} agents: "
                    f"{', '.join(pattern.affected_agents)}.\n\n"
                    f"Instead of each agent learning individually, create a shared "
                    f"skill that handles this error pattern."
                ),
                target_path=f"shared/skills/{_slugify(pattern.error_class)}/SKILL.md",
                content=_generate_shared_skill(pattern),
                pattern_id=pattern.id,
                affected_agents=pattern.affected_agents,
                confidence=pattern.confidence,
            ))

        elif pattern.id.startswith("tag:"):
            # Tag overlap → advisory + best practice
            self._counter += 1
            proposals.append(Proposal(
                id=f"prop-{self._counter:04d}",
                type=ProposalType.BEST_PRACTICE,
                title=f"Best practice: {pattern.common_tags[0] if pattern.common_tags else 'unknown'}",
                description=(
                    f"Cross-agent concern '{pattern.common_tags[0]}' detected in "
                    f"{pattern.agent_count} agents.\n\n"
                    f"{pattern.description}\n\n"
                    f"Propose a best practice document for the marketplace."
                ),
                target_path=f"docs/best-practices/{_slugify(pattern.common_tags[0] if pattern.common_tags else 'general')}.md",
                content=_generate_best_practice(pattern),
                pattern_id=pattern.id,
                affected_agents=pattern.affected_agents,
                confidence=pattern.confidence * 0.9,
            ))

        elif pattern.id.startswith("convergence:"):
            # Rule convergence → shared skill with the converged rule
            self._counter += 1
            proposals.append(Proposal(
                id=f"prop-{self._counter:04d}",
                type=ProposalType.SHARED_SKILL_CREATE,
                title=f"New shared skill from converged rules",
                description=(
                    f"{pattern.agent_count} agents independently learned similar rules.\n\n"
                    f"{pattern.description}\n\n"
                    f"Extract as a shared skill so all agents benefit."
                ),
                target_path=f"shared/skills/{_slugify(pattern.id.split(':', 1)[-1][:30])}/SKILL.md",
                content=_generate_converged_skill(pattern),
                pattern_id=pattern.id,
                affected_agents=pattern.affected_agents,
                confidence=pattern.confidence,
            ))

        return proposals

    @property
    def proposals(self) -> list[Proposal]:
        """All generated proposals."""
        return self._proposals


def _severity_weight(s: Severity) -> float:
    return {
        Severity.INFO: 0.1,
        Severity.LOW: 0.3,
        Severity.MEDIUM: 0.5,
        Severity.HIGH: 0.8,
        Severity.CRITICAL: 1.0,
    }.get(s, 0.5)


def _slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    return (
        text.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("/", "-")
        .replace(".", "-")
        .strip("-")[:40]
    )


def _generate_shared_skill(pattern: CrossAgentPattern) -> str:
    """Generate a shared skill document for an error class pattern."""
    date = datetime.utcnow().strftime("%Y-%m-%d")
    agents = ", ".join(pattern.affected_agents)
    return (
        f"# Shared Skill: Handle '{pattern.error_class}' Errors\n\n"
        f"> Auto-generated by Curator on {date}\n"
        f"> Pattern: {pattern.id} | Confidence: {pattern.confidence:.0%}\n"
        f"> Affected agents: {agents}\n\n"
        f"## Trigger\n\n"
        f"Activate when encountering errors classified as `{pattern.error_class}`.\n\n"
        f"## Background\n\n"
        f"{pattern.description}\n\n"
        f"## Rules\n\n"
        f"1. When a `{pattern.error_class}` error occurs, apply the following handling:\n"
        f"   - Classify the specific variant\n"
        f"   - Apply the appropriate fix\n"
        f"   - Log the resolution to EVOLUTION_LOG.md\n\n"
        f"2. If the fix doesn't resolve the issue, escalate via EVO skill.\n\n"
        f"## Evidence\n\n"
        f"This skill was created because {pattern.agent_count} agents independently "
        f"learned to handle this error class through their EVO skills. "
        f"Centralizing the knowledge prevents redundant learning.\n"
    )


def _generate_best_practice(pattern: CrossAgentPattern) -> str:
    """Generate a best practice document."""
    date = datetime.utcnow().strftime("%Y-%m-%d")
    tag = pattern.common_tags[0] if pattern.common_tags else "general"
    return (
        f"# Best Practice: {tag.title()}\n\n"
        f"> Generated by Curator on {date}\n"
        f"> Pattern: {pattern.id} | Confidence: {pattern.confidence:.0%}\n\n"
        f"## Context\n\n"
        f"{pattern.description}\n\n"
        f"## Recommendation\n\n"
        f"{pattern.suggested_action}\n\n"
        f"## Affected Agents\n\n"
        + "\n".join(f"- {a}" for a in pattern.affected_agents)
        + "\n"
    )


def _generate_converged_skill(pattern: CrossAgentPattern) -> str:
    """Generate a skill from converged rules."""
    date = datetime.utcnow().strftime("%Y-%m-%d")
    agents = ", ".join(pattern.affected_agents)
    return (
        f"# Shared Skill: Converged Rule\n\n"
        f"> Auto-generated by Curator on {date}\n"
        f"> Pattern: {pattern.id} | Confidence: {pattern.confidence:.0%}\n"
        f"> Derived from independent learning in: {agents}\n\n"
        f"## Background\n\n"
        f"{pattern.description}\n\n"
        f"## Rule\n\n"
        f"{pattern.suggested_action}\n\n"
        f"## Notes\n\n"
        f"This rule was independently discovered by {pattern.agent_count} agents. "
        f"Extracting it as a shared skill ensures all agents benefit without "
        f"redundant learning cycles.\n"
    )
