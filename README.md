# Curator

**Level 2 evolution for the iEvo marketplace** — cross-agent pattern detection and shared skill updates.

Curator reads what every marketplace agent learned through their EVO skill (Level 1), finds lessons that apply to multiple agents, and proposes shared skills so the entire marketplace benefits.

## Evolution Stack

| Level | Agent | Scope |
|-------|-------|-------|
| EVO | Each agent | Self-correction → `EVOLUTION_LOG.md` |
| **Curator** | **This** | **Cross-agent patterns → shared skills** |
| Eva | Platform | External signals → mutations to any repo |

## Quick Start

```bash
# Initialize config
curator init

# Run a scan (dry-run by default)
curator scan --marketplace ../marketplace

# Check status
curator status
```

## How It Works

1. **COLLECT** — Scans `agents/*/EVOLUTION_LOG.md` from the marketplace
2. **ANALYZE** — Detects cross-agent patterns using 3 strategies:
   - Error class clustering (same errors across agents)
   - Tag overlap (shared tags across agents)
   - Rule convergence (agents independently learning similar rules)
3. **PROPOSE** — Generates shared skill updates, ranked by severity × confidence

All proposals require human review. Curator never auto-merges.

## Installation

```bash
pip install -e .
```

## Docker

```bash
docker build -t curator .
docker run --rm -v /path/to/marketplace:/marketplace:ro curator scan --marketplace /marketplace
```

## Documentation

- [Architecture](docs/architecture.md) — system design, models, project structure
- [Pipeline](docs/pipeline.md) — COLLECT → ANALYZE → PROPOSE phases
- [Configuration](docs/configuration.md) — curator.yaml reference

## Part of iEvo

[ievo.ai](https://ievo.ai) — Self-evolving multi-agent SDD framework.
