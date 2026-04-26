"""Tests for audit service."""

from __future__ import annotations

from github_pipeline_triage.core.types import PR, PrState, SuspicionLevel
from github_pipeline_triage.services import audit


class TestAuditPrs:
    """Test audit_prs function."""

    def test_audit_prs_empty(self) -> None:
        """Test audit with no PRs."""
        result = audit.audit_prs([])
        assert "PR Suspicion Audit" in result

    def test_audit_prs_with_clean_pr(self) -> None:
        """Test audit with clean PR."""

        clean_pr = PR(
            number=1,
            title="Clean PR",
            state=PrState.OPEN,
            labels=[],
            author="trusted",
            body="Good PR description",
            branch="feature",
            created_at="2026-01-01T00:00:00Z",
            suspicion_level=SuspicionLevel.NONE,
        )
        result = audit.audit_prs([clean_pr])
        assert "Critical" not in result
        assert "High" not in result

    def test_audit_prs_critical(self) -> None:
        """Test audit with critical PR."""
        pr = PR(
            number=1,
            title="Suspicious PR",
            state=PrState.OPEN,
            labels=[],
            author="newuser",
            body="",
            branch="main",
            created_at="2026-01-01T00:00:00Z",
            suspicion_level=SuspicionLevel.CRITICAL,
            suspicious_flags=["touches security config"],
            first_time_author=True,
        )
        result = audit.audit_prs([pr])
        assert "Critical" in result
        assert "#1" in result
        assert "First-time" in result

    def test_audit_prs_high(self) -> None:
        """Test audit with high PR."""
        pr = PR(
            number=2,
            title="High PR",
            state=PrState.OPEN,
            labels=[],
            author="user",
            body="",
            branch="feature",
            created_at="2026-01-01T00:00:00Z",
            suspicion_level=SuspicionLevel.HIGH,
            suspicious_flags=["large diff"],
        )
        result = audit.audit_prs([pr])
        assert "High" in result

    def test_audit_prs_medium(self) -> None:
        """Test audit with medium PR."""
        pr = PR(
            number=3,
            title="Medium PR",
            state=PrState.OPEN,
            labels=[],
            author="user",
            body="",
            branch="fix",
            created_at="2026-01-01T00:00:00Z",
            suspicion_level=SuspicionLevel.MEDIUM,
        )
        result = audit.audit_prs([pr])
        assert "Medium" in result

    def test_audit_prs_low(self) -> None:
        """Test audit with low PR."""
        pr = PR(
            number=4,
            title="Low PR",
            state=PrState.OPEN,
            labels=[],
            author="user",
            body="",
            branch="fix",
            created_at="2026-01-01T00:00:00Z",
            suspicion_level=SuspicionLevel.LOW,
            additions=3000,
            deletions=1000,
        )
        result = audit.audit_prs([pr])
        assert "Large diffs" in result


class TestNoiseReport:
    """Test noise_report function."""

    def test_noise_report_empty(self) -> None:
        """Test noise report with no issues."""
        result = audit.noise_report([])
        assert "No" in result or "0" in result

    def test_noise_report_with_issues(self) -> None:
        """Test noise report with issues."""
        from github_pipeline_triage.core.types import Issue, IssueState

        noise = Issue(
            number=1,
            title="TLDR",
            state=IssueState.OPEN,
            labels=[],
            author="newuser",
            body="Thanks!",
            created_at="2026-01-01T00:00:00Z",
            is_noise=True,
            noise_reason="Short title",
        )
        result = audit.noise_report([noise])
        assert "noise" in result.lower() or "1" in result

    def test_noise_report_multiple(self) -> None:
        """Test noise report with multiple issues."""
        from github_pipeline_triage.core.types import Issue, IssueState

        issues = [
            Issue(
                number=1,
                title="TLDR",
                state=IssueState.OPEN,
                labels=[],
                author="user",
                body="",
                created_at="2026-01-01T00:00:00Z",
                is_noise=True,
                noise_reason="short",
            ),
            Issue(
                number=2,
                title="Thanks",
                state=IssueState.OPEN,
                labels=[],
                author="user",
                body="",
                created_at="2026-01-01T00:00:00Z",
                is_noise=True,
                noise_reason="thank you",
            ),
        ]
        result = audit.noise_report(issues)
        assert "2" in result
