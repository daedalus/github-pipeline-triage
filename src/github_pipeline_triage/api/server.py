"""FastAPI server with REST and WebSocket endpoints."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from github_pipeline_triage.core.types import SyncOptions, SyncPayload
from github_pipeline_triage.services.pipeline import run_sync

from pydantic import BaseModel, Field


app = FastAPI(title="github-pipeline-triage", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.subscriptions: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket, topics: list[str]):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set(topics)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

    async def broadcast(self, topic: str, data: Any):
        message = json.dumps({"topic": topic, "data": data})
        for connection in self.active_connections:
            if topic in self.subscriptions.get(connection, set()):
                try:
                    await connection.send_text(message)
                except Exception:
                    pass


manager = ConnectionManager()

latest_payload: SyncPayload | None = None
latest_stats: dict[str, Any] = {}


class SyncInput(BaseModel):
    repo: str = Field(
        default="owner/repo", description="GitHub repository in owner/repo format"
    )
    skip_diffs: bool = Field(default=False, description="Skip PR diff analysis")
    no_cache: bool = Field(default=False, description="Skip cache and fetch fresh data")
    json_output: bool = Field(
        default=False, description="Output as JSON instead of markdown"
    )


@app.post("/api/sync")
async def sync_issues(input: SyncInput):
    """Run full triage sync on a GitHub repository."""
    try:
        options = SyncOptions(
            repo=input.repo,
            skip_diffs=input.skip_diffs,
            no_cache=input.no_cache,
        )
        payload = await run_sync(options)

        if input.json_output:
            return payload.model_dump()

        issues = payload.issues
        prs = payload.prs

        critical = [
            i for i in issues if i.severity.value == "critical" and not i.is_noise
        ]
        high = [i for i in issues if i.severity.value == "high" and not i.is_noise]
        normal = [i for i in issues if i.severity.value == "normal" and not i.is_noise]
        noise = [i for i in issues if i.is_noise]

        result = {
            "repo": payload.repo,
            "fetched_at": payload.fetched_at,
            "critical": critical[:20],
            "high": high[:20],
            "normal": normal[:10],
            "noise": noise,
            "suspicious_prs": [p for p in prs if p.suspicion_level.value != "none"][
                :20
            ],
            "duplicates": payload.duplicates,
            "total_issues": len(issues),
            "total_prs": len(prs),
        }
        return result

    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)}"}


class AuditPRsInput(BaseModel):
    repo: str = Field(
        default="owner/repo", description="GitHub repository in owner/repo format"
    )
    no_cache: bool = Field(default=False, description="Skip cache")


@app.post("/api/audit-prs")
async def audit_prs(input: AuditPRsInput):
    """Audit suspicious PRs in a GitHub repository."""
    try:
        options = SyncOptions(
            repo=input.repo, skip_diffs=False, no_cache=input.no_cache
        )
        payload = await run_sync(options)

        prs = payload.prs
        critical = [p for p in prs if p.suspicion_level.value == "critical"]
        high = [p for p in prs if p.suspicion_level.value == "high"]
        medium = [p for p in prs if p.suspicion_level.value == "medium"]
        low = [p for p in prs if p.suspicion_level.value == "low"]

        return {
            "critical": [
                {
                    "number": p.number,
                    "title": p.title,
                    "author": p.author,
                    "flags": p.suspicious_flags,
                }
                for p in critical
            ],
            "high": [{"number": p.number, "title": p.title} for p in high[:10]],
            "medium": len(medium),
            "low": len(low),
        }

    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)}"}


class NoiseReportInput(BaseModel):
    repo: str = Field(
        default="owner/repo", description="GitHub repository in owner/repo format"
    )
    no_cache: bool = Field(default=False, description="Skip cache")


@app.post("/api/noise-report")
async def noise_report(input: NoiseReportInput):
    """Report noise candidates in a GitHub repository."""
    try:
        options = SyncOptions(repo=input.repo, skip_diffs=True, no_cache=input.no_cache)
        payload = await run_sync(options)

        noise = [i for i in payload.issues if i.is_noise]
        return {
            "total": len(noise),
            "items": [
                {"number": i.number, "title": i.title, "reason": i.noise_reason}
                for i in noise[:50]
            ],
        }

    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)}"}


@app.post("/api/stats")
async def get_stats_endpoint(input: NoiseReportInput):
    """Get triage statistics for a GitHub repository."""
    try:
        options = SyncOptions(repo=input.repo, skip_diffs=True, no_cache=input.no_cache)
        payload = await run_sync(options)

        issues = payload.issues
        prs = payload.prs

        stats = {
            "repo": payload.repo,
            "total_issues": len(issues),
            "open_issues": len([i for i in issues if i.state.value == "OPEN"]),
            "closed_issues": len([i for i in issues if i.state.value == "CLOSED"]),
            "total_prs": len(prs),
            "open_prs": len([p for p in prs if p.state.value == "OPEN"]),
            "merged_prs": len([p for p in prs if p.state.value == "MERGED"]),
            "by_severity": {
                "critical": len([i for i in issues if i.severity.value == "critical"]),
                "high": len([i for i in issues if i.severity.value == "high"]),
                "normal": len([i for i in issues if i.severity.value == "normal"]),
            },
            "noise_count": len([i for i in issues if i.is_noise]),
            "suspicious_prs": len(
                [p for p in prs if p.suspicion_level.value != "none"]
            ),
            "duplicates": len(payload.duplicates),
            "fetched_at": payload.fetched_at,
        }

        return stats

    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)}"}


@app.get("/api/items")
async def get_items(
    kind: str = Query(None, description="Filter by kind: issue or pr"),
    severity: str = Query(None, description="Filter by severity"),
    state: str = Query(None, description="Filter by state"),
    noise: bool = Query(None, description="Filter noise issues"),
):
    if not latest_payload:
        return {"items": [], "total": 0}

    items = []
    for issue in latest_payload.issues:
        if kind and kind != "issue":
            continue
        if severity and issue.severity.value != severity:
            continue
        if state and issue.state.value != state:
            continue
        if noise is not None and issue.is_noise != noise:
            continue
        items.append(issue.model_dump())

    for pr in latest_payload.prs:
        if kind and kind != "pr":
            continue
        if severity and pr.suspicion_level.value != severity:
            continue
        if state and pr.state.value != state:
            continue
        items.append(pr.model_dump())

    return {"items": items, "total": len(items)}


@app.get("/api/stats")
async def get_stats():
    if not latest_payload:
        return latest_stats

    stats = {
        "total_issues": len(latest_payload.issues),
        "open_issues": len(
            [i for i in latest_payload.issues if i.state.value == "OPEN"]
        ),
        "closed_issues": len(
            [i for i in latest_payload.issues if i.state.value == "CLOSED"]
        ),
        "total_prs": len(latest_payload.prs),
        "open_prs": len([p for p in latest_payload.prs if p.state.value == "OPEN"]),
        "merged_prs": len([p for p in latest_payload.prs if p.state.value == "MERGED"]),
        "by_severity": {
            "critical": len(
                [i for i in latest_payload.issues if i.severity.value == "critical"]
            ),
            "high": len(
                [i for i in latest_payload.issues if i.severity.value == "high"]
            ),
            "normal": len(
                [i for i in latest_payload.issues if i.severity.value == "normal"]
            ),
        },
        "noise_count": len([i for i in latest_payload.issues if i.is_noise]),
        "suspicious_prs": len(
            [p for p in latest_payload.prs if p.suspicion_level.value != "none"]
        ),
        "duplicates": len(latest_payload.duplicates),
        "fetched_at": latest_payload.fetched_at,
    }

    return stats


@app.get("/api/activity")
async def get_activity(limit: int = Query(50, ge=1, le=200)):
    return {"activity": [], "total": 0}


@app.get("/api/maintainers")
async def get_maintainers():
    return {"maintainers": []}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, topics: str = Query("items,stats")):
    topic_list = topics.split(",") if topics else ["items", "stats", "activity"]
    await manager.connect(websocket, topic_list)

    try:
        await websocket.send_json(
            {
                "topic": "connected",
                "data": {"status": "connected", "topics": topic_list},
            }
        )

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60)
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "subscribe":
                    new_topics = message.get("topics", [])
                    manager.subscriptions[websocket].update(new_topics)

            except TimeoutError:
                await websocket.send_json({"type": "heartbeat"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def sync_and_broadcast(repo: str):
    global latest_payload, latest_stats

    try:
        options = SyncOptions(no_cache=True, repo=repo)
        latest_payload = await run_sync(options)
        latest_stats = {
            "total_issues": len(latest_payload.issues),
            "open_issues": len(
                [i for i in latest_payload.issues if i.state.value == "OPEN"]
            ),
        }

        await manager.broadcast("items", {"fetched_at": latest_payload.fetched_at})
        await manager.broadcast("stats", latest_stats)
        await manager.broadcast(
            "activity",
            {
                "event": "sync_complete",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )
    except Exception as e:
        print(f"Sync error: {e}")


async def periodic_sync(repo: str, interval_minutes: int = 15):
    while True:
        await asyncio.sleep(interval_minutes * 60)
        await sync_and_broadcast(repo)


async def run_server(host: str = "0.0.0.0", port: int = 8000, repo: str = "owner/repo"):
    import uvicorn

    asyncio.create_task(periodic_sync(repo))

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
