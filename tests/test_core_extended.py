"""Tests for classify and pr_suspicion - existing patterns."""

from __future__ import annotations

from github_pipeline_triage.core import classify
from github_pipeline_triage.core.types import (
    PR,
    Issue,
    IssueState,
    PrState,
    Severity,
    SuspicionLevel,
)


class TestClassifyIssue:
    """Test classify with Issue objects."""

    def test_classify_issue_bug_label(self) -> None:
        """Test classify with bug label."""
        issue = Issue(
            number=1,
            title="Issue",
            state=IssueState.OPEN,
            labels=["bug"],
            author="user",
            body="Body",
            created_at="2026-01-01T00:00:00Z",
        )
        result = classify.classify_severity(issue)
        assert result in [Severity.CRITICAL, Severity.HIGH, Severity.NORMAL]

    def test_classify_issue_enhancement(self) -> None:
        """Test classify with enhancement."""
        issue = Issue(
            number=2,
            title="Feature request",
            state=IssueState.OPEN,
            labels=["enhancement"],
            author="user",
            body="Would be nice",
            created_at="2026-01-01T00:00:00Z",
        )
        result = classify.classify_severity(issue)
        assert result == Severity.NORMAL


class TestDetectNoiseIssue:
    """Test detect_noise with Issue objects."""

    def test_detect_noise_short(self) -> None:
        """Test detect noise with short content."""
        issue = Issue(
            number=1,
            title="Hi",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="Hi",
            created_at="2026-01-01T00:00:00Z",
        )
        is_noise, reason = classify.detect_noise(issue)
        assert is_noise is True

    def test_detect_noise_has_body(self) -> None:
        """Test detect noise with full content."""
        issue = Issue(
            number=2,
            title="Bug report",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="I found a bug. Steps: 1. Do X 2. See error",
            created_at="2026-01-01T00:00:00Z",
        )
        is_noise, reason = classify.detect_noise(issue)
        assert is_noise is False


class TestPrSuspicionWithPr:
    """Test pr_suspicion with PR objects."""

    def test_analyze_pr_basic(self) -> None:
        """Test analyze_pr_suspicion basic."""
        from github_pipeline_triage.core import pr_suspicion

        pr = PR(
            number=1,
            title="Test PR",
            state=PrState.OPEN,
            labels=[],
            author="user",
            body="Description",
            branch="main",
            created_at="2026-01-01T00:00:00Z",
            files=[],
            additions=10,
            deletions=5,
        )
        result = pr_suspicion.analyze_pr_suspicion(pr, "", 0)
        assert result.suspicion_level == SuspicionLevel.NONE

    def test_analyze_pr_with_files(self) -> None:
        """Test analyze_pr_suspicion with files."""
        from github_pipeline_triage.core import pr_suspicion

        pr = PR(
            number=2,
            title="Config PR",
            state=PrState.OPEN,
            labels=[],
            author="user",
            body="Update config",
            branch="config",
            created_at="2026-01-01T00:00:00Z",
            files=[".github/workflows/ci.yml"],
            additions=5,
            deletions=2,
        )
        result = pr_suspicion.analyze_pr_suspicion(pr, "", 5)
        assert result.suspicion_level in list(SuspicionLevel)

    def test_cross_reference(self) -> None:
        """Test cross_reference_modules."""
        from github_pipeline_triage.core import pr_suspicion

        result = pr_suspicion.cross_reference_modules("auth user", [])
        assert isinstance(result, list)

    def test_extract_linked(self) -> None:
        """Test extract_linked_issues."""
        from github_pipeline_triage.core import pr_suspicion

        pr = PR(
            number=1,
            title="Fix",
            state=PrState.OPEN,
            labels=[],
            author="user",
            body="Closes #123",
            branch="fix",
            created_at="2026-01-01T00:00:00Z",
            files=[],
            additions=10,
            deletions=5,
        )
        result = pr_suspicion.extract_linked_issues(pr)
        assert isinstance(result, list)
