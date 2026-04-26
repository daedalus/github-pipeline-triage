"""Tests for classify module."""

from __future__ import annotations

from github_pipeline_triage.core.classify import classify_severity, detect_noise
from github_pipeline_triage.core.types import Issue, IssueState, Severity


class TestClassifySeverity:
    def test_critical_from_keyword_in_title(self, sample_issue: Issue):
        sample_issue.title = "Segfault in parser"
        severity = classify_severity(sample_issue)
        assert severity == Severity.CRITICAL

    def test_high_from_keyword(self):
        issue = Issue(
            number=1,
            title="DoS vulnerability in API",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="",
            created_at="2026-01-01",
        )
        severity = classify_severity(issue)
        assert severity == Severity.HIGH

    def test_normal_for_enhancement_label(self, sample_issue: Issue):
        sample_issue.labels = ["enhancement"]
        severity = classify_severity(sample_issue)
        assert severity == Severity.NORMAL

    def test_feature_prefix_normal(self, feature_issue: Issue):
        severity = classify_severity(feature_issue)
        assert severity == Severity.NORMAL

    def test_data_loss_critical(self, sample_issue: Issue):
        sample_issue.title = "Data loss when saving"
        severity = classify_severity(sample_issue)
        assert severity == Severity.CRITICAL

    def test_race_condition_high(self):
        issue = Issue(
            number=1,
            title="Race condition in concurrent processing",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="",
            created_at="2026-01-01",
        )
        severity = classify_severity(issue)
        assert severity == Severity.HIGH


class TestDetectNoise:
    def test_noise_tldr_title(self, noise_issue: Issue):
        is_noise, reason = detect_noise(noise_issue)
        assert is_noise is True
        assert "noise pattern" in reason

    def test_noise_short_title_and_body(self):
        issue = Issue(
            number=1,
            title="Help",
            state=IssueState.OPEN,
            labels=[],
            author="user",
            body="Pls",
            created_at="2026-01-01T00:00:00Z",
        )
        is_noise, reason = detect_noise(issue)
        assert is_noise is True

    def test_not_noise_substantive(self, sample_issue: Issue):
        is_noise, reason = detect_noise(sample_issue)
        assert is_noise is False
        assert reason == ""
