#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."
ALLOWED = {"health:read", "status:read", "capabilities:read"}
FORBIDDEN = {"repo:write", "branch:write", "merge:write", "release:write", "sign:write", "publish:write", "secret:read", "secret:write", "device:control", "shell:execute"}


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def data(path: str) -> dict:
    value = json.loads(text(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a JSON object")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def audit() -> None:
    truth = data("doctrine/SOURCE_OF_TRUTH.json")
    doctrine = data("doctrine/fastApiCloudBoundary-20260927.json")
    policy = data("host/cloud/policy.json")
    app = text("host/cloud/main.py")
    pyproject = text("host/cloud/pyproject.toml")
    ignore = text("host/cloud/.fastapicloudignore")

    require(doctrine.get("status") == "READINESS_ONLY_NOT_DEPLOYED", "cloud doctrine must not imply live deployment")
    require(doctrine.get("sourceLaw") == LAW and policy.get("sourceLaw") == LAW, "cloud source law drift")
    ent = doctrine.get("entitlements", {})
    require(set(ent.get("allowed", [])) == ALLOWED, "cloud read entitlement drift")
    require(FORBIDDEN.issubset(set(ent.get("forbidden", []))), "cloud forbidden entitlement set incomplete")
    for key in ("greenAuthority", "promotionAuthority", "mutationAuthority"):
        require(ent.get(key) is False, f"cloud authority drift: {key}")
        require(policy.get(key) is False, f"runtime cloud policy authority drift: {key}")
    require(set(policy.get("allowedEntitlements", [])) == ALLOWED, "runtime policy entitlement drift")
    require(policy.get("providerSecretsAccepted") is False, "cloud bridge unexpectedly accepts provider secrets")
    require(policy.get("localMcpDirectReachabilityClaim") is False, "cloud bridge claims direct loopback reachability")

    auth = doctrine.get("authentication", {})
    require(auth.get("secretEnvironmentVariable") == "LUHM_CLOUD_READ_TOKEN", "cloud auth env drift")
    require(auth.get("secretInGit") is False and auth.get("failClosedWhenSecretMissing") is True, "cloud auth must fail closed")
    require("secrets.compare_digest" in app, "cloud bearer token compare must be constant-time")
    require('TOKEN_ENV = "LUHM_CLOUD_READ_TOKEN"' in app, "cloud token env missing")
    require('docs_url=None' in app and 'redoc_url=None' in app and 'openapi_url=None' in app, "interactive docs must remain disabled")
    require('@app.get("/healthz")' in app and '@app.get("/v1/status"' in app and '@app.get("/v1/capabilities"' in app, "required cloud GET endpoints missing")
    require("@app.post" not in app and "@app.put" not in app and "@app.patch" not in app and "@app.delete" not in app, "cloud bridge gained write endpoint")
    require("subprocess" not in app and "os.system" not in app and "shell=True" not in app, "cloud bridge gained shell execution")
    require("OPENAI_API_KEY" not in app and "FASTAPI_CLOUD_TOKEN" not in app, "provider/deploy secret reference entered bridge runtime")
    require("merge_pull_request" not in app and "production_sign" not in app, "cloud bridge gained consequential executor")

    require('fastapi[standard]' in pyproject, "FastAPI standard extra missing")
    require("fastapi-cli" not in pyproject, "fastapi-cli must not be installed directly")
    for pattern in (".env", "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore"):
        require(pattern in ignore, f"FastAPI Cloud ignore missing secret pattern: {pattern}")

    gate = truth.get("remainingExternalGates", {}).get("chatGptPrivateMcpConnection")
    require(gate == "PENDING_SECURE_TUNNEL_OR_APPROVED_HTTPS_BRIDGE", "source truth cloud/MCP external gate drift")
    require(doctrine.get("fastApiCloud", {}).get("appId") == "UNKNOWN", "hard-coded cloud app id entered doctrine")
    require(doctrine.get("fastApiCloud", {}).get("liveDeploymentReceipt") == "PENDING", "cloud doctrine falsely claims live receipt")

    secret_like = re.compile(r"(sk-proj-[A-Za-z0-9_-]{8,}|BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|AIza[A-Za-z0-9_-]{20,})")
    for path in ("doctrine/fastApiCloudBoundary-20260927.json", "host/cloud/policy.json", "host/cloud/main.py", "host/cloud/pyproject.toml"):
        require(secret_like.search(text(path)) is None, f"secret-like material detected in {path}")

    print("LUHM_FASTAPI_CLOUD_STATIC_GREEN LIVE_DEPLOYMENT=UNKNOWN")


if __name__ == "__main__":
    audit()
