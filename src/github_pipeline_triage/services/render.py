"""Markdown report generation for ISSUES.md."""

from __future__ import annotations

from github_pipeline_triage.core.types import (
    Severity,
    SyncPayload,
)


def render_issues_md(payload: SyncPayload) -> str:
    lines: list[str] = []
    lines.append("# Issues & PRs Triage Report")
    lines.append(f"\n*Fetched: {payload.fetched_at}*\n")

    critical = [i for i in payload.issues if i.severity == Severity.CRITICAL and not i.is_noise]
    high = [i for i in payload.issues if i.severity == Severity.HIGH and not i.is_noise]
    normal = [i for i in payload.issues if i.severity == Severity.NORMAL and not i.is_noise]
    noise = [i for i in payload.issues if i.is_noise]

    lines.append("## Issues by Severity\n")

    if critical:
        lines.append("### 🔴 Critical\n")
        for issue in critical:
            lines.append(f"- [#{issue.number}](https://github.com/{payload.repo}/issues/{issue.number}) **{issue.title}**\n")
            if issue.modules:
                lines.append(f"  - Modules: {', '.join(issue.modules)}\n")
            lines.append(f"  - Author: @{issue.author}\n")

    if high:
        lines.append("### 🟠 High\n")
        for issue in high:
            lines.append(f"- [#{issue.number}](https://github.com/{payload.repo}/issues/{issue.number}) **{issue.title}**\n")
            if issue.modules:
                lines.append(f"  - Modules: {', '.join(issue.modules)}\n")

    if normal:
        lines.append("### 🟡 Normal\n")
        for issue in normal[:50]:
            lines.append(f"- [#{issue.number}](https://github.com/{payload.repo}/issues/{issue.number}) {issue.title}\n")

    if noise:
        lines.append(f"\n## 📵 Noise ({len(noise)} marked)\n")
        for issue in noise[:10]:
            lines.append(f"- ~~#{issue.number}~~ {issue.title}\n")

    suspicious_prs = [p for p in payload.prs if p.suspicion_level.value != "none"]
    if suspicious_prs:
        lines.append("\n## ⚠️ Suspicious PRs\n")
        for pr in suspicious_prs:
            lines.append(f"- [#{pr.number}](https://github.com/{payload.repo}/pull/{pr.number}) **{pr.title}**\n")
            lines.append(f"  - Level: {pr.suspicion_level.value}\n")
            for flag in pr.suspicious_flags:
                lines.append(f"  - {flag}\n")

    if payload.duplicates:
        lines.append("\n## 🔗 Potential Duplicates\n")
        for dup in payload.duplicates:
            lines.append(f"- #{dup.a} ↔ #{dup.b} (similarity: {dup.similarity:.2%})\n")

    return "".join(lines)
