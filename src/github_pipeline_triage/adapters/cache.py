"""On-disk caching for GitHub API responses."""

from __future__ import annotations

import json
from pathlib import Path

from github_pipeline_triage.core.constants import CACHE_DIR, CACHE_TTL_MS

CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_path(name: str) -> Path:
    return CACHE_DIR / name


def cache_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    import time
    age = time.time() - path.stat().st_mtime
    return age < (CACHE_TTL_MS / 1000)


async def read_cached_json[T](path: Path) -> T:
    with open(path) as f:
        return json.load(f)


async def read_cached_text(path: Path) -> str:
    with open(path) as f:
        return f.read()


async def write_cached_json(path: Path, data: object) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


async def write_cached_text(path: Path, text: str) -> None:
    with open(path, "w") as f:
        f.write(text)
