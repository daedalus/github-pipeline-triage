# SPEC.md — github-pipeline-triage

## Purpose

Automated GitHub issue and PR triage system for open-source projects. Applies heuristic classification (severity, noise detection, duplicate finding), PR suspicion analysis (red flags, first-time authors), and provides a real-time dashboard via REST API + WebSocket.

## Scope

### In Scope
- Fetch issues and PRs from GitHub via `gh` CLI
- Severity classification (CRITICAL/HIGH/NORMAL) via keyword matching
- Noise detection (low-quality issues: empty titles, thank-you posts, fear-mongering)
- Duplicate detection using Ratcliff-Obershelp similarity
- PR suspicion analysis: sensitive file paths, diff red flags, first-time author detection
- Module cross-referencing against project files
- Markdown report generation (ISSUES.md)
- CLI for local triage runs
- FastAPI REST API server with WebSocket support
- SQLite database for persistent storage
- Background poller for periodic GitHub sync

### Not In Scope
- Direct GitHub API calls (uses `gh` CLI only)
- Authentication system (uses gh CLI auth)
- Frontend dashboard (TypeScript Angular dashboard will be separate)
- Deep semantic analysis (handled by separate agent skill)

## Public API

### Core Module (`github_pipeline_triage.core`)

```python
from github_pipeline_triage.core.types import Issue, PR, Severity, SuspicionLevel

def classify_severity(issue: Issue) -> Severity
def detect_noise(issue: Issue) -> tuple[bool, str]
def similarity_ratio(a: str, b: str) -> float
def find_duplicates(issues: list[Issue]) -> list[DuplicatePair]
def analyze_pr_suspicion(pr: PR, diff: str, author_merged_count: int) -> SuspicionResult
def cross_reference_modules(text: str, changed_files: list[str]) -> list[str]
```

### GitHub Module (`github_pipeline_triage.adapters.gh`)

```python
from github_pipeline_triage.adapters.gh import fetch_issues, fetch_prs, fetch_pr_diff, fetch_author_history
```

### CLI (`github_pipeline_triage.cli`)

```bash
github-pipeline-triage sync          # Run full sync, generate ISSUES.md
github-pipeline-triage sync --json   # JSON output
github-pipeline-triage audit-prs     # PR audit report
github-pipeline-triage noise-report  # Noise candidates
github-pipeline-triage serve         # Start API server
```

### API Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/items` | List triage items with filters |
| GET | `/api/stats` | Aggregate statistics |
| GET | `/api/activity` | Recent activity log |
| GET | `/api/maintainers` | Maintainer allowlist |
| WS | `/ws` | WebSocket for real-time updates |

## Data Formats

### Issue
```python
{
    "number": int,
    "title": str,
    "state": "OPEN" | "CLOSED",
    "labels": list[str],
    "author": str,
    "body": str,
    "created_at": str,
    "closed_at": str | None,
    "severity": Severity,
    "is_noise": bool,
    "noise_reason": str,
    "modules": list[str],
}
```

### PR
```python
{
    "number": int,
    "title": str,
    "state": "OPEN" | "CLOSED" | "MERGED",
    "labels": list[str],
    "author": str,
    "body": str,
    "branch": str,
    "created_at": str,
    "merged_at": str | None,
    "closed_at": str | None,
    "files": list[str],
    "additions": int,
    "deletions": int,
    "suspicious_flags": list[str],
    "suspicion_level": SuspicionLevel,
    "context_notes": list[str],
    "modules": list[str],
    "linked_issues": list[int],
    "first_time_author": bool,
}
```

### DuplicatePair
```python
{"a": int, "b": int, "similarity": float}
```

## Heuristics

### Severity Keywords

**CRITICAL**: segfault, data loss, corrupt, malicious, exploit, RCE, path traversal, release defect, broken install

**HIGH**: silent fail, memory exhaustion, DoS, race condition, stale cache, plugin.json, pyproject.toml

### Noise Patterns
- Empty/non-substantive titles: "null", "test", "TLDR", only emoji
- Thank you / greeting-only bodies
- Fear-post titles: "!! COMPROMISED !!"

### PR Red Flags
- **critical**: eval(), exec(), subprocess shell=True, dynamic __import__, curl|wget pipe to shell
- **high**: .github/workflows/, hook scripts, conftest.py
- **medium**: pyproject.toml, LICENSE, uv.lock changes

## Edge Cases

1. Empty `gh` output (no issues/PRs) — return empty list, not error
2. `gh` command failure (transient) — log error, return empty/cached
3. First-time author (no prior PRs) — mark as suspicious context only
4. Very large PR diff (>2000 changes) — low severity flag
5. Single common-word module hit (e.g., "config.py") — require file path confirmation
6. Meta-reports ("Security Audit: 8 vulnerabilities") — demote severity one tier

## Performance & Constraints

- Cache TTL: 6 hours for GitHub data
- Max issues/PRs fetched: 500 per run
- Similarity threshold for duplicates: 0.85
- Poller interval: 15 minutes
- All I/O operations are async

## Architecture

```
github_pipeline_triage/
├── __init__.py
├── __main__.py
├── py.typed
├── core/
│   ├── __init__.py
│   ├── types.py          # Pydantic models
│   ├── classify.py       # Severity/noise classification
│   ├── duplicates.py     # Ratcliff-Obershelp similarity
│   └── pr_suspicion.py   # PR suspicion analysis
├── adapters/
│   ├── __init__.py
│   ├── gh.py             # GitHub CLI wrappers
│   └── cache.py          # On-disk caching
├── services/
│   ├── __init__.py
│   ├── pipeline.py       # End-to-end sync
│   ├── render.py         # Markdown generation
│   └── audit.py          # Terminal reports
├── cli/
│   ├── __init__.py
│   └── commands.py       # CLI commands
├── api/
│   ├── __init__.py
│   ├── routes.py         # REST endpoints
│   └── websocket.py      # WebSocket handler
└── db/
    ├── __init__.py
    ├── schema.py         # SQLAlchemy models
    ├── client.py         # SQLite connection
    └── poller.py         # Background sync
```