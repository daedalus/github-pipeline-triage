"""Tests for pipeline service."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from github_pipeline_triage.core.types import (
    PR,
    DuplicatePair,
    Issue,
    IssueState,
    PrState,
    SuspicionLevel,
    SyncOptions,
)
from github_pipeline_triage.services import pipeline


class TestRunSync:
    """Test the main sync pipeline."""

    @pytest.mark.asyncio
    async def test_run_sync_empty_repo(self) -> None:
        """Test sync with no issues or PRs."""
        with (
            patch(
                "github_pipeline_triage.services.pipeline.fetch_issues"
            ) as mock_issues,
            patch("github_pipeline_triage.services.pipeline.fetch_prs") as mock_prs,
        ):
            mock_issues.return_value = []
            mock_prs.return_value = []

            result = await pipeline.run_sync(SyncOptions(repo="owner/repo"))

            assert result.repo == "owner/repo"
            assert len(result.issues) == 0
            assert len(result.prs) == 0
            assert result.fetched_at != ""

    @pytest.mark.asyncio
    async def test_run_sync_with_issues(self) -> None:
        """Test sync with issues."""
        test_issue = Issue(
            number=1,
            title="Test Issue",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="Test body",
            created_at="2026-01-01T00:00:00Z",
        )

        with (
            patch(
                "github_pipeline_triage.services.pipeline.fetch_issues"
            ) as mock_issues,
            patch("github_pipeline_triage.services.pipeline.fetch_prs") as mock_prs,
            patch(
                "github_pipeline_triage.services.pipeline.find_duplicates"
            ) as mock_dupes,
        ):
            mock_issues.return_value = [test_issue]
            mock_prs.return_value = []
            mock_dupes.return_value = []

            result = await pipeline.run_sync(SyncOptions(repo="owner/repo"))

            assert len(result.issues) == 1
            assert result.issues[0].severity is not None

    @pytest.mark.asyncio
    async def test_run_sync_detects_noise(self) -> None:
        """Test sync detects noise in issues."""
        noise_issue = Issue(
            number=1,
            title="TLDR",
            state=IssueState.OPEN,
            labels=[],
            author="newuser",
            body="Thanks!",
            created_at="2026-01-01T00:00:00Z",
        )

        with (
            patch(
                "github_pipeline_triage.services.pipeline.fetch_issues"
            ) as mock_issues,
            patch("github_pipeline_triage.services.pipeline.fetch_prs") as mock_prs,
            patch(
                "github_pipeline_triage.services.pipeline.find_duplicates"
            ) as mock_dupes,
        ):
            mock_issues.return_value = [noise_issue]
            mock_prs.return_value = []
            mock_dupes.return_value = []

            result = await pipeline.run_sync(SyncOptions(repo="owner/repo"))

            assert result.issues[0].is_noise is True
            assert result.issues[0].noise_reason != ""

    @pytest.mark.asyncio
    async def test_run_sync_with_prs(self) -> None:
        """Test sync with PRs."""
        test_pr = PR(
            number=1,
            title="Test PR",
            state=PrState.OPEN,
            labels=[],
            author="contributor",
            body="PR description",
            branch="feature",
            created_at="2026-01-01T00:00:00Z",
            files=["src/main.py"],
            additions=50,
            deletions=10,
        )

        with (
            patch(
                "github_pipeline_triage.services.pipeline.fetch_issues"
            ) as mock_issues,
            patch("github_pipeline_triage.services.pipeline.fetch_prs") as mock_prs,
            patch(
                "github_pipeline_triage.services.pipeline.find_duplicates"
            ) as mock_dupes,
            patch(
                "github_pipeline_triage.services.pipeline.fetch_pr_diff"
            ) as mock_diff,
            patch(
                "github_pipeline_triage.services.pipeline.fetch_author_history"
            ) as mock_history,
            patch(
                "github_pipeline_triage.services.pipeline.analyze_pr_suspicion"
            ) as mock_susp,
        ):
            mock_issues.return_value = []
            mock_prs.return_value = [test_pr]
            mock_dupes.return_value = []
            mock_diff.return_value = ""
            mock_history.return_value = 5
            mock_susp.return_value = Mock(
                hard_flags=[],
                suspicion_level=SuspicionLevel.NONE,
                context_notes=[],
            )

            result = await pipeline.run_sync(
                SyncOptions(repo="owner/repo", skip_diffs=False)
            )

            assert len(result.prs) == 1

    @pytest.mark.asyncio
    async def test_run_sync_skip_diffs(self) -> None:
        """Test sync with diffs skipped."""
        test_pr = PR(
            number=1,
            title="Test PR",
            state=PrState.OPEN,
            labels=[],
            author="contributor",
            body="",
            branch="feature",
            created_at="2026-01-01T00:00:00Z",
        )

        with (
            patch(
                "github_pipeline_triage.services.pipeline.fetch_issues"
            ) as mock_issues,
            patch("github_pipeline_triage.services.pipeline.fetch_prs") as mock_prs,
            patch(
                "github_pipeline_triage.services.pipeline.find_duplicates"
            ) as mock_dupes,
        ):
            mock_issues.return_value = []
            mock_prs.return_value = [test_pr]
            mock_dupes.return_value = []

            result = await pipeline.run_sync(
                SyncOptions(repo="owner/repo", skip_diffs=True)
            )

            assert len(result.prs) == 1

    @pytest.mark.asyncio
    async def test_run_sync_default_options(self) -> None:
        """Test sync with default options."""
        with (
            patch(
                "github_pipeline_triage.services.pipeline.fetch_issues"
            ) as mock_issues,
            patch("github_pipeline_triage.services.pipeline.fetch_prs") as mock_prs,
            patch(
                "github_pipeline_triage.services.pipeline.find_duplicates"
            ) as mock_dupes,
        ):
            mock_issues.return_value = []
            mock_prs.return_value = []
            mock_dupes.return_value = []

            result = await pipeline.run_sync()

            assert result.repo == "owner/repo"

    @pytest.mark.asyncio
    async def test_run_sync_finds_duplicates(self) -> None:
        """Test sync finds duplicate issues."""
        issue1 = Issue(
            number=1,
            title="Bug in memory",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="Memory bug description",
            created_at="2026-01-01T00:00:00Z",
        )
        issue2 = Issue(
            number=2,
            title="Memory bug issue",
            state=IssueState.OPEN,
            labels=[],
            author="user2",
            body="Another memory bug report",
            created_at="2026-01-01T00:00:00Z",
        )

        with (
            patch(
                "github_pipeline_triage.services.pipeline.fetch_issues"
            ) as mock_issues,
            patch("github_pipeline_triage.services.pipeline.fetch_prs") as mock_prs,
            patch(
                "github_pipeline_triage.services.pipeline.find_duplicates"
            ) as mock_dupes,
        ):
            mock_issues.return_value = [issue1, issue2]
            mock_prs.return_value = []
            mock_dupes.return_value = [DuplicatePair(a=1, b=2, similarity=0.85)]

            result = await pipeline.run_sync(SyncOptions(repo="owner/repo"))

            assert len(result.duplicates) == 1
