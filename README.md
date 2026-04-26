# github-pipeline-triage

Automated GitHub issue and PR triage system with heuristic classification, noise detection, duplicate finding, and PR suspicion analysis.

[![PyPI](https://img.shields.io/pypi/v/github-pipeline-triage.svg)](https://pypi.org/project/github-pipeline-triage/)
[![Python](https://img.shields.io/pypi/pyversions/github-pipeline-triage.svg)](https://pypi.org/project/github-pipeline-triage/)

## Install

```bash
pip install github-pipeline-triage
```

## Usage

```bash
# Run full sync and generate ISSUES.md report
github-pipeline-triage sync

# Output as JSON
github-pipeline-triage sync --json

# Skip cache
github-pipeline-triage sync --no-cache

# Skip PR diff analysis
github-pipeline-triage sync --skip-diffs

# Audit suspicious PRs
github-pipeline-triage audit-prs

# Show noise candidates
github-pipeline-triage noise-report

# Start API server
github-pipeline-triage serve --port 8000
```

## API

The server provides REST and WebSocket endpoints:

- `GET /api/items` - List triage items
- `GET /api/stats` - Statistics
- `GET /api/activity` - Activity log
- `GET /api/maintainers` - Maintainer list
- `WS /ws` - Real-time updates

## Development

```bash
git clone https://github.com/dclavijo/github-pipeline-triage.git
cd github-pipeline-triage
pip install -e ".[test]"

# Run tests
pytest

# Format
ruff format src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Architecture

- **Core**: Heuristic classification, noise detection, duplicate finding
- **Adapters**: GitHub CLI wrappers, caching
- **Services**: Pipeline, rendering, auditing
- **API**: FastAPI server with WebSocket
- **DB**: SQLAlchemy with SQLite