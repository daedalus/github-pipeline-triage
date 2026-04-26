# AGENTS.md — github-pipeline-triage

## Overview

Automated GitHub issue and PR triage system. Fetches issues/PRs via `gh` CLI, applies heuristic classification (CRITICAL/HIGH/NORMAL severity), detects noise (low-quality issues), finds duplicates via Ratcliff-Obershelp similarity, and analyzes PR suspicion (red flags, first-time authors).

## Commands

```bash
# Install dev dependencies
pip install -e ".[test]"

# Run tests
pytest

# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/

# Run CLI
github-pipeline-triage sync --json
github-pipeline-triage audit-prs
github-pipeline-triage serve
```

## Architecture

```
src/github_pipeline_triage/
├── core/           # Domain logic: types, classify, duplicates, pr_suspicion
├── adapters/       # External: gh CLI wrappers, cache
├── services/       # Business: pipeline, render, audit
├── cli/            # CLI commands
├── api/            # FastAPI server + WebSocket
└── db/             # SQLAlchemy models + SQLite
```

## Testing

Tests use pytest with fixtures for mock GitHub responses.

## Code Style

- Format: ruff
- Lint: ruff + mypy (strict mode)
- Docstrings: Google style