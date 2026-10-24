#!/usr/bin/env python3
"""Google AI + Cloudflare edge read-only readiness, exact LuHm source.

No generative inference, no token printing, no Cloudflare configuration changes.
The direct MCP host check uses HEAD only and does not prove MCP session support.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    "doctrine/studioCompatibilityFastMeshV1.json",
    "doctrine/providerEconomyV1.json",
    "doctrine/apiSpineV1.json",
    "doctrine/cloudflareAirTrafficControllerV1.json",
    "doctrine/cloudflareLumOrchestrationV1.json",
    "doctrine/companyWideOperationalQuarantineV1.json",
)
GOOGLE_MODELS = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1"
DNS_ENDPOINT = "https://cloudflare-dns.com/dns-query?" + urlencode(
    {"name": "mcp.eggiebagelface.art", "type": "CNAME"})
MCP_ENDPOINT = "https://luhm-os-harness-green.onrender.com/mcp"
SHA = re.compile(r"^[a-f0-9]{40}$")


def policies(root: Path) -> dict:
    return {name: json.loads((root / name).read_text(encoding="utf-8"))
            for name in SOURCE_FILES}


def check_contract(docs: dict) -> list[str]:
    errors = []
    def need(value: bool, message: str) -> None:
        if not value:
            errors.append(message)
    layer, economy, spine, edge, orchestration, hold = (docs[x] for x in SOURCE_FILES)
    priorities = layer.get("compatibilityPriority", [])
    need([(x.get("priority"), x.get("id")) for x in priorities]
         == [(1, "chatGptOpenAi"), (2, "github")],
         "COMPATIBILITY_LAYER_ORDER")
    g = layer.get("workhorse", {}).get("googleAi", {})
    big = economy.get("bigBrother", {})
    api = spine.get("providers", {}).get("googleAi", {})
    need(g.get("providerId") == big.get("providerId") == api.get("providerId") == "googleAi",
         "GOOGLE_PROVIDER_ID")
    need(g.get("adapterId") == api.get("adapterId") == "bigBrother",
         "GOOGLE_ADAPTER")
    need(g.get("permittedBillableCalls") is False, "GOOGLE_NO_UNPROVEN_SPENDING")
    need(g.get("routesThrough") == "lum" and big.get("authority") == "candidateEvidenceOnly",
         "LUM_OWNS_ROUTING")
    need(edge.get("provider") == "cloudflare"
         and edge.get("authorityBoundary", {}).get("aiProvider") is False
         and edge.get("authorityBoundary", {}).get("crownAuthority") is False,
         "CLOUDFLARE_NETWORK_ONLY")
    mcp = edge.get("lanes", {}).get("publicChatPluginMcp", {})
    public = orchestration.get("trafficLanes", {}).get("publicMcp", {})
    need(mcp.get("currentEndpoint") == MCP_ENDPOINT and
         public.get("origin", "") + public.get("path", "") == MCP_ENDPOINT,
         "EXACT_DIRECT_MCP_ORIGIN")
    need(mcp.get("cloudflareDependencyForCurrentEndpoint") is False
         and mcp.get("tunnelForThisLane") is False
         and public.get("cloudflareProxy") == "OFF_UNTIL_COMPAT_PROOF"
         and public.get("cacheMcpRequests") is False,
         "MCP_DIRECT_NO_PROXY_NO_CACHE")
    need(mcp.get("bootstrapRecord", {}).get("proxied") is False,
         "CLOUDFLARE_NO_UNPROVEN_PROXY")
    need(hold.get("state") == "QUARANTINED"
         and hold.get("registeredCount") == 15
         and hold.get("activeTaskWorkersAllowed") is False
         and hold.get("crownStatus") == "STOP",
         "MESH_QUARANTINE")
    return errors


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def request_status(url: str, *, method: str = "GET", api_key: str | None = None) -> tuple[int, bytes]:
    """Bounded, allowlisted HTTPS requests only. Never log returned error bodies."""
    if url not in (GOOGLE_MODELS, DNS_ENDPOINT, MCP_ENDPOINT):
        raise ValueError("RED_UNAPPROVED_PROBE_ENDPOINT")
    headers = {"User-Agent": "LuHm-ReadOnly-Compatibility/1", "Cache-Control": "no-cache"}
    if url == DNS_ENDPOINT:
        headers["Accept"] = "application/dns-json"
    if url == MCP_ENDPOINT:
        headers["Accept"] = "application/json, text/event-stream"
    if api_key:
        if url != GOOGLE_MODELS:
            raise ValueError("RED_PROVIDER_KEY_ON_WRONG_ENDPOINT")
        headers["x-goog-api-key"] = api_key
    req = Request(url, headers=headers, method=method)
    try:
        with build_opener(NoRedirect()).open(req, timeout=9) as r:
            return r.status, r.read(16000)
    except HTTPError as error:
        return error.code, b""


def google_readiness(*, key: str | None = None, probe=None) -> dict:
    if not key:
        return {"state": "NOT_VERIFIED_NO_CREDENTIAL",
                "metadataApi": "models.list", "modelGenerationCalled": False,
                "modelMetadataAccessVerified": False,
                "identityAndEntitlementVerified": False,
                "billingEntitlementVerified": False, "costApproval": False}
    probe = probe or request_status
    try:
        code, body = probe(GOOGLE_MODELS, api_key=key)
        if code == 200:
            parsed = json.loads(body)
            observed = (isinstance(parsed, dict)
                        and isinstance(parsed.get("models"), list)
                        and bool(parsed["models"])
                        and all(isinstance(m.get("name"), str) and
                                m["name"].startswith("models/")
                                for m in parsed["models"]))
            state = "AUTHENTICATED_MODEL_METADATA" if observed else "UNVERIFIED_INVALID_MODEL_METADATA"
        else:
            state = "NOT_VERIFIED_API_HTTP_" + str(code)
    except (URLError, TimeoutError, OSError, ValueError, TypeError):
        state = "NOT_VERIFIED_NETWORK_OR_FORMAT"
    return {"state": state, "metadataApi": "models.list", "modelGenerationCalled": False,
            "modelMetadataAccessVerified": state == "AUTHENTICATED_MODEL_METADATA",
            "identityAndEntitlementVerified": False,
            "billingEntitlementVerified": False,
            "costApproval": False, "modelWorkerDeployed": False}


def cloudflare_readiness(*, probe=None) -> dict:
    probe = probe or request_status
    dns_state = "UNVERIFIED_DNS"
    origin_state = "UNVERIFIED_ORIGIN"
    try:
        code, body = probe(DNS_ENDPOINT)
        if code == 200:
            response = json.loads(body)
            if isinstance(response, dict) and response.get("Status") == 0:
                answers = response.get("Answer", [])
                dns_state = ("PUBLIC_CNAME_OBSERVED" if
                             isinstance(answers, list) and any(
                                 isinstance(x, dict) and x.get("type") == 5 for x in answers)
                             else "NO_PUBLIC_CNAME_OBSERVED")
            else:
                dns_state = "DNS_RESOLVER_NONZERO_OR_INVALID"
        else:
            dns_state = "DNS_HTTP_" + str(code)
    except (OSError, ValueError, TypeError):
        dns_state = "UNVERIFIED_DNS"
    try:
        code, _ = probe(MCP_ENDPOINT, method="HEAD")
        if 200 <= code < 300:
            origin_state = "ORIGIN_HTTP_REACHABLE_NOT_MCP_SESSION_PROOF"
        elif code in (400, 401, 403, 405, 406, 415):
            origin_state = "ORIGIN_PROTOCOL_BOUNDARY_REACHABLE_NOT_MCP_PROOF"
        elif code in (301, 302, 307, 308):
            origin_state = "ORIGIN_REDIRECT_NOT_MCP_PROOF"
        elif 500 <= code < 600:
            origin_state = "ORIGIN_SERVER_ERROR_" + str(code)
        else:
            origin_state = "ORIGIN_UNEXPECTED_HTTP_" + str(code)
    except (OSError, ValueError, TypeError):
        origin_state = "UNVERIFIED_ORIGIN"
    return {
        "dnsState": dns_state, "directMcpOrigin": origin_state,
        "cloudflareProxyEnabled": False, "edgeWorkerDeploymentVerified": False,
        "mcpSessionNegotiated": False, "cloudflareCacheMutation": False,
        "dnsChanged": False,
    }


def receipt(root: Path, source_ref: str, *, network: bool = False,
            credential_key: str | None = None, google_probe=None, edge_probe=None) -> dict:
    if not SHA.fullmatch(source_ref):
        raise ValueError("exact SHA required")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                   cwd=root, text=True, timeout=6).strip()
    if head != source_ref:
        raise ValueError("checkout does not match exact source")
    error = check_contract(policies(root))
    return {
        "schema": "luhmOs.providerAndEdgeReadiness.v1",
        "sourceRef": head, "observedAt": datetime.now(timezone.utc).isoformat(),
        "sourceContract": "RED_SOURCE" if error else "PASS_SOURCE_ONLY",
        "contractErrors": error,
        "compatibilityLayers": ["chatGptOpenAi", "github"],
        "workhorse": "googleAi",
        "edge": "cloudflare",
        "googleAi": (google_readiness(key=credential_key, probe=google_probe)
                     if network and not error else google_readiness()),
        "cloudflare": (cloudflare_readiness(probe=edge_probe) if network and not error else
                       {"dnsState": "NOT_PROBED", "directMcpOrigin": "NOT_PROBED",
                        "mcpSessionNegotiated": False, "cloudflareProxyEnabled": False}),
        "networkProbeAttempted": network and not bool(error),
        "googleAiGenerationExecuted": False,
        "liveProviderWorkers": "NOT_PROVEN",
        "chatGptHostInstalled": "NOT_PROVEN",
        "publicReleaseAuthorized": False,
        "agentActivationAuthorized": False,
        "executionAuthorized": False,
        "crownStatus": "STOP",
    }


def main() -> int:
    import os
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--probe-public", action="store_true")
    parser.add_argument("--probe-google-key", action="store_true",
                        help="Explicit metadata-only key probe. Never call generateContent.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    key = os.environ.get("GOOGLE_AI_API_KEY") if args.probe_google_key else None
    data = receipt(ROOT, args.source_ref, network=args.probe_public or args.probe_google_key,
                   credential_key=key)
    out = json.dumps(data, indent=2) + "\n"
    print(out)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    return 0 if data["sourceContract"] == "PASS_SOURCE_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
