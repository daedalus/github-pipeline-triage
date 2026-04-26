name: github-pipeline-triage
description: >
  Automated GitHub issue and PR triage system with heuristic classification.
  Triggers on requests to triage GitHub issues, analyze PRs for suspicious content,
  detect duplicates, or generate triage reports.
---

# github-pipeline-triage Skill

This skill provides tools for automated GitHub issue and PR triage.

## Usage

Use the MCP tools to interact with the triage system:

- `sync_issues` - Run full triage sync on any GitHub repo
- `audit_prs` - Audit suspicious PRs (red flags, first-time authors)
- `noise_report` - Report noise candidates
- `get_stats` - Get triage statistics

## Examples

- "Run triage on my repository" → use sync_issues with repo parameter
- "Find suspicious PRs" → use audit_prs with repo parameter
- "Show me noise issues" → use noise_report with repo parameter
- "Get statistics" → use get_stats with repo parameter
