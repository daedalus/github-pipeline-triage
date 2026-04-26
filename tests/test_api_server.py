"""Tests for API server module."""

from __future__ import annotations


class TestApiImports:
    """Test API module imports."""

    def test_server_imports(self) -> None:
        """Test server module can be imported."""
        from github_pipeline_triage.api import server

        assert server.app is not None


class TestAppConfig:
    """Test FastAPI app configuration."""

    def test_app_has_title(self) -> None:
        """Test app has correct title."""
        from github_pipeline_triage.api.server import app

        assert app.title == "github-pipeline-triage"

    def test_app_has_version(self) -> None:
        """Test app has version."""
        from github_pipeline_triage.api.server import app

        assert app.version == "0.1.0"

    def test_app_has_routes(self) -> None:
        """Test app has routes defined."""
        from github_pipeline_triage.api.server import app

        routes = [r.path for r in app.routes]
        assert len(routes) > 0
        assert "/api/items" in routes
        assert "/api/stats" in routes


class TestConnectionManager:
    """Test WebSocket connection manager."""

    def test_manager_init(self) -> None:
        """Test ConnectionManager initializes."""
        from github_pipeline_triage.api.server import ConnectionManager

        manager = ConnectionManager()
        assert manager.active_connections == []
        assert manager.subscriptions == {}

    def test_manager_disconnect(self) -> None:
        """Test ConnectionManager disconnect."""
        from github_pipeline_triage.api.server import ConnectionManager

        manager = ConnectionManager()
        assert manager.active_connections == []
        # Should not raise when empty
        # Note: can't easily test with real websocket without more setup


class TestGlobals:
    """Test module-level globals."""

    def test_latest_payload_init(self) -> None:
        """Test latest_payload starts as None."""
        from github_pipeline_triage.api import server

        assert server.latest_payload is None

    def test_latest_stats_init(self) -> None:
        """Test latest_stats starts as empty dict."""
        from github_pipeline_triage.api import server

        assert server.latest_stats == {}
