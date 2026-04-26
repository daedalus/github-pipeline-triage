"""Tests for render service."""

from __future__ import annotations

from github_pipeline_triage.core.types import (
    PR,
    DuplicatePair,
    Issue,
    IssueState,
    PrState,
    Severity,
    SuspicionLevel,
    SyncPayload,
)
from github_pipeline_triage.services import render


class TestRenderIssuesMd:
    """Test markdown rendering."""

    def test_render_empty_payload(self) -> None:
        """Test rendering empty payload."""
        payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[],
            prs=[],
        )
        result = render.render_issues_md(payload)
        assert "Issues" in result
        assert "Fetched" in result or "Fetched" in result

    def test_render_issues_sorted_by_severity(self) -> None:
        """Test issues are sorted by severity."""
        issues = [
            Issue(
                number=1,
                title="Normal Issue",
                state=IssueState.OPEN,
                labels=[],
                author="user",
                body="",
                created_at="2026-01-01T00:00:00Z",
                severity=Severity.NORMAL,
            ),
            Issue(
                number=2,
                title="Critical Bug",
                state=IssueState.OPEN,
                labels=[],
                author="user",
                body="",
                created_at="2026-01-01T00:00:00Z",
                severity=Severity.CRITICAL,
            ),
            Issue(
                number=3,
                title="High Priority",
                state=IssueState.OPEN,
                labels=[],
                author="user",
                body="",
                created_at="2026-01-01T00:00:00Z",
                severity=Severity.HIGH,
            ),
        ]
        payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=issues,
            prs=[],
        )
        result = render.render_issues_md(payload)
        critical_pos = result.find("Critical Bug")
        high_pos = result.find("High Priority")
        normal_pos = result.find("Normal Issue")
        assert critical_pos < high_pos < normal_pos

    def test_render_issue_with_labels(self) -> None:
        """Test rendering issue with labels."""
        issue = Issue(
            number=1,
            title="Labeled Issue",
            state=IssueState.OPEN,
            labels=["bug", "high-priority"],
            author="user",
            body="Issue description",
            created_at="2026-01-01T00:00:00Z",
            severity=Severity.HIGH,
        )
        payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[issue],
            prs=[],
        )
        result = render.render_issues_md(payload)
        assert "#1" in result
        assert "Labeled Issue" in result

    def test_render_closed_issue(self) -> None:
        """Test rendering closed issue."""
        issue = Issue(
            number=1,
            title="Closed Issue",
            state=IssueState.CLOSED,
            labels=[],
            author="user",
            body="",
            created_at="2026-01-01T00:00:00Z",
            closed_at="2026-01-02T00:00:00Z",
        )
        payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[issue],
            prs=[],
        )
        result = render.render_issues_md(payload)
        assert "Closed" in result


class TestRenderPRs:
    """Test PR rendering."""

    def test_render_prs_section(self) -> None:
        """Test PRs are rendered in separate section."""
        pr = PR(
            number=1,
            title="Suspicious PR",
            state=PrState.OPEN,
            labels=[],
            author="contributor",
            body="Implements new feature",
            branch="feature/new",
            created_at="2026-01-01T00:00:00Z",
            suspicion_level=SuspicionLevel.HIGH,
        )
        payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[],
            prs=[pr],
        )
        result = render.render_issues_md(payload)
        assert "Suspicious PRs" in result
        assert "#1" in result

    def test_render_suspicious_pr(self) -> None:
        """Test rendering suspicious PR."""
        pr = PR(
            number=1,
            title="Suspicious PR",
            state=PrState.OPEN,
            labels=[],
            author="newuser",
            body="",
            branch="fix/urgent",
            created_at="2026-01-01T00:00:00Z",
            suspicion_level=SuspicionLevel.HIGH,
            suspicious_flags=["touches .github/workflows/ci.yml"],
            first_time_author=True,
        )
        payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[],
            prs=[pr],
        )
        result = render.render_issues_md(payload)
        assert "suspicious" in result.lower() or "high" in result.lower()


class TestRenderDuplicates:
    """Test duplicate rendering."""

    def test_render_duplicates_section(self) -> None:
        """Test duplicates are rendered."""
        dupes = [
            DuplicatePair(a=1, b=2, similarity=0.85),
            DuplicatePair(a=3, b=4, similarity=0.78),
        ]
        payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[],
            prs=[],
            duplicates=dupes,
        )
        result = render.render_issues_md(payload)
        assert "duplicate" in result.lower() or "similar" in result.lower()
