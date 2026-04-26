"""Tests for GitHub adapter."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from github_pipeline_triage.adapters import gh
from github_pipeline_triage.core.types import IssueState, PrState


class TestRunGh:
    """Test gh command execution."""

    @pytest.mark.asyncio
    async def test_run_gh_success(self) -> None:
        """Test successful gh command execution."""
        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b'{"test": true}', b""))
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            stdout, code = await gh.run_gh(["issue", "list"])
            assert code == 0


class TestNewIssue:
    """Test Issue creation from raw data."""

    def test_new_issue_basic(self) -> None:
        """Test creating Issue from minimal data."""
        raw = {
            "number": 1,
            "title": "Test Issue",
            "state": "OPEN",
            "labels": [],
            "author": None,
            "body": "Issue body",
            "createdAt": "2026-01-01T00:00:00Z",
            "closedAt": None,
        }
        issue = gh.new_issue(raw)
        assert issue.number == 1
        assert issue.title == "Test Issue"
        assert issue.state == IssueState.OPEN
        assert issue.author == "—"

    def test_new_issue_with_labels(self) -> None:
        """Test Issue creation with labels."""
        raw = {
            "number": 2,
            "title": "Labeled Issue",
            "state": "CLOSED",
            "labels": [{"name": "bug"}, {"name": "high-priority"}],
            "author": {"login": "testuser"},
            "body": "Body text",
            "createdAt": "2026-01-01T00:00:00Z",
            "closedAt": "2026-01-02T00:00:00Z",
        }
        issue = gh.new_issue(raw)
        assert issue.labels == ["bug", "high-priority"]
        assert issue.author == "testuser"
        assert issue.state == IssueState.CLOSED


class TestNewPr:
    """Test PR creation from raw data."""

    def test_new_pr_basic(self) -> None:
        """Test creating PR from minimal data."""
        raw = {
            "number": 1,
            "title": "Test PR",
            "state": "OPEN",
            "labels": [],
            "author": None,
            "body": "PR body",
            "headRefName": "feature-branch",
            "createdAt": "2026-01-01T00:00:00Z",
            "mergedAt": None,
            "closedAt": None,
            "files": [],
            "additions": 0,
            "deletions": 0,
        }
        pr = gh.new_pr(raw)
        assert pr.number == 1
        assert pr.title == "Test PR"
        assert pr.state == PrState.OPEN
        assert pr.branch == "feature-branch"

    def test_new_pr_with_files(self) -> None:
        """Test PR creation with changed files."""
        raw = {
            "number": 2,
            "title": "Complex PR",
            "state": "MERGED",
            "labels": [{"name": "bug"}],
            "author": {"login": "contributor"},
            "body": "Fixes a bug",
            "headRefName": "fix/bug",
            "createdAt": "2026-01-01T00:00:00Z",
            "mergedAt": "2026-01-02T00:00:00Z",
            "closedAt": None,
            "files": [
                {"path": "src/main.py"},
                {"path": "tests/test_main.py"},
            ],
            "additions": 100,
            "deletions": 50,
        }
        pr = gh.new_pr(raw)
        assert pr.files == ["src/main.py", "tests/test_main.py"]
        assert pr.additions == 100
        assert pr.deletions == 50
        assert pr.state == PrState.MERGED


class TestGhJson:
    """Test gh_json function."""

    @pytest.mark.asyncio
    async def test_gh_json_error(self) -> None:
        """Test gh_json raises on error."""
        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(RuntimeError, match="exited with code"):
                await gh.gh_json(
                    ["invalid"],
                    cache_name=None,
                    use_cache=False,
                    repo="owner/repo",
                )
