"""Tests for types module."""

from __future__ import annotations

from github_pipeline_triage.core.types import (
    PR,
    Issue,
    IssueState,
    PrState,
    Severity,
    SuspicionLevel,
    SyncOptions,
)


class TestIssue:
    def test_create_issue(self):
        issue = Issue(
            number=1,
            title="Test issue",
            state=IssueState.OPEN,
            author="user",
            body="Body",
            created_at="2026-01-01",
        )
        assert issue.number == 1
        assert issue.severity == Severity.NORMAL
        assert issue.is_noise is False

    def test_issue_model_dump(self):
        issue = Issue(
            number=1,
            title="Test",
            state=IssueState.OPEN,
            author="u",
            body="",
            created_at="2026-01-01",
        )
        data = issue.model_dump()
        assert data["state"] == "OPEN"
        assert data["severity"] == "normal"


class TestPR:
    def test_create_pr(self):
        pr = PR(
            number=1,
            title="Test PR",
            state=PrState.OPEN,
            author="user",
            body="Body",
            branch="main",
            created_at="2026-01-01",
        )
        assert pr.number == 1
        assert pr.suspicion_level == SuspicionLevel.NONE

    def test_pr_model_dump(self):
        pr = PR(
            number=1,
            title="Test",
            state=PrState.MERGED,
            author="u",
            body="",
            branch="main",
            created_at="2026-01-01",
        )
        data = pr.model_dump()
        assert data["state"] == "MERGED"
        assert data["suspicion_level"] == "none"


class TestSyncOptions:
    def test_defaults(self):
        options = SyncOptions()
        assert options.skip_diffs is False
        assert options.no_cache is False

    def test_custom_values(self):
        options = SyncOptions(skip_diffs=True, no_cache=True)
        assert options.skip_diffs is True
        assert options.no_cache is True
