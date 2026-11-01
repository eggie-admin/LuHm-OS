#!/usr/bin/env python3
"""Private optional FastAPI surface for LuHm two-lane orchestration planning.

This is NOT a browser-served admin API, ChatGPT hosted runtime, Android Python
process, or replacement for the existing MCP harness. Default is host loopback;
all task endpoints require a strong secret sent only by trusted host-side clients.
"""
from __future__ import annotations

import os
import secrets
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[2]
API_DIR = ROOT / "host" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from luhmCanonOrchestration import CheckpointLedger, plan
from luhmCryptoBreathing import status as crypto_status
from luhmMariaDbReceipt import connection_plan as maria_db_plan
from luhmGpuVideoPlanner import status as gpu_video_status, plan as gpu_video_plan

TOKEN_HEADER = APIKeyHeader(name="X-LuHm-Control-Token", auto_error=False)


class TaskEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    taskId: str = Field(min_length=1, max_length=80)
    sourceRef: str = Field(pattern=r"^[0-9a-f]{40}$")
    scopeId: str = Field(min_length=1, max_length=80)
    goal: str = Field(min_length=1, max_length=2048)
    tier: int = Field(default=0, ge=0, le=3)



class VideoMinutePlanEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    taskId: str = Field(min_length=1, max_length=80)
    sourceRef: str = Field(pattern=r"^[0-9a-f]{40}$")
    scopeId: str = Field(min_length=1, max_length=80)
    seconds: int = Field(ge=1, le=3600)
    prompt: str = Field(min_length=1, max_length=1024)
    width: int = Field(default=1280, ge=256, le=3840)
    height: int = Field(default=720, ge=256, le=2160)
    fps: int = Field(default=24)
    modelShotSeconds: int = Field(default=6, ge=1, le=12)
    vramMode: str = Field(default="balanced")
    modelVramEstimateMiB: int = Field(default=8192, ge=1, le=1048576)


def create_app(*, admin_token: str | None = None,
               sqlite_path: str | None = None) -> FastAPI:
    token = os.environ.get("LUHM_ORCHESTRATION_CONTROL_TOKEN", "") if admin_token is None else admin_token
    if not isinstance(token, str):
        raise ValueError("host token must be a string")
    private_path = ":memory:" if sqlite_path is None else sqlite_path
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Create SQLite connection in the ASGI event-loop thread, not the import thread.
        app.state.ledger = CheckpointLedger(private_path)
        try:
            yield
        finally:
            app.state.ledger.close()

    app = FastAPI(
        title="LuHm Canon Orchestration (private host only)",
        docs_url=None, redoc_url=None, openapi_url=None,
        lifespan=lifespan,
    )

    async def authenticated(provided: str | None = Depends(TOKEN_HEADER)) -> None:
        if len(token) < 32:
            raise HTTPException(status_code=503, detail="HOST_AUTH_NOT_CONFIGURED")
        if not isinstance(provided, str) or not secrets.compare_digest(provided, token):
            raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    @app.middleware("http")
    async def no_cache(request: Any, call_next: Any):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        return {"status": "SOURCE_ONLY", "service": "luhm-canon-orchestration",
                "liveAgents": False, "liveMachine": False}

    @app.post("/v1/plan", dependencies=[Depends(authenticated)])
    def plan_route(body: TaskEnvelope) -> dict[str, Any]:
        try:
            return plan(body.taskId, body.sourceRef, body.scopeId, body.goal, body.tier)
        except ValueError:
            raise HTTPException(status_code=422, detail="INVALID_SCOPED_TASK") from None

    @app.post("/v1/checkpoint", dependencies=[Depends(authenticated)])
    async def checkpoint_route(body: TaskEnvelope) -> dict[str, Any]:
        try:
            return app.state.ledger.checkpoint(
                body.taskId, body.sourceRef, body.scopeId, body.goal, body.tier)
        except ValueError:
            raise HTTPException(status_code=409, detail="SCOPE_CONFLICT_OR_INVALID_TASK") from None

    @app.get("/v1/ledger", dependencies=[Depends(authenticated)])
    async def ledger_route(
        taskId: str = Query(min_length=1, max_length=80),
        sourceRef: str = Query(pattern=r"^[0-9a-f]{40}$"),
        scopeId: str = Query(min_length=1, max_length=80),
        limit: int = Query(default=20, ge=1, le=100),
    ) -> dict[str, Any]:
        try:
            return app.state.ledger.events(taskId, sourceRef, scopeId, limit)
        except ValueError:
            raise HTTPException(status_code=422, detail="INVALID_LEDGER_SCOPE") from None

    @app.get("/v1/crypto/status", dependencies=[Depends(authenticated)])
    async def crypto_status_route() -> dict[str, Any]:
        return crypto_status()

    @app.get("/v1/sql/mariadb-status", dependencies=[Depends(authenticated)])
    async def maria_db_status_route() -> dict[str, Any]:
        # No MariaDB connection, driver import, or SQL write happens here.
        return maria_db_plan()

    @app.get("/v1/video/gpu-status", dependencies=[Depends(authenticated)])
    async def gpu_video_status_route() -> dict[str, Any]:
        return gpu_video_status()

    @app.post("/v1/video/minute-plan", dependencies=[Depends(authenticated)])
    async def gpu_video_plan_route(body: VideoMinutePlanEnvelope) -> dict[str, Any]:
        try:
            return gpu_video_plan(
                task_id=body.taskId, source_ref=body.sourceRef,
                scope_id=body.scopeId, seconds=body.seconds, prompt=body.prompt,
                width=body.width, height=body.height, fps=body.fps,
                model_shot_seconds=body.modelShotSeconds,
                vram_mode=body.vramMode,
                model_vram_estimate_mib=body.modelVramEstimateMiB,
            )
        except ValueError:
            raise HTTPException(status_code=422, detail="INVALID_VIDEO_PLAN") from None

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    # Never use 0.0.0.0 for this private control-plane proof service.
    uvicorn.run(app, host="127.0.0.1", port=8791, proxy_headers=False)
