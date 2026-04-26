"""Core module exports."""

from .classify import classify_severity, detect_noise
from .duplicates import find_duplicates, similarity_ratio
from .pr_suspicion import analyze_pr_suspicion, cross_reference_modules
from .types import (
    PR,
    DuplicatePair,
    Issue,
    IssueState,
    PrState,
    Severity,
    SuspicionLevel,
    SuspicionResult,
    SyncPayload,
)

__all__ = [
    "Issue",
    "PR",
    "Severity",
    "SuspicionLevel",
    "IssueState",
    "PrState",
    "DuplicatePair",
    "SyncPayload",
    "SuspicionResult",
    "classify_severity",
    "detect_noise",
    "similarity_ratio",
    "find_duplicates",
    "analyze_pr_suspicion",
    "cross_reference_modules",
]
