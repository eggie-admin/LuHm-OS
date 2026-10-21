#!/usr/bin/env python3
"""GitHub-green exact-commit deploy of EXISTING Render sidecars.

Only GitHub Actions main runs after deterministic CI may call this.
Render native autoDeploy remains off. Private Google AI and 15 worker routes
remain disabled. No new Render resources, no keys in logs, no paid APIs.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "mcp": ("srv-daubsi1srm7s73bl5lh0", "https://luhm-os-harness-green.onrender.com"),
    "godot": ("srv-dauc8lnavr4c738kfd0g", "https://luhm-os-godot-harness-green.onrender.com"),
}
HEX40 = re.compile(r"[a-f0-9]{40}\Z")
TERMINAL_RED = {"build_failed", "update_failed", "pre_deploy_failed", "canceled"}
SCHEMA = "luhmOs.githubGatedRenderDeploy.v1"

def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf8"))

def policy() -> None:
    side = load("doctrine/githubRenderSidecarV1.json")
    company = load("doctrine/companyWideOperationalQuarantineV1.json")
    cabinet = load("doctrine/goddessCabinetLiveChatV1.json")
    google = load("doctrine/googleAiDeveloperEntitlementsV1.json")
    assert side["renderSidecar"]["autoDeployCanonical"] is False, "NATIVE_RENDER_AUTODEPLOY_MUST_REMAIN_OFF"
    assert side["strictFreeTier"]["required"] is True, "FREE_TIER_LOST"
    assert company["state"] == "QUARANTINED" and company["activeTaskWorkersAllowed"] is False, "WORKER_QUARANTINE_LOST"
    assert cabinet["status"] == "PROFESSOR_AUTHORIZED_SUPERVISED_CHAT_CAST", "CAST_NOT_AUTHORIZED"
    assert google["executionLaw"]["noAutomaticDeploy"] is True, "GOOGLE_AI_RUNTIME_GUARD_LOST"
    assert google["executionLaw"]["defaultAction"] == "DENY", "GOOGLE_AI_FAIL_CLOSED_LOST"

def transport(url: str, *, token: str, method: str = "GET", data: dict | None = None) -> dict:
    if not url.startswith("https://api.render.com/v1/services/") and not url.startswith(
        "https://api.github.com/repos/eggie-admin/LuHm-OS/"
    ):
        raise ValueError("UNEXPECTED_PROVIDER_URL")
    body = json.dumps(data, separators=(",", ":")).encode("utf8") if data is not None else None
    req = request.Request(url, method=method, data=body, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json" if "github.com" in url else "application/json",
        "Content-Type": "application/json",
        "User-Agent": "luhm-os-gated-deployer"
    })
    with request.urlopen(req, timeout=15) as response:
        if response.status not in (200, 201):
            raise ValueError("PROVIDER_HTTP_STATUS_" + str(response.status))
        raw = response.read(65537)
    if len(raw) > 65536:
        raise ValueError("RESPONSE_TOO_LARGE")
    return json.loads(raw)

def main_is_exact(source: str, github_token: str) -> None:
    result = transport(
        "https://api.github.com/repos/eggie-admin/LuHm-OS/git/ref/heads/main", token=github_token)
    if result.get("object", {}).get("sha") != source:
        raise ValueError("MAIN_SOURCE_DRIFT_STOP")

def run(service: str, source: str, token: str, *, poll_seconds: int = 540) -> dict:
    service_id, host = SOURCES[service]
    obj = transport("https://api.render.com/v1/services/" + service_id + "/deploys",
                    token=token, method="POST",
                    data={"commitId": source, "clearCache": "do_not_clear"})
    deploy_id = obj.get("id", "")
    if not re.fullmatch(r"dep-[a-z0-9]+", deploy_id):
        raise ValueError("DEPLOY_ID_INVALID")
    if obj.get("commit", {}).get("id") != source:
        raise ValueError("RENDER_COMMIT_ID_DRIFT")
    start = time.monotonic()
    state = "created"
    while time.monotonic() - start < poll_seconds:
        record = transport("https://api.render.com/v1/services/" + service_id +
                           "/deploys/" + deploy_id, token=token)
        state = record.get("status", "UNKNOWN")
        if record.get("commit", {}).get("id") != source:
            raise ValueError("RENDER_LIVE_SOURCE_MISMATCH")
        if state == "live":
            return {"service": service, "serviceId": service_id, "status": "LIVE_EXACT_SHA",
                    "sourceRef": source, "deployId": deploy_id, "url": host}
        if state in TERMINAL_RED:
            raise ValueError("RENDER_DEPLOY_FAILED_" + state)
        if state not in {"created","queued","build_in_progress","update_in_progress","pre_deploy_in_progress"}:
            raise ValueError("RENDER_UNKNOWN_DEPLOY_STATE")
        time.sleep(12)
    raise TimeoutError("RENDER_DEPLOY_PENDING_" + state)

def self_test() -> None:
    policy()
    assert set(SOURCES) == {"mcp", "godot"}
    assert not HEX40.fullmatch("c" * 39)
    assert HEX40.fullmatch("a" * 40)
    assert len(set(s[0] for s in SOURCES.values())) == 2
    assert all(h.startswith("https://") for _,h in SOURCES.values())
    for bad_url in ("http://api.render.com/v1/services/x", "https://evil.example/"):
        try:
            transport(bad_url, token="DUMMY")
            raise AssertionError("UNSAFE_NETWORK_ENDPOINT_ACCEPTED")
        except ValueError as exc:
            assert "UNEXPECTED_PROVIDER_URL" in str(exc)
    print("GREEN_GITHUB_GREEN_DEPLOY_SOURCE_GATES_7")
    print("NO_RUNTIME_PROVIDER_CREDENTIALS_OR_AUTONOMOUS_GOOGLE_AI_CALLS")

def main() -> None:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--self-test",action="store_true")
    args.add_argument("--source",default="")
    args.add_argument("--service",choices=["mcp","godot"],action="append",default=[])
    args.add_argument("--output",type=Path)
    opt=args.parse_args()
    if opt.self_test: self_test()
    if not opt.service: return
    if not HEX40.fullmatch(opt.source):
        raise SystemExit("RED_MISSING_EXACT_SOURCE_SHA")
    if os.environ.get("GITHUB_REF") != "refs/heads/main" or os.environ.get("GITHUB_SHA") != opt.source:
        raise SystemExit("RED_NO_MAIN_EXACT_SHA")
    policy()
    github_token=os.environ.get("GH_TOKEN","")
    render_token=os.environ.get("RENDER_API_KEY","")
    result={"schema":SCHEMA,"sourceRef":opt.source,"scope":"EXISTING_RENDER_SERVICES_ONLY",
            "companyQuarantinePreserved":True,"googleAiProviderCalled":False,
            "publicArtPromoted":False,"godotRuntimeProven":False,
            "results":[],"state":"AMBER_MISSING_RENDER_API_KEY"}
    if not github_token:
        raise SystemExit("RED_MISSING_GITHUB_READ_TOKEN")
    main_is_exact(opt.source,github_token)
    if render_token:
        result["state"]="BUILDING"
        for service in list(dict.fromkeys(opt.service)):
            result["results"].append(run(service,opt.source,render_token))
        result["state"]="LIVE_EXACT_SHA"
    else:
        print("AMBER_RENDER_API_KEY_NOT_CONFIGURED: no deployment requested")
    if opt.output:
        opt.output.parent.mkdir(parents=True,exist_ok=True)
        opt.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
