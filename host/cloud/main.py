from __future__ import annotations

import json
import os
import secrets
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ROOT = Path(__file__).resolve().parent
POLICY = json.loads((ROOT / "policy.json").read_text(encoding="utf-8"))
TOKEN_ENV = "LUHM_CLOUD_READ_TOKEN"

app = FastAPI(
    title="LuHm OS Read-Only Bridge",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
security = HTTPBearer(auto_error=False)


@app.middleware("http")
async def harden_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


def require_read_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> None:
    expected = os.environ.get(TOKEN_ENV, "")
    if not expected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="bridge not provisioned")
    supplied = credentials.credentials if credentials is not None else ""
    if not supplied or not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "luhm-read-only-bridge"}


@app.get("/v1/capabilities", dependencies=[Depends(require_read_token)])
def capabilities() -> dict:
    return {
        "schema": POLICY["schema"],
        "entitlements": POLICY["allowedEntitlements"],
        "greenAuthority": False,
        "mutationAuthority": False,
        "promotionAuthority": False,
    }


@app.get("/v1/status", dependencies=[Depends(require_read_token)])
def bridge_status() -> dict:
    return {
        "schema": "luhm-os.cloud-status.v1",
        "status": "READ_ONLY_BRIDGE_READY",
        "sourceLaw": POLICY["sourceLaw"],
        "unknownIsNotGreen": POLICY["unknownIsNotGreen"],
        "greenAuthority": False,
        "mutationAuthority": False,
        "promotionAuthority": False,
        "localMcpDirectReachabilityClaim": False,
    }
