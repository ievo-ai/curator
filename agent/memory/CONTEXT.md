# Curator — Current Context

## Platform: iEvo

Self-evolving multi-agent SDD framework.

- **GitHub Org**: `ievo-ai`
- **Creator**: Denis (denis@27tech.co), 27Tech / Amplifier.AI

## Repos

| Repo | Purpose | Stack |
|------|---------|-------|
| `cli` | Developer CLI + TUI dashboard | Python, Typer, Textual |
| `marketplace` | Agent registry (`agents/` + `shared/`) | YAML + Markdown |
| `sdk` | Scaffold & validate agent packages | Python |
| `eva` | Level 3 — platform-wide meta-evolution | Python, Docker, GitHub Actions |
| `curator` | Level 2 — collective marketplace evolution (me) | Python, Click, Docker |
| `ievo.ai` | Landing page | Next.js |

## My Position in the Evolution Stack

```
Level 1: EVO (local)    — each agent corrects itself → EVOLUTION_LOG.md
Level 2: Curator (me)   — reads all EVO logs → shared skill proposals
Level 3: Eva (platform) — external signals → mutations to any repo
```

Eva can trigger me via `repository_dispatch` if she detects marketplace-level patterns.

## Data Sources

I read **only** from marketplace agents' `EVOLUTION_LOG.md` files. I never access external APIs, Sentry, or GitHub Issues — that's Eva's domain.

## Marketplace Structure

```
marketplace/
├── agents/
│   ├── agent-a/
│   │   ├── agent.yaml
│   │   ├── ROLE.md
│   │   ├── EVOLUTION_LOG.md  ← I read this
│   │   ├── memory/
│   │   └── skills/evo/
│   ├── agent-b/
│   └── ...
└── shared/
    ├── skills/           ← I propose updates here
    ├── templates/
    └── docs/
```

## Current State

- Core pipeline: COLLECT → ANALYZE → PROPOSE — implemented
- 3 detection strategies: error class clustering, tag overlap, rule convergence
- CLI: `curator scan`, `curator status`, `curator init`
- Dry-run by default, `--live` required for PRs
- Docker deployment planned
- GitHub Actions workflow planned

## Auth

- GitHub App (ievo-bot) for PR creation in live mode
- PAT fallback for development

## Documentation Standard (all iEvo repos)

Every repo must have: `README.md` (overview) + `CLAUDE.md` (AI context) + `docs/` (detailed reference).
No README inside `docs/` — root README links to docs/ files.
