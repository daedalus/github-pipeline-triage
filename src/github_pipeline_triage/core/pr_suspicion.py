"""PR suspicion analysis: red flags, sensitive paths, first-time authors."""

from __future__ import annotations

import re
from os.path import basename

from github_pipeline_triage.core.constants import (
    COMMON_WORD_MODULES,
    DIFF_RED_FLAGS,
    MEMPALACE_MODULES,
    MODULE_BARE_NAMES,
    SENSITIVE_PATHS,
)
from github_pipeline_triage.core.types import PR, SuspicionLevel, SuspicionResult

LEVEL_RANK: dict[SuspicionLevel, int] = {
    SuspicionLevel.NONE: 0,
    SuspicionLevel.LOW: 1,
    SuspicionLevel.MEDIUM: 2,
    SuspicionLevel.HIGH: 3,
    SuspicionLevel.CRITICAL: 4,
}


def max_level(a: SuspicionLevel, b: SuspicionLevel) -> SuspicionLevel:
    return a if LEVEL_RANK[a] >= LEVEL_RANK[b] else b


def cross_reference_modules(text: str, changed_files: list[str] = None) -> list[str]:
    changed_files = changed_files or []
    hits: set[str] = set()
    lower = text.lower()
    words = set(re.findall(r"\b\w+\b", lower))

    for mod in MEMPALACE_MODULES:
        if mod in lower:
            hits.add(mod)
            continue
        bare = mod[:-3] if mod.endswith(".py") else mod
        if bare in MODULE_BARE_NAMES and bare in words:
            hits.add(mod)

    for f in changed_files:
        base = basename(f)
        if base in MEMPALACE_MODULES:
            hits.add(base)

    if len(hits) == 1:
        only = next(iter(hits))
        if only in COMMON_WORD_MODULES:
            confirmed_by_file = any(basename(f) == only for f in changed_files)
            if not confirmed_by_file:
                return []

    return sorted(list(hits))


def extract_linked_issues(pr: PR) -> list[int]:
    text = f"{pr.title}\n{pr.body}"
    nums: set[int] = set()
    for m in re.finditer(r"#(\d+)", text):
        nums.add(int(m.group(1)))
    return sorted(list(nums))


def analyze_pr_suspicion(
    pr: PR,
    diff: str,
    author_merged_count: int,
) -> SuspicionResult:
    hard_flags: list[str] = []
    context_notes: list[str] = []
    level: SuspicionLevel = SuspicionLevel.NONE

    if author_merged_count == 0 and pr.state.value == "OPEN":
        context_notes.append("first-time contributor (no prior merged PRs)")
        pr.first_time_author = True

    for f in pr.files:
        for rule in SENSITIVE_PATHS:
            if rule.pattern.search(f):
                hard_flags.append(f"touches `{f}` — {rule.reason}")
                level = max_level(level, SuspicionLevel(rule.level))
                break

    if diff:
        added_lines: list[str] = []
        for line in diff.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                added_lines.append(line[1:])
        added_text = "\n".join(added_lines)

        for rule in DIFF_RED_FLAGS:
            for m in rule.pattern.finditer(added_text):
                snippet = m.group(0)[:70] if m.group(0) else ""
                if rule.exclude_if and rule.exclude_if.search(snippet):
                    continue
                hard_flags.append(f"diff contains {rule.reason}: `{snippet}`")
                level = max_level(level, SuspicionLevel(rule.level))
                break

    total_changes = pr.additions + pr.deletions
    if total_changes > 2000:
        hard_flags.append(f"very large diff: +{pr.additions}/-{pr.deletions}")
        level = max_level(level, SuspicionLevel.LOW)
    elif total_changes > 500:
        context_notes.append(f"large-ish diff (+{pr.additions}/-{pr.deletions})")

    if (
        pr.state.value == "OPEN"
        and total_changes > 300
        and len(pr.body) < 100
        and len(hard_flags) == 0
    ):
        context_notes.append(
            f"thin description ({len(pr.body)} chars) for "
            f"+{pr.additions}/-{pr.deletions}"
        )

    return SuspicionResult(
        hard_flags=hard_flags,
        context_notes=context_notes,
        suspicion_level=level,
    )
