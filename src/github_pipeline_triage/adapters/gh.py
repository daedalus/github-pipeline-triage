"""GitHub CLI wrappers using the `gh` command."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from github_pipeline_triage.core.types import PR, Issue, IssueState, PrState


async def run_gh(args: list[str]) -> tuple[str, int]:
    proc = await asyncio.create_subprocess_exec(
        "gh", *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode(), proc.returncode or 0


async def gh_json[T](
    args: list[str],
    cache_name: str | None,
    use_cache: bool,
    repo: str,
) -> T:
    from github_pipeline_triage.adapters.cache import (
        cache_fresh,
        cache_path,
        read_cached_json,
        write_cached_json,
    )

    if cache_name and use_cache:
        safe_repo = re.sub(r"[^a-zA-Z0-9_-]", "_", repo)
        path = cache_path(f"{safe_repo}_{cache_name}")
        if cache_fresh(path):
            return await read_cached_json(path)

    stdout, code = await run_gh(args)
    if code != 0:
        raise RuntimeError(f"gh {' '.join(args)} exited with code {code}")

    data = json.loads(stdout.strip()) if stdout.strip() else []
    if cache_name:
        safe_repo = re.sub(r"[^a-zA-Z0-9_-]", "_", repo)
        await write_cached_json(cache_path(f"{safe_repo}_{cache_name}"), data)
    return data


async def gh_text(
    args: list[str],
    cache_name: str | None,
    use_cache: bool,
    repo: str,
) -> str:
    from github_pipeline_triage.adapters.cache import (
        cache_fresh,
        cache_path,
        read_cached_text,
        write_cached_text,
    )

    if cache_name and use_cache:
        safe_repo = re.sub(r"[^a-zA-Z0-9_-]", "_", repo)
        path = cache_path(f"{safe_repo}_{cache_name}")
        if cache_fresh(path):
            return await read_cached_text(path)

    stdout, code = await run_gh(args)
    if code != 0:
        return ""
    if cache_name:
        safe_repo = re.sub(r"[^a-zA-Z0-9_-]", "_", repo)
        await write_cached_text(cache_path(f"{safe_repo}_{cache_name}"), stdout)
    return stdout


def new_issue(raw: dict[str, Any]) -> Issue:
    return Issue(
        number=raw["number"],
        title=raw.get("title") or "",
        state=IssueState(raw["state"]),
        labels=[l["name"] for l in raw.get("labels", [])],
        author=raw.get("author", {}).get("login", "—") if raw.get("author") else "—",
        body=raw.get("body") or "",
        created_at=raw.get("createdAt", ""),
        closed_at=raw.get("closedAt"),
    )


def new_pr(raw: dict[str, Any]) -> PR:
    return PR(
        number=raw["number"],
        title=raw.get("title") or "",
        state=PrState(raw["state"]),
        labels=[l["name"] for l in raw.get("labels", [])],
        author=raw.get("author", {}).get("login", "—") if raw.get("author") else "—",
        body=raw.get("body") or "",
        branch=raw.get("headRefName") or "",
        created_at=raw.get("createdAt", ""),
        merged_at=raw.get("mergedAt"),
        closed_at=raw.get("closedAt"),
        files=[f["path"] for f in raw.get("files", [])],
        additions=raw.get("additions") or 0,
        deletions=raw.get("deletions") or 0,
    )


async def fetch_issues(repo: str, use_cache: bool = True) -> list[Issue]:
    raw: list[dict[str, Any]] = await gh_json(
        [
            "issue", "list", "--repo", repo, "--state", "all",
            "--limit", "500",
            "--json", "number,title,state,labels,author,body,createdAt,closedAt",
        ],
        "issues.json",
        use_cache,
        repo,
    )
    return [new_issue(r) for r in raw]


async def fetch_prs(repo: str, use_cache: bool = True) -> list[PR]:
    raw: list[dict[str, Any]] = await gh_json(
        [
            "pr", "list", "--repo", repo, "--state", "all",
            "--limit", "500",
            "--json",
            "number,title,state,labels,author,body,headRefName,"
            "createdAt,mergedAt,closedAt,additions,deletions,files",
        ],
        "prs.json",
        use_cache,
        repo,
    )
    return [new_pr(r) for r in raw]


async def fetch_pr_diff(pr_number: int, repo: str, use_cache: bool = True) -> str:
    return await gh_text(
        ["pr", "diff", str(pr_number), "--repo", repo],
        f"pr_{pr_number}_diff.txt",
        use_cache,
        repo,
    )


async def fetch_author_history(login: str, repo: str, use_cache: bool = True) -> int:
    if not login or login == "—":
        return 0
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", login)
    raw: list[dict[str, Any]] = await gh_json(
        [
            "pr", "list", "--repo", repo, "--state", "merged",
            "--author", login, "--limit", "50",
            "--json", "number",
        ],
        f"author_{safe}.json",
        use_cache,
        repo,
    )
    return len(raw)
