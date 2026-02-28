# Curator — Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D-001 | Dry-run by default | Safety — never create PRs without explicit `--live` flag |
| D-002 | Min 2 agents for pattern | Avoid false positives from single-agent quirks |
| D-003 | Min 2 entries for pattern | Require repeated evidence before proposing |
| D-004 | Confidence threshold ≥ 30% | Low bar to surface weak signals, human reviews anyway |
| D-005 | Max 5 proposals per run | Rate limiting prevents noise |
| D-006 | Never auto-merge | Every proposal requires human approval |
| D-007 | Never modify individual agents | I only update shared resources (skills, templates, docs) |
| D-008 | Read only EVOLUTION_LOG.md | Clear scope boundary — external signals are Eva's domain |
| D-009 | Separate repo from marketplace | Clean separation of concerns, independent CI/CD |
| D-010 | Regex-based parser | EVOLUTION_LOG.md is structured Markdown, regex is sufficient |
| D-011 | 3 detection strategies | Error class clustering + tag overlap + rule convergence cover complementary patterns |
| D-012 | Severity-weighted ranking | Critical patterns surface first in proposal queue |
| D-013 | Full evidence chain | Every proposal links back to the EVO entries that triggered it |
| D-014 | Docker-based GitHub Actions | Consistent environment, same image for local and CI |
