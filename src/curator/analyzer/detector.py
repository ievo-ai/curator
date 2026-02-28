"""Cross-agent pattern detection — Curator's analytical core."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from curator.core.models import CrossAgentPattern, EvoEntry, Severity


@dataclass
class CrossAgentDetector:
    """Detects patterns that span multiple agents.

    Detection strategies:
    1. Error class clustering — same error_class in multiple agents
    2. Tag overlap — same tags appearing across agent boundaries
    3. Rule convergence — multiple agents adding similar rules independently
    4. Temporal clustering — multiple agents evolving at the same time
    """

    min_agents: int = 2
    min_entries: int = 2

    _patterns: dict[str, CrossAgentPattern] = field(default_factory=dict)

    def analyze(self, entries: list[EvoEntry]) -> list[CrossAgentPattern]:
        """Analyze EVO entries and detect cross-agent patterns.

        Args:
            entries: All EVO entries collected from marketplace agents.

        Returns:
            Newly detected cross-agent patterns.
        """
        patterns: list[CrossAgentPattern] = []

        patterns.extend(self._detect_error_class_clusters(entries))
        patterns.extend(self._detect_tag_overlap(entries))
        patterns.extend(self._detect_rule_convergence(entries))

        return patterns

    def _detect_error_class_clusters(self, entries: list[EvoEntry]) -> list[CrossAgentPattern]:
        """Find same error class appearing in multiple agents."""
        patterns: list[CrossAgentPattern] = []

        # Group by error_class
        by_class: dict[str, list[EvoEntry]] = defaultdict(list)
        for e in entries:
            if e.error_class:
                by_class[e.error_class.lower().strip()].append(e)

        for error_class, group in by_class.items():
            agents = list({e.agent_name for e in group})
            if len(agents) < self.min_agents:
                continue

            pid = f"class:{error_class[:40]}"
            if pid in self._patterns:
                # Update existing
                p = self._patterns[pid]
                p.entry_ids = list({*p.entry_ids, *(e.key for e in group)})
                p.affected_agents = sorted(set(p.affected_agents) | set(agents))
                p.frequency = len(p.entry_ids)
                p.confidence = _class_confidence(len(agents), len(group))
                patterns.append(p)
            else:
                p = CrossAgentPattern(
                    id=pid,
                    title=f"Shared error class: {error_class}",
                    description=(
                        f"Error class '{error_class}' triggered EVO corrections in "
                        f"{len(agents)} agents: {', '.join(sorted(agents))}"
                    ),
                    entry_ids=[e.key for e in group],
                    affected_agents=sorted(agents),
                    error_class=error_class,
                    frequency=len(group),
                    severity=max((e.severity for e in group), default=Severity.MEDIUM),
                    confidence=_class_confidence(len(agents), len(group)),
                    suggested_action=(
                        f"Create or update shared skill to handle '{error_class}' errors "
                        f"so agents don't have to learn this individually."
                    ),
                )
                self._patterns[pid] = p
                patterns.append(p)

        return patterns

    def _detect_tag_overlap(self, entries: list[EvoEntry]) -> list[CrossAgentPattern]:
        """Find tags shared across multiple agents' EVO entries."""
        patterns: list[CrossAgentPattern] = []

        # Group by tag
        tag_agents: dict[str, set[str]] = defaultdict(set)
        tag_entries: dict[str, list[EvoEntry]] = defaultdict(list)

        for e in entries:
            for tag in e.tags:
                tag_lower = tag.lower().strip()
                if tag_lower in ("evo", "evolution", "fix", "patch", "update"):
                    continue  # Skip generic tags
                tag_agents[tag_lower].add(e.agent_name)
                tag_entries[tag_lower].append(e)

        for tag, agents in tag_agents.items():
            if len(agents) < self.min_agents:
                continue

            pid = f"tag:{tag}"
            if pid in self._patterns:
                continue

            group = tag_entries[tag]
            p = CrossAgentPattern(
                id=pid,
                title=f"Cross-agent tag: {tag}",
                description=(
                    f"Tag '{tag}' appears in EVO logs of {len(agents)} agents: "
                    f"{', '.join(sorted(agents))}"
                ),
                entry_ids=[e.key for e in group],
                affected_agents=sorted(agents),
                common_tags=[tag],
                frequency=len(group),
                severity=Severity.HIGH,
                confidence=min(0.35 + len(agents) * 0.15, 0.85),
                suggested_action=(
                    f"Investigate '{tag}' as a platform-wide concern. "
                    f"Consider a shared skill or template fix."
                ),
            )
            self._patterns[pid] = p
            patterns.append(p)

        return patterns

    def _detect_rule_convergence(self, entries: list[EvoEntry]) -> list[CrossAgentPattern]:
        """Find multiple agents adding similar rules independently.

        If 2+ agents add rules with overlapping keywords, they're converging
        on the same lesson — Curator should extract it as a shared skill.
        """
        patterns: list[CrossAgentPattern] = []

        # Only look at entries that added rules
        rule_entries = [e for e in entries if e.rule_added]
        if len(rule_entries) < self.min_entries:
            return patterns

        # Group by simplified rule keywords (first 5 significant words)
        rule_groups: dict[str, list[EvoEntry]] = defaultdict(list)
        for e in rule_entries:
            key = _simplify_rule(e.rule_added)
            if key:
                rule_groups[key].append(e)

        for key, group in rule_groups.items():
            agents = list({e.agent_name for e in group})
            if len(agents) < self.min_agents:
                continue

            pid = f"convergence:{key[:40]}"
            if pid in self._patterns:
                continue

            p = CrossAgentPattern(
                id=pid,
                title=f"Rule convergence: {key}",
                description=(
                    f"{len(agents)} agents independently added similar rules about '{key}'. "
                    f"Agents: {', '.join(sorted(agents))}"
                ),
                entry_ids=[e.key for e in group],
                affected_agents=sorted(agents),
                frequency=len(group),
                severity=Severity.MEDIUM,
                confidence=min(0.4 + len(agents) * 0.15 + len(group) * 0.05, 0.9),
                suggested_action=(
                    f"Extract the converged rule into a shared skill so all agents "
                    f"benefit without independent learning."
                ),
            )
            self._patterns[pid] = p
            patterns.append(p)

        return patterns

    @property
    def patterns(self) -> list[CrossAgentPattern]:
        """All detected patterns."""
        return list(self._patterns.values())


def _class_confidence(agent_count: int, entry_count: int) -> float:
    """Compute confidence for error class patterns."""
    # More agents and more entries = higher confidence
    base = 0.3
    agent_boost = agent_count * 0.15
    entry_boost = entry_count * 0.05
    return min(base + agent_boost + entry_boost, 0.9)


def _simplify_rule(rule: str) -> str:
    """Extract key concept from a rule string for comparison."""
    # Remove common prefixes and normalize
    rule = rule.lower().strip()
    for prefix in ("always ", "never ", "must ", "should ", "ensure ", "verify ", "check "):
        if rule.startswith(prefix):
            rule = rule[len(prefix):]

    # Take first 5 significant words
    words = [w for w in rule.split() if len(w) > 2][:5]
    return " ".join(words) if len(words) >= 2 else ""
