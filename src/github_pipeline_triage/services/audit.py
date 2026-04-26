"""Terminal audit reports for PRs and noise."""

from __future__ import annotations

from github_pipeline_triage.core.types import PR, Issue, SuspicionLevel


def audit_prs(prs: list[PR]) -> str:
    lines: list[str] = []
    lines.append("## PR Suspicion Audit\n")

    critical = [p for p in prs if p.suspicion_level == SuspicionLevel.CRITICAL]
    high = [p for p in prs if p.suspicion_level == SuspicionLevel.HIGH]
    medium = [p for p in prs if p.suspicion_level == SuspicionLevel.MEDIUM]
    low = [p for p in prs if p.suspicion_level == SuspicionLevel.LOW]

    if critical:
        lines.append("\n🔴 Critical Flags:\n")
        for pr in critical:
            lines.append(f"\n  #{pr.number}: {pr.title}\n")
            for flag in pr.suspicious_flags:
                lines.append(f"    - {flag}\n")
            if pr.first_time_author:
                lines.append("    - ⚠️  First-time contributor\n")

    if high:
        lines.append("\n🟠 High Flags:\n")
        for pr in high:
            lines.append(f"\n  #{pr.number}: {pr.title}\n")
            for flag in pr.suspicious_flags:
                lines.append(f"    - {flag}\n")

    if medium:
        lines.append(f"\n🟡 Medium ({len(medium)} PRs)\n")
        for pr in medium[:20]:
            lines.append(f"  - #{pr.number}: {pr.title}\n")

    if low:
        lines.append(f"\n⚪ Large diffs ({len(low)} PRs, >2000 changes)\n")
        for pr in low[:10]:
            lines.append(f"  - #{pr.number}: +{pr.additions}/-{pr.deletions}\n")

    return "".join(lines)


def noise_report(issues: list[Issue]) -> str:
    lines: list[str] = []
    lines.append("## Noise Candidates\n")

    noise = [i for i in issues if i.is_noise]
    lines.append(f"\nTotal noise candidates: {len(noise)}\n\n")

    for issue in noise[:50]:
        lines.append(f"- #{issue.number}: {issue.title}\n")
        lines.append(f"  Reason: {issue.noise_reason}\n")

    return "".join(lines)
