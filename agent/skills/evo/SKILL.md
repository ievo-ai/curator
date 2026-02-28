# EVO Skill — Curator Self-Evolution

> When Curator makes a mistake or a proposal is rejected, this skill classifies the error and updates Curator's own behavior.

## Trigger

After every `curator scan` run, check:
1. Were any proposals rejected by the human reviewer?
2. Did any detection strategy produce zero results despite available data?
3. Did the parser fail on any EVOLUTION_LOG.md entries?

## Classification

| Type | When | Action |
|------|------|--------|
| `false_positive` | Proposal rejected — pattern wasn't real | Raise confidence threshold for that strategy |
| `missed_pattern` | Human identified pattern Curator missed | Add detection rule or lower threshold |
| `bad_proposal` | Proposal content was incorrect/unhelpful | Improve template for that proposal type |
| `parser_failure` | EVOLUTION_LOG.md entry couldn't be parsed | Extend regex patterns |
| `stale_threshold` | Thresholds too high/low over time | Adjust based on acceptance rate |

## Evolution Entry Format

```markdown
## CUR-{NNN}

- **Date**: YYYY-MM-DD
- **Type**: {classification}
- **Trigger**: {what happened}
- **Root cause**: {why}
- **Mutation**: {what changed}
- **Confidence**: {0.0–1.0}
```

## Metrics to Track

| Metric | Target | Action if missed |
|--------|--------|-----------------|
| Proposal acceptance rate | > 70% | Lower confidence thresholds, improve templates |
| Pattern coverage | > 80% of cross-agent patterns | Add detection strategies |
| False positive rate | < 30% | Raise confidence thresholds |
| Parser success rate | > 95% | Extend regex patterns |

## Tunable Parameters

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| `min_agents_for_pattern` | 2 | 2–5 | Higher = fewer but stronger patterns |
| `min_entries_for_pattern` | 2 | 1–10 | Higher = more evidence required |
| `min_confidence` | 0.30 | 0.1–0.9 | Higher = fewer proposals |
| `max_proposals_per_run` | 5 | 1–20 | Rate limiting |

## Safety

- Never auto-adjust thresholds — always log and propose
- Track direction of changes (are we tightening or loosening over time?)
- If acceptance rate drops below 50%, pause and require human review of thresholds
- Every EVO entry links to the specific proposal that triggered it
