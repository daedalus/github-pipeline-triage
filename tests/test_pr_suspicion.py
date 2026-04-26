"""Tests for pr_suspicion module."""

from __future__ import annotations

from github_pipeline_triage.core.pr_suspicion import analyze_pr_suspicion
from github_pipeline_triage.core.types import PR, SuspicionLevel


class TestAnalyzePrSuspicion:
    def test_first_time_author(self, sample_pr: PR):
        result = analyze_pr_suspicion(sample_pr, "", 0)
        assert result.context_notes
        assert "first-time contributor" in result.context_notes[0]
        assert sample_pr.first_time_author is True

    def test_sensitive_path_workflow(self, sample_pr: PR):
        sample_pr.files = [".github/workflows/ci.yml"]
        result = analyze_pr_suspicion(sample_pr, "", 10)
        assert result.hard_flags
        assert "workflows/ci.yml" in result.hard_flags[0]
        assert result.suspicion_level != SuspicionLevel.NONE

    def test_large_diff_flag(self, sample_pr: PR):
        sample_pr.additions = 3000
        sample_pr.deletions = 1000
        result = analyze_pr_suspicion(sample_pr, "", 10)
        assert "very large diff" in result.hard_flags[0]
        assert result.suspicion_level == SuspicionLevel.LOW

    def test_no_flags_clean_pr(self, sample_pr: PR):
        result = analyze_pr_suspicion(sample_pr, "", 10)
        assert len(result.hard_flags) == 0
        assert result.suspicion_level == SuspicionLevel.NONE

    def test_eval_in_diff(self, sample_pr: PR):
        diff = "+    eval('malicious code')"
        result = analyze_pr_suspicion(sample_pr, diff, 10)
        assert len(result.hard_flags) > 0
        assert result.suspicion_level == SuspicionLevel.CRITICAL
