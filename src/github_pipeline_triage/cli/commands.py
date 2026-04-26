"""CLI commands for github-pipeline-triage."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from github_pipeline_triage.core.constants import DEFAULT_OUTPUT
from github_pipeline_triage.core.types import SyncOptions
from github_pipeline_triage.services.audit import audit_prs, noise_report
from github_pipeline_triage.services.pipeline import run_sync
from github_pipeline_triage.services.render import render_issues_md


async def cmd_sync(args: argparse.Namespace) -> int:
    options = SyncOptions(
        skip_diffs=args.skip_diffs,
        no_cache=args.no_cache,
        repo=args.repo,
    )
    payload = await run_sync(options)

    if args.json:
        print(json.dumps(payload.model_dump(), indent=2))
    else:
        md = render_issues_md(payload)
        output_path = Path(args.output) if args.output else DEFAULT_OUTPUT
        output_path.write_text(md)
        print(f"Report written to {output_path}")

    return 0


async def cmd_audit_prs(args: argparse.Namespace) -> int:
    options = SyncOptions(skip_diffs=False, no_cache=args.no_cache, repo=args.repo)
    payload = await run_sync(options)
    print(audit_prs(payload.prs))
    return 0


async def cmd_noise_report(args: argparse.Namespace) -> int:
    options = SyncOptions(skip_diffs=True, no_cache=args.no_cache, repo=args.repo)
    payload = await run_sync(options)
    print(noise_report(payload.issues))
    return 0


async def cmd_serve(args: argparse.Namespace) -> int:
    from github_pipeline_triage.api.server import run_server

    await run_server(host=args.host, port=args.port, repo=args.repo)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="github-pipeline-triage - Automated GitHub triage"
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPO", "owner/repo"),
        help="GitHub repo (owner/repo). Can also set GITHUB_REPO env var",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sync = sub.add_parser("sync", help="Run full sync and generate report")
    sync.add_argument("--json", action="store_true", help="Output JSON")
    sync.add_argument("--output", help="Output file path")
    sync.add_argument("--no-cache", action="store_true", help="Skip cache")
    sync.add_argument("--skip-diffs", action="store_true", help="Skip PR diff analysis")

    audit = sub.add_parser("audit-prs", help="Audit suspicious PRs")
    audit.add_argument("--no-cache", action="store_true", help="Skip cache")

    noise = sub.add_parser("noise-report", help="Show noise candidates")
    noise.add_argument("--no-cache", action="store_true", help="Skip cache")

    serve = sub.add_parser("serve", help="Start API server")
    serve.add_argument("--host", default="0.0.0.0", help="Host to bind")
    serve.add_argument("--port", type=int, default=8000, help="Port to bind")

    args = parser.parse_args()

    commands = {
        "sync": cmd_sync,
        "audit-prs": cmd_audit_prs,
        "noise-report": cmd_noise_report,
        "serve": cmd_serve,
    }

    return asyncio.run(commands[args.command](args))
