"""Severity classification and noise detection for issues."""

from __future__ import annotations

import re

from github_pipeline_triage.core.constants import (
    BUG_TITLE_PREFIX,
    CRITICAL_KEYWORDS,
    DEWEIGHT_PHRASES,
    FEATURE_TITLE_PREFIX,
    HIGH_KEYWORDS,
    META_REPORT_TITLE_PATTERNS,
    NOISE_BODY_PATTERNS,
    NOISE_TITLE_PATTERNS,
    SUBSTANTIVE_TITLE_MARKERS,
)
from github_pipeline_triage.core.types import Issue, Severity


def match_any(patterns: list[str], text: str) -> bool:
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def demote_once(sev: Severity) -> Severity:
    if sev is Severity.CRITICAL:
        return Severity.HIGH
    if sev is Severity.HIGH:
        return Severity.NORMAL
    return sev


def classify_severity(issue: Issue) -> Severity:
    title_lower = issue.title.lower()
    body_lower = issue.body.lower()

    if "enhancement" in issue.labels:
        return Severity.NORMAL
    if FEATURE_TITLE_PREFIX.search(issue.title):
        return Severity.NORMAL

    for phrase in DEWEIGHT_PHRASES:
        body_lower = body_lower.replace(phrase, "")

    is_bug_signaled = "bug" in issue.labels or BUG_TITLE_PREFIX.search(issue.title) is not None

    severity: Severity = Severity.NORMAL

    if match_any(CRITICAL_KEYWORDS, title_lower):
        severity = Severity.CRITICAL
    elif is_bug_signaled and match_any(CRITICAL_KEYWORDS, body_lower):
        severity = Severity.CRITICAL
    elif match_any(HIGH_KEYWORDS, title_lower):
        severity = Severity.HIGH
    elif is_bug_signaled and match_any(HIGH_KEYWORDS, body_lower):
        severity = Severity.HIGH

    for pat in META_REPORT_TITLE_PATTERNS:
        if pat.search(issue.title):
            severity = demote_once(severity)
            break

    return severity


def detect_noise(issue: Issue) -> tuple[bool, str]:
    title = issue.title.strip()
    body = issue.body.strip()
    substantive_title = SUBSTANTIVE_TITLE_MARKERS.search(title) is not None

    for pat in NOISE_TITLE_PATTERNS:
        if pat.search(title):
            return True, f"title matches noise pattern /{pat.pattern}/"

    if len(title) < 20 and len(body) < 40 and not substantive_title:
        return True, "very short title and body, no bug signal in title"

    if len(body) < 200 and not substantive_title:
        for pat in NOISE_BODY_PATTERNS:
            if pat.search(body):
                return True, f"body matches noise pattern /{pat.pattern}/"

    if 0 < len(body) < 300 and not substantive_title:
        non_word = 0
        for ch in body:
            is_alnum = re.match(r"[\w\d]", ch, re.UNICODE) is not None
            is_space = ch.isspace()
            if not is_alnum and not is_space:
                non_word += 1
        if non_word / max(len(body), 1) > 0.5:
            return True, "body is mostly symbols/emoji"

    return False, ""
