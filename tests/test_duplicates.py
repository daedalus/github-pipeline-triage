"""Tests for duplicates module."""

from __future__ import annotations

from github_pipeline_triage.core.duplicates import find_duplicates, similarity_ratio
from github_pipeline_triage.core.types import Issue, IssueState


class TestSimilarityRatio:
    def test_identical_strings(self):
        ratio = similarity_ratio("hello world", "hello world")
        assert ratio == 1.0

    def test_empty_strings(self):
        ratio = similarity_ratio("", "")
        assert ratio == 1.0

    def test_completely_different(self):
        ratio = similarity_ratio("abc", "xyz")
        assert ratio == 0.0

    def test_similar_strings(self):
        ratio = similarity_ratio("hello world", "hello world!")
        assert ratio > 0.9

    def test_partial_similarity(self):
        ratio = similarity_ratio("bug in memory", "memory bug")
        assert ratio > 0.5


class TestFindDuplicates:
    def test_find_exact_duplicates(self):
        issues = [
            Issue(number=1, title="Bug: Memory leak", state=IssueState.OPEN, author="u", body="", created_at="2026-01-01"),
            Issue(number=2, title="Bug: Memory leak", state=IssueState.OPEN, author="u", body="", created_at="2026-01-01"),
        ]
        dupes = find_duplicates(issues)
        assert len(dupes) == 1
        assert dupes[0].a == 1
        assert dupes[0].b == 2

    def test_no_duplicates_below_threshold(self):
        issues = [
            Issue(number=1, title="Bug: Memory leak", state=IssueState.OPEN, author="u", body="", created_at="2026-01-01"),
            Issue(number=2, title="Feature: Add CLI", state=IssueState.OPEN, author="u", body="", created_at="2026-01-01"),
        ]
        dupes = find_duplicates(issues)
        assert len(dupes) == 0

    def test_only_checks_open_issues(self):
        issues = [
            Issue(number=1, title="Bug: Memory leak", state=IssueState.OPEN, author="u", body="", created_at="2026-01-01"),
            Issue(number=2, title="Bug: Memory leak", state=IssueState.CLOSED, author="u", body="", created_at="2026-01-01"),
        ]
        dupes = find_duplicates(issues)
        assert len(dupes) == 0
