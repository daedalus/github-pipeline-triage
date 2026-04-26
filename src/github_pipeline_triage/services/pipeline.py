"""End-to-end triage sync pipeline."""

from __future__ import annotations

from datetime import UTC, datetime

from github_pipeline_triage.adapters.gh import (
    fetch_author_history,
    fetch_issues,
    fetch_pr_diff,
    fetch_prs,
)
from github_pipeline_triage.core.classify import classify_severity, detect_noise
from github_pipeline_triage.core.duplicates import find_duplicates
from github_pipeline_triage.core.pr_suspicion import (
    analyze_pr_suspicion,
    cross_reference_modules,
    extract_linked_issues,
)
from github_pipeline_triage.core.types import (
    SyncOptions,
    SyncPayload,
)


async def run_sync(options: SyncOptions | None = None) -> SyncOptions:
    options = options or SyncOptions()
    use_cache = not options.no_cache
    repo = options.repo

    issues = await fetch_issues(repo, use_cache)
    prs = await fetch_prs(repo, use_cache)

    for issue in issues:
        issue.severity = classify_severity(issue)
        is_noise, reason = detect_noise(issue)
        issue.is_noise = is_noise
        issue.noise_reason = reason

        text = f"{issue.title}\n{issue.body}"
        issue.modules = cross_reference_modules(text, [])

    duplicates = find_duplicates(issues)

    for pr in prs:
        text = f"{pr.title}\n{pr.body}"
        pr.modules = cross_reference_modules(text, pr.files)
        pr.linked_issues = extract_linked_issues(pr)

        if not options.skip_diffs:
            diff = await fetch_pr_diff(pr.number, repo, use_cache)
            author_count = await fetch_author_history(pr.author, repo, use_cache)
            result = analyze_pr_suspicion(pr, diff, author_count)
            pr.suspicious_flags = result.hard_flags
            pr.suspicion_level = result.suspicion_level
            pr.context_notes = result.context_notes

    return SyncPayload(
        fetched_at=datetime.now(UTC).isoformat(),
        repo=repo,
        issues=issues,
        prs=prs,
        duplicates=duplicates,
    )
