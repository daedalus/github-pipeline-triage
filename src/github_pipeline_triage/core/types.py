"""Core domain types for github-pipeline-triage."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"


class SuspicionLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class IssueState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class PrState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    MERGED = "MERGED"


class Issue(BaseModel):
    number: int
    title: str
    state: IssueState
    labels: list[str] = Field(default_factory=list)
    author: str
    body: str
    created_at: str
    closed_at: str | None = None
    severity: Severity = Severity.NORMAL
    is_noise: bool = False
    noise_reason: str = ""
    modules: list[str] = Field(default_factory=list)

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["severity"] = self.severity.value
        data["state"] = self.state.value
        return data


class PR(BaseModel):
    number: int
    title: str
    state: PrState
    labels: list[str] = Field(default_factory=list)
    author: str
    body: str
    branch: str
    created_at: str
    merged_at: str | None = None
    closed_at: str | None = None
    files: list[str] = Field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    suspicious_flags: list[str] = Field(default_factory=list)
    suspicion_level: SuspicionLevel = SuspicionLevel.NONE
    context_notes: list[str] = Field(default_factory=list)
    modules: list[str] = Field(default_factory=list)
    linked_issues: list[int] = Field(default_factory=list)
    first_time_author: bool = False

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["state"] = self.state.value
        data["suspicion_level"] = self.suspicion_level.value
        return data


class DuplicatePair(BaseModel):
    a: int
    b: int
    similarity: float


class SyncPayload(BaseModel):
    fetched_at: str
    repo: str
    issues: list[Issue] = Field(default_factory=list)
    prs: list[PR] = Field(default_factory=list)
    duplicates: list[DuplicatePair] = Field(default_factory=list)


class SuspicionResult(BaseModel):
    hard_flags: list[str] = Field(default_factory=list)
    context_notes: list[str] = Field(default_factory=list)
    suspicion_level: SuspicionLevel = SuspicionLevel.NONE


class SyncOptions(BaseModel):
    skip_diffs: bool = False
    no_cache: bool = False
    repo: str = "owner/repo"
