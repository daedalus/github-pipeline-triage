"""Tests for cache adapter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from github_pipeline_triage.adapters import cache


class TestCacheFunctions:
    """Test cache utility functions."""

    def test_cache_path_returns_path(self) -> None:
        """Test that cache_path returns a Path."""
        result = cache.cache_path("test.json")
        assert isinstance(result, Path)
        assert result.name == "test.json"

    def test_cache_fresh_returns_false_when_missing(self, tmp_path: Path) -> None:
        """Test cache_fresh returns False when file doesn't exist."""
        result = cache.cache_fresh(tmp_path / "nonexistent.json")
        assert result is False


class TestCacheReadWrite:
    """Test cache read/write functions."""

    @pytest.mark.asyncio
    async def test_read_cached_json(self, tmp_path: Path) -> None:
        """Test reading cached JSON."""
        cache_file = tmp_path / "data.json"
        test_data = {"key": "value", "number": 42}
        cache_file.write_text(json.dumps(test_data))

        result = await cache.read_cached_json(cache_file)
        assert result == test_data

    @pytest.mark.asyncio
    async def test_read_cached_text(self, tmp_path: Path) -> None:
        """Test reading cached text."""
        cache_file = tmp_path / "text.txt"
        test_text = "Hello, world!"
        cache_file.write_text(test_text)

        result = await cache.read_cached_text(cache_file)
        assert result == test_text

    @pytest.mark.asyncio
    async def test_write_cached_json(self, tmp_path: Path) -> None:
        """Test writing JSON to cache."""
        cache_file = tmp_path / "output.json"
        test_data = {"test": True}

        await cache.write_cached_json(cache_file, test_data)

        with open(cache_file) as f:
            result = json.load(f)
        assert result == test_data

    @pytest.mark.asyncio
    async def test_write_cached_text(self, tmp_path: Path) -> None:
        """Test writing text to cache."""
        cache_file = tmp_path / "output.txt"
        test_text = "Some cached text"

        await cache.write_cached_text(cache_file, test_text)

        assert cache_file.read_text() == test_text
