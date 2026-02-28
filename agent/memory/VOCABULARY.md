# Curator — Vocabulary

## Core Concepts

| Term | Meaning |
|------|---------|
| **EVO Entry** | A single self-correction record in an agent's EVOLUTION_LOG.md |
| **Cross-Agent Pattern** | A recurring theme detected across ≥2 agents' EVO logs |
| **Proposal** | A suggested change to shared marketplace resources |
| **Confidence** | 0.0–1.0 score indicating pattern strength |
| **Dry-run** | Default mode — analyze and report without creating PRs |
| **Live mode** | Creates actual GitHub PRs (`--live` flag required) |

## Evolution Levels

| Term | Meaning |
|------|---------|
| **EVO** | Level 1 — single agent self-correction |
| **Curator** | Level 2 — cross-agent pattern detection (me) |
| **Eva** | Level 3 — platform-wide meta-evolution |

## EVO Entry Types

| Type | Meaning |
|------|---------|
| `new_rule` | Agent learned a new rule |
| `false_positive` | Agent flagged something incorrectly |
| `missed_pattern` | Agent failed to detect something |
| `bad_output` | Agent produced incorrect output |
| `stale_rule` | Agent has an outdated rule |
| `role_patch` | Agent updated its ROLE.md |
| `skill_update` | Agent updated a skill file |

## Detection Strategies

| Strategy | What it detects |
|----------|-----------------|
| **Error class clustering** | Same `error_class` in multiple agents' logs |
| **Tag overlap** | Same tags appearing across agent boundaries |
| **Rule convergence** | Multiple agents independently adding similar rules |

## Proposal Types

| Type | Target | When |
|------|--------|------|
| `SHARED_SKILL_UPDATE` | `shared/skills/*/SKILL.md` | Error class affects multiple agents |
| `SHARED_SKILL_CREATE` | `shared/skills/new/SKILL.md` | Rules converge across agents |
| `BEST_PRACTICE` | `docs/best-practices/*.md` | Tag overlap suggests platform concern |
| `AGENT_ADVISORY` | (notification) | Specific agents need attention |

## Pipeline Phases

| Phase | Action |
|-------|--------|
| **COLLECT** | Scan `agents/*/EVOLUTION_LOG.md`, parse entries |
| **ANALYZE** | Run 3 detection strategies, produce patterns |
| **PROPOSE** | Generate proposals from patterns, rank by severity × confidence |
| **REVIEW** | Human reviews (outside pipeline) |
| **MERGE** | Shared resource updated (outside pipeline) |

## Platform Terms

| Term | Meaning |
|------|---------|
| **SDD** | Spec-Driven Development |
| **Agent package** | Standard structure: agent.yaml + ROLE.md + memory/ + skills/evo/ |
| **Marketplace** | Registry of all agents (`agents/` + `shared/`) |
| **Shared skill** | Skill available to all marketplace agents |
| **ievo-bot** | GitHub App for automated PRs |

## People

| Name | Role |
|------|------|
| **Denis** | Creator of iEvo, 27Tech / Amplifier.AI |
