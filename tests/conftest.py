"""Test fixtures for github-pipeline-triage."""

from __future__ import annotations

from typing import Any

import pytest

from github_pipeline_triage.core.types import PR, Issue, IssueState, PrState


@pytest.fixture
def sample_issue() -> Issue:
    return Issue(
        number=123,
        title="Segfault when processing large files",
        state=IssueState.OPEN,
        labels=["bug", "crash"],
        author="testuser",
        body="The application crashes with segfault when files exceed 1GB.",
        created_at="2026-01-01T00:00:00Z",
    )


@pytest.fixture
def sample_pr() -> PR:
    return PR(
        number=456,
        title="Fix memory leak",
        state=PrState.OPEN,
        labels=["bug", "enhancement"],
        author="contributor",
        body="This PR fixes a memory leak in the cache module.",
        branch="fix/memory-leak",
        created_at="2026-01-01T00:00:00Z",
        files=["src/cache.py"],
        additions=50,
        deletions=10,
    )


@pytest.fixture
def noise_issue() -> Issue:
    return Issue(
        number=789,
        title="TLDR",
        state=IssueState.OPEN,
        labels=[],
        author="newuser",
        body="Thanks for this project!",
        created_at="2026-01-01T00:00:00Z",
    )


@pytest.fixture
def feature_issue() -> Issue:
    return Issue(
        number=101,
        title="Feature: Add support for custom encodings",
        state=IssueState.OPEN,
        labels=["enhancement"],
        author="devuser",
        body="Would be nice to support custom text encodings.",
        created_at="2026-01-01T00:00:00Z",
    )


@pytest.fixture
def mock_gh_response() -> dict[str, Any]:
    return {
        "issues": [
            {"number": 1, "title": "Bug report", "state": "OPEN", "labels": [{"name": "bug"}], "author": {"login": "user1"}, "body": "Fix this", "createdAt": "2026-01-01T00:00:00Z", "closedAt": None},
            {"number": 2, "title": "New feature", "state": "OPEN", "labels": [{"name": "enhancement"}], "author": {"login": "user2"}, "body": "Add feature", "createdAt": "2026-01-01T00:00:00Z", "closedAt": None},
        ],
        "prs": [
            {"number": 10, "title": "PR Title", "state": "OPEN", "labels": [], "author": {"login": "user3"}, "body": "PR body", "headRefName": "feature-branch", "createdAt": "2026-01-01T00:00:00Z", "mergedAt": None, "closedAt": None, "additions": 100, "deletions": 50, "files": []},
        ],
    }
