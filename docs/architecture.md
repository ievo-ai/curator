# Architecture

## Overview

Curator is Level 2 in the iEvo evolution stack. It reads what every marketplace agent learned through their EVO skill (Level 1) and extracts shared lessons that benefit the entire marketplace.

```
Level 1: EVO (local)     — agent self-corrects → EVOLUTION_LOG.md
Level 2: Curator (this)  — reads all logs → shared skill proposals
Level 3: Eva (platform)  — external signals → mutations to any repo
```

## System Design

```
┌─────────────────────────────────────────────────────────┐
│                     Marketplace Repo                     │
│  agents/                                                 │
│  ├── agent-a/EVOLUTION_LOG.md                           │
│  ├── agent-b/EVOLUTION_LOG.md    ──── COLLECT ────┐     │
│  ├── agent-c/EVOLUTION_LOG.md                     │     │
│  └── ...                                          │     │
│                                                   ▼     │
│  ┌──────────┐   ┌──────────┐   ┌───────────┐          │
│  │  Parser   │──▶│ Detector │──▶│ Proposer  │          │
│  │ (regex)   │   │(3 strats)│   │(templates)│          │
│  └──────────┘   └──────────┘   └───────────┘          │
│       │              │              │                    │
│    EvoEntry[]   Pattern[]      Proposal[]               │
│                                     │                    │
│  shared/                            │                    │
│  ├── skills/  ◀──── PROPOSE ────────┘                   │
│  ├── templates/                                          │
│  └── docs/best-practices/                               │
└─────────────────────────────────────────────────────────┘
```

## Domain Models

### EvoEntry
A single self-correction record parsed from an agent's `EVOLUTION_LOG.md`.

Fields: id, agent_name, agent_path, title, entry_type, error_class, rule_added, severity, date, tags, metadata.

### CrossAgentPattern
A recurring theme detected across ≥2 agents.

Fields: id, title, description, entry_ids, affected_agents, error_class, common_tags, frequency, severity, confidence.

### Proposal
A suggested change to shared marketplace resources.

Fields: id, type, title, description, target_path, content, pattern_id, affected_agents, confidence, approved.

## Detection Strategies

### 1. Error Class Clustering
Groups EVO entries by `error_class` field. If the same error class appears in ≥2 agents' logs, it's a cross-agent pattern.

**Confidence**: `min(0.3 + agents × 0.15 + entries × 0.05, 0.9)`

### 2. Tag Overlap
Finds tags that appear across agent boundaries. If ≥2 agents share the same tag in their EVO entries, it indicates a platform-wide concern.

**Confidence**: `min(0.35 + agents × 0.15, 0.85)`

### 3. Rule Convergence
Detects when multiple agents independently add similar rules. Rules are simplified to their first 5 significant words (excluding stopwords) for comparison.

**Confidence**: `min(0.4 + agents × 0.15 + entries × 0.05, 0.9)`

## Project Structure

```
curator/
├── src/curator/
│   ├── core/
│   │   ├── models.py      # EvoEntry, CrossAgentPattern, Proposal
│   │   └── config.py      # CuratorConfig (load/save YAML)
│   ├── collector/
│   │   ├── parser.py       # Regex parser for EVOLUTION_LOG.md
│   │   └── scanner.py      # Marketplace directory scanner
│   ├── analyzer/
│   │   └── detector.py     # CrossAgentDetector (3 strategies)
│   ├── proposer/
│   │   └── engine.py       # ProposalEngine (templates + ranking)
│   ├── pipeline.py         # CuratorPipeline orchestrator
│   └── cli.py              # Click CLI (scan, status, init)
├── agent/                   # Agent identity (iEvo standard)
│   ├── agent.yaml
│   ├── ROLE.md
│   ├── EVOLUTION_LOG.md
│   ├── memory/
│   └── skills/evo/
├── docs/                    # Technical documentation
├── tests/                   # Test suite
└── curator.yaml             # Default configuration
```

## Data Flow

1. **Input**: `marketplace/agents/*/EVOLUTION_LOG.md` files
2. **Parse**: Regex extracts structured `EvoEntry` objects from Markdown
3. **Detect**: 3 strategies run independently, producing `CrossAgentPattern` objects
4. **Propose**: Patterns mapped to `Proposal` objects with generated content
5. **Rank**: Proposals sorted by `severity_weight × confidence`
6. **Output**: Summary printed (dry-run) or PRs created (live mode)

## Relationship with Eva

Curator and Eva are complementary:

| Aspect | Curator | Eva |
|--------|---------|-----|
| Looks | Inward (evolution logs) | Outward (Sentry, GitHub, reviews) |
| Scope | Marketplace agents | Entire platform (any repo) |
| Input | EVOLUTION_LOG.md only | 4 external sources |
| Output | Shared skill proposals | Mutations to any file |
| Trigger | Scheduled scan | Scheduled + repository_dispatch |

Eva can trigger Curator via `repository_dispatch` if she detects marketplace-level patterns from external signals.
