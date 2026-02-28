# Configuration

## curator.yaml

Main configuration file. Created with `curator init`.

```yaml
# Path to local marketplace repo (for local development)
marketplace_path: ../marketplace

# GitHub repo for PR creation (live mode)
marketplace_repo: ievo-ai/marketplace

# Minimum distinct agents sharing a pattern
min_agents_for_pattern: 2

# Minimum total EVO entries for a pattern to qualify
min_entries_for_pattern: 2

# Minimum confidence score (0.0–1.0)
min_confidence: 0.3

# Maximum proposals per scan run
max_proposals_per_run: 5

# Dry-run mode (no PRs created)
dry_run: true

# Never auto-merge PRs
auto_merge: false
```

## Parameter Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `marketplace_path` | string | `""` | Local path to marketplace repo |
| `marketplace_repo` | string | `ievo-ai/marketplace` | GitHub org/repo for live PRs |
| `min_agents_for_pattern` | int | `2` | Min agents sharing a pattern |
| `min_entries_for_pattern` | int | `2` | Min total entries for pattern |
| `min_confidence` | float | `0.3` | Confidence threshold |
| `max_proposals_per_run` | int | `5` | Rate limit |
| `dry_run` | bool | `true` | Disable PR creation |
| `auto_merge` | bool | `false` | Always false (safety rule) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Live mode | GitHub App token or PAT for PR creation |
| `CURATOR_CONFIG` | No | Override config file path (default: `curator.yaml`) |
| `MARKETPLACE_PATH` | No | Override marketplace path |

## CLI Options

### `curator scan`

```bash
curator scan [OPTIONS]

Options:
  -c, --config PATH        Config file (default: curator.yaml)
  -m, --marketplace PATH   Marketplace path (overrides config)
  --dry-run / --live       Dry-run (default) or live mode
```

### `curator status`

```bash
curator status [OPTIONS]

Options:
  -c, --config PATH   Config file (default: curator.yaml)
```

Shows current configuration and lists marketplace agents with their EVO log status.

### `curator init`

```bash
curator init [OPTIONS]

Options:
  -o, --output PATH   Output path (default: curator.yaml)
```

Creates a default `curator.yaml` configuration file.

## Loading Order

1. Default values (hardcoded in `CuratorConfig`)
2. `curator.yaml` file (or path from `CURATOR_CONFIG` env var)
3. CLI options (`--marketplace`, `--dry-run/--live`)
4. Environment variables override matching config values

## Confidence Tuning

Adjust these parameters based on your marketplace size:

| Marketplace size | Recommended `min_agents` | Recommended `min_confidence` |
|-----------------|--------------------------|------------------------------|
| < 10 agents | 2 | 0.25 |
| 10–50 agents | 3 | 0.30 |
| 50–100 agents | 4 | 0.35 |
| > 100 agents | 5 | 0.40 |
