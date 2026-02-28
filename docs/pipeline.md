# Pipeline

## Overview

Curator runs a three-phase pipeline: **COLLECT → ANALYZE → PROPOSE**.

```
COLLECT ──────▶ ANALYZE ──────▶ PROPOSE
(parse logs)    (detect)        (generate)
                                    │
                              ┌─────┴─────┐
                              │  REVIEW    │  (human)
                              │  MERGE     │  (human)
                              └───────────┘
```

## Phase 1: COLLECT

**Goal**: Gather all EVO entries from marketplace agents.

### Process
1. Scanner walks `marketplace/agents/*/` directories
2. For each agent with an `EVOLUTION_LOG.md`, the parser extracts entries
3. Entries are sorted by date (newest first)

### Parser Details
The parser uses regex to split `EVOLUTION_LOG.md` by `## EVO-\d+` headers, then extracts fields:

| Field | Pattern | Required |
|-------|---------|----------|
| Date | `**Date**:` or `Date:` | Yes |
| Type | `**Type**:` or `Type:` | Yes |
| Trigger | `**Trigger**:` or `Trigger:` | No |
| Root cause | `**Root cause**:` or `Root cause:` | No |
| Mutation | `**Mutation**:` or `Mutation:` | No |
| Rule added | `**Rule added**:` or `Rule added:` | No |
| Confidence | `**Confidence**:` | No |
| Class | `**Class**:` or `Error class:` | No |
| Severity | `**Severity**:` | No |
| Tags | `**Tags**:` | No |

Tags are parsed as comma-separated values, with optional `#` prefix stripped.

### Output
`List[EvoEntry]` — all entries across all agents, sorted by date.

## Phase 2: ANALYZE

**Goal**: Detect cross-agent patterns in the collected entries.

### Strategy 1: Error Class Clustering

Groups entries by `error_class`. A cluster qualifies as a pattern when:
- `error_class` is non-empty
- ≥ `min_agents_for_pattern` distinct agents share it
- ≥ `min_entries_for_pattern` total entries

**Confidence formula**:
```
confidence = min(0.3 + unique_agents × 0.15 + total_entries × 0.05, 0.9)
```

**Maps to**: `SHARED_SKILL_UPDATE` proposal

### Strategy 2: Tag Overlap

Finds tags shared across agent boundaries. A tag qualifies when:
- ≥ `min_agents_for_pattern` distinct agents use it
- ≥ `min_entries_for_pattern` total entries with that tag

**Confidence formula**:
```
confidence = min(0.35 + unique_agents × 0.15, 0.85)
```

**Maps to**: `BEST_PRACTICE` proposal

### Strategy 3: Rule Convergence

Detects when agents independently learn similar rules. Rules are simplified by:
1. Lowercasing
2. Removing stopwords (the, a, an, is, are, was, were, to, for, of, in, on, with, that, this, it, not, and, or, but, if, when, should, must, always, never)
3. Taking first 5 remaining words
4. Joining as a key

Two rules converge if they share the same simplified key across different agents.

**Confidence formula**:
```
confidence = min(0.4 + unique_agents × 0.15 + total_entries × 0.05, 0.9)
```

**Maps to**: `SHARED_SKILL_CREATE` proposal

### Output
`List[CrossAgentPattern]` — all patterns meeting confidence threshold.

## Phase 3: PROPOSE

**Goal**: Generate actionable proposals from detected patterns.

### Mapping

| Pattern source | Proposal type | Target |
|----------------|--------------|--------|
| `class:*` | `SHARED_SKILL_UPDATE` | `shared/skills/{class}/SKILL.md` |
| `tag:*` | `BEST_PRACTICE` | `docs/best-practices/{tag}.md` |
| `convergence:*` | `SHARED_SKILL_CREATE` | `shared/skills/{topic}/SKILL.md` |

### Ranking

Proposals are ranked by `severity_weight × confidence`:

| Severity | Weight |
|----------|--------|
| CRITICAL | 1.0 |
| HIGH | 0.8 |
| MEDIUM | 0.5 |
| LOW | 0.3 |
| INFO | 0.1 |

Only the top `max_proposals_per_run` proposals are kept.

### Output Modes

**Dry-run** (default): Prints summary table with proposal details, affected agents, confidence scores.

**Live** (`--live`): Creates GitHub PRs to the marketplace repo with the proposed changes.

## Error Handling

- Parser failures are logged but don't stop the pipeline
- Detection strategies run independently — one failing doesn't affect others
- If no patterns are found, pipeline completes with empty results
- If no entries are found, pipeline reports "no EVO data" and exits cleanly
