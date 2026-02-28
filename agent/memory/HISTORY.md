# Curator — History

## 2026-02-28 — Initial Build

### What was built
- Complete Python package with Click CLI
- Core models: EvoEntry, CrossAgentPattern, Proposal
- Collector: EVOLUTION_LOG.md regex parser + marketplace scanner
- Analyzer: CrossAgentDetector with 3 strategies (error class clustering, tag overlap, rule convergence)
- Proposer: ProposalEngine generating shared skill/template proposals
- Pipeline: CuratorPipeline orchestrating COLLECT → ANALYZE → PROPOSE
- CLI commands: `curator scan`, `curator status`, `curator init`
- Full agent identity: ROLE.md, agent.yaml, memory/, skills/evo/

### Architecture decisions
- Separate repo from marketplace (clean separation)
- Regex-based parser (EVOLUTION_LOG.md is structured enough)
- 3 complementary detection strategies
- Severity-weighted proposal ranking
- Dry-run default with `--live` flag for PRs

### Key metrics
- ~20 source files
- ~1500 lines of code
- 3 detection strategies
- 4 proposal types
- 7 safety rules

### What's next
- Docker deployment
- GitHub Actions (scheduled scan + tests)
- Integration testing with real marketplace data
- Eva ↔ Curator cross-repo dispatch
