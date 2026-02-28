# Curator — AI Context

## What is this?

Curator is **Level 2** of the iEvo evolution stack. It reads evolution logs from all marketplace agents, detects cross-agent patterns, and proposes shared skill updates.

```
Level 1: EVO     — agent self-corrects → EVOLUTION_LOG.md
Level 2: Curator — reads all logs → shared skill proposals (THIS REPO)
Level 3: Eva     — external signals → mutations to any repo
```

## Quick reference

- **Language**: Python 3.13+
- **CLI framework**: Click
- **Package layout**: `src/curator/`
- **Entry point**: `curator.cli:main`
- **Config**: `curator.yaml` (YAML)
- **Tests**: `pytest tests/ -v` (36 tests)
- **Lint**: `ruff check src/ tests/`

## Architecture

```
src/curator/
├── core/models.py     — EvoEntry, CrossAgentPattern, Proposal
├── core/config.py     — CuratorConfig (load/save YAML)
├── collector/parser.py — Regex parser for EVOLUTION_LOG.md
├── collector/scanner.py — Marketplace directory scanner
├── analyzer/detector.py — CrossAgentDetector (3 strategies)
├── proposer/engine.py  — ProposalEngine (templates + ranking)
├── pipeline.py         — CuratorPipeline orchestrator
└── cli.py              — Click CLI
```

## Pipeline

```
COLLECT → ANALYZE → PROPOSE → [REVIEW] → [MERGE]
```

1. Scan `marketplace/agents/*/EVOLUTION_LOG.md`
2. Detect patterns: error class clustering, tag overlap, rule convergence
3. Generate proposals ranked by severity × confidence
4. Human reviews (Curator never auto-merges)

## CLI commands

```bash
curator scan --marketplace ../marketplace --dry-run
curator status
curator init
```

## Safety rules

1. Dry-run by default (`--live` for PRs)
2. Never auto-merge
3. Max 5 proposals per run
4. Confidence threshold ≥ 30%
5. Pattern must span ≥ 2 agents
6. Never modify individual agents — only shared resources
7. Full evidence chain in every proposal

## Documentation

Detailed docs in `docs/`:
- [Architecture](docs/architecture.md) — system design, models, project structure
- [Pipeline](docs/pipeline.md) — COLLECT → ANALYZE → PROPOSE phases
- [Configuration](docs/configuration.md) — curator.yaml reference

## Documentation standard (all iEvo repos)

Every `ievo-ai/*` repo follows: `README.md` (overview) + `CLAUDE.md` (AI context) + `docs/` (detailed reference). No README inside `docs/`.

## Platform

- **GitHub Org**: `ievo-ai`
- **Repos**: cli, marketplace, sdk, eva, curator, ievo.ai
- **Creator**: Denis (denis@27tech.co)
