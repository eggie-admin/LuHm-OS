#!/usr/bin/env python3
"""Static/negative-control check. Never probes DNS, credentials, SQL, or production."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/firefoxFqdnSqlGatewayV1.json"
NGINX = ROOT / "deploy/nginx/firefox-fqdn-gateway.candidate.conf"

def require(ok: bool, reason: str) -> None:
    if not ok:
        raise AssertionError("RED_FIREFOX_FQDN_SQL_GATE: " + reason)

def check(policy: dict, conf: str) -> None:
    require(policy["schema"] == "luhmOs.firefoxFqdnSqlGateway.v1", "schema drift")
    require(policy["promotion"] is False and policy["crownStatus"] == "STOP", "promotion leak")
    require(policy["status"] == "SOURCE_CANDIDATE_NOT_DEPLOYED", "live overclaim")
    require(policy["domains"]["existingMcpRouteMustRemainUnchanged"] is True, "MCP rewired")
    require(policy["publicRouting"]["defaultDeny"] is True, "default permit")
    require(policy["publicRouting"]["loginActivation"].startswith("BLOCKED"), "unproven login")
    require(policy["publicRouting"]["apiFqdnActivation"].startswith("BLOCKED"), "unproven API login")
    require(policy["authentication"]["unauthenticatedPrivateAccess"] == "DENY", "auth bypass")
    require(policy["sql"]["networkExposure"] == "DENY", "SQL exposure")
    require(policy["sql"]["runtimeDdl"] == "DENY", "runtime SQL DDL")
    require(policy["sql"]["readiness"] == "NOT_PROVEN", "SQL overclaim")
    require(policy["sql"]["statements"] == "parameterized SQL only", "unsafe SQL contract")
    for marker in (
        "server_name eggiebagelface.art www.eggiebagelface.art",
        "server_name api.eggiebagelface.art",
        "ssl_protocols TLSv1.2 TLSv1.3",
        "auth_request /__luhm_auth;",
        "proxy_pass http://127.0.0.1:8787",
        "proxy_pass http://127.0.0.1:8789",
        "proxy_pass http://127.0.0.1:8790",
        'proxy_set_header Authorization "";',
        "proxy_set_header X-Forwarded-For $remote_addr;",
        "location / { return 404; }",
    ):
        require(marker in conf, "missing proxy control: " + marker)
    forbidden = (
        "proxy_pass http://0.0.0.0", "proxy_pass http://localhost:3306",
        "listen 3306", "listen 5432", "noTLSVerify", "ssl_verify off",
        "proxy_pass http://127.0.0.1:8788/mcp", "includeSubDomains",
        "ssl_client_verify off", "Access-Control-Allow-Origin *"
    )
    for needle in forbidden:
        require(needle not in conf, "forbidden network control: " + needle)
    require(conf.count("auth_request /__luhm_auth;") >= 3, "private routes not gated")
    require("location = /__luhm_auth {\n        internal;" in conf, "auth verifier externally reachable")
    for secret in ("password=", "client_secret=", "sk-proj-", "CF_API_TOKEN="):
        require(secret not in conf, "secret-like value in source")
    require(not policy["noBuildNoDeployNoDnsChange"] is False, "mutation state misrepresented")

def main() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    conf = NGINX.read_text(encoding="utf-8")
    check(policy, conf)
    # Negative controls: audit itself must fail when a material boundary weakens.
    def rejects(p: dict, c: str) -> bool:
        try:
            check(p, c)
        except AssertionError:
            return True
        return False
    changed = json.loads(json.dumps(policy))
    changed["sql"]["networkExposure"] = "ALLOW"
    require(rejects(changed, conf), "negative SQL control failed")
    changed = json.loads(json.dumps(policy))
    changed["promotion"] = True
    require(rejects(changed, conf), "negative Crown control failed")
    require(rejects(policy, conf.replace("127.0.0.1:8787", "0.0.0.0:8787")), "negative proxy control failed")
    require(rejects(policy, conf.replace("auth_request /__luhm_auth;", "")), "negative auth control failed")
    print("GREEN_FIREFOX_FQDN_SQL_STATIC_CANDIDATE; LIVE_DNS_TLS_LOGIN_SQL=UNVERIFIED; CROWN=STOP")

if __name__ == "__main__":
    main()
