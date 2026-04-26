"""Tests for database module."""

from __future__ import annotations


class TestDbImports:
    """Test database module imports."""

    def test_client_imports(self) -> None:
        """Test client module can be imported."""
        from github_pipeline_triage.db import client

        assert hasattr(client, "get_db")
        assert hasattr(client, "init_db")
        assert hasattr(client, "engine")

    def test_schema_imports(self) -> None:
        """Test schema module can be imported."""
        from github_pipeline_triage.db import schema

        assert hasattr(schema, "Base")


class TestClientFunctions:
    """Test client functions."""

    def test_engine_exists(self) -> None:
        """Test engine is created."""
        from github_pipeline_triage.db import client

        assert client.engine is not None

    def test_init_db(self) -> None:
        """Test init_db runs without error."""
        from github_pipeline_triage.db.client import init_db

        # Should not raise
        init_db()

    def test_get_db(self) -> None:
        """Test get_db is a generator."""
        from github_pipeline_triage.db.client import get_db

        # get_db is a generator function
        result = get_db()
        assert hasattr(result, "__next__")
