"""Tests for API server."""

from __future__ import annotations

from fastapi.testclient import TestClient

from github_pipeline_triage.api import server
from github_pipeline_triage.core.types import (
    PR,
    Issue,
    IssueState,
    PrState,
    Severity,
    SyncPayload,
)


class TestApiEndpoints:
    """Test API endpoints."""

    def setup_method(self) -> None:
        """Setup test fixtures."""
        self.client = TestClient(server.app)
        server.latest_payload = None
        server.latest_stats = {}

    def test_get_items_empty(self) -> None:
        """Test get_items returns empty when no data."""
        response = self.client.get("/api/items")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_items_with_data(self) -> None:
        """Test get_items returns items when data exists."""
        test_issue = Issue(
            number=1,
            title="Test Issue",
            state=IssueState.OPEN,
            labels=["bug"],
            author="user",
            body="Test body",
            created_at="2026-01-01T00:00:00Z",
            severity=Severity.HIGH,
        )
        test_pr = PR(
            number=1,
            title="Test PR",
            state=PrState.OPEN,
            labels=[],
            author="user",
            body="PR body",
            branch="main",
            created_at="2026-01-01T00:00:00Z",
        )
        server.latest_payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[test_issue],
            prs=[test_pr],
        )

        response = self.client.get("/api/items")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_get_items_filter_by_kind(self) -> None:
        """Test filtering items by kind."""
        test_issue = Issue(
            number=1,
            title="Test Issue",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="",
            created_at="2026-01-01T00:00:00Z",
        )
        test_pr = PR(
            number=1,
            title="Test PR",
            state=PrState.OPEN,
            labels=[],
            author="user",
            body="",
            branch="main",
            created_at="2026-01-01T00:00:00Z",
        )
        server.latest_payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[test_issue],
            prs=[test_pr],
        )

        response = self.client.get("/api/items?kind=issue")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_get_items_filter_by_severity(self) -> None:
        """Test filtering items by severity."""
        critical_issue = Issue(
            number=1,
            title="Critical Bug",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="",
            created_at="2026-01-01T00:00:00Z",
            severity=Severity.CRITICAL,
        )
        normal_issue = Issue(
            number=2,
            title="Normal Issue",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="",
            created_at="2026-01-01T00:00:00Z",
            severity=Severity.NORMAL,
        )
        server.latest_payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[critical_issue, normal_issue],
            prs=[],
        )

        response = self.client.get("/api/items?severity=critical")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_get_stats_empty(self) -> None:
        """Test get_stats returns empty stats."""
        server.latest_payload = None
        response = self.client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data == {}

    def test_get_stats_with_data(self) -> None:
        """Test get_stats returns computed stats."""
        test_issue = Issue(
            number=1,
            title="Test",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="",
            created_at="2026-01-01T00:00:00Z",
        )
        test_pr = PR(
            number=1,
            title="Test",
            state=PrState.MERGED,
            labels=[],
            author="user",
            body="",
            branch="main",
            created_at="2026-01-01T00:00:00Z",
        )
        server.latest_payload = SyncPayload(
            fetched_at="2026-01-01T00:00:00Z",
            repo="owner/repo",
            issues=[test_issue],
            prs=[test_pr],
        )

        response = self.client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_issues"] == 1
        assert data["total_prs"] == 1

    def test_get_activity(self) -> None:
        """Test activity endpoint."""
        response = self.client.get("/api/activity")
        assert response.status_code == 200
        data = response.json()
        assert data["activity"] == []
        assert data["total"] == 0

    def test_get_maintainers(self) -> None:
        """Test maintainers endpoint."""
        response = self.client.get("/api/maintainers")
        assert response.status_code == 200
        data = response.json()
        assert data["maintainers"] == []
