#!/usr/bin/env python3
"""Read-only forward DNS evidence for LuHm Canon FQDNs; PTR is NOT a namespace alias.

Queries publicly accessible DNS-over-HTTPS only. Never writes Cloudflare DNS,
touches a private network, provision reverse zones, or claims origin TLS/health.
"""
from __future__ import annotations
import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/fourServiceCompatibilityCanonV1.json"
TYPES = ("NS", "SOA", "A", "AAAA", "CNAME")
KNOWN = {"NS": 2, "SOA": 6, "A": 1, "AAAA": 28, "CNAME": 5}
DOM = re.compile(r"^[a-z0-9-]+(?:\.[a-z0-9-]+)+$")


def canonical_hostname(value: str) -> str:
    if type(value) is not str or len(value) > 253:
        raise ValueError("FQDN_NOT_VALID")
    value = value.rstrip(".").lower()
    if not DOM.fullmatch(value) or any(len(x) > 63 or x.startswith("-") or x.endswith("-") for x in value.split(".")):
        raise ValueError("FQDN_NOT_VALID")
    return value


def dns_google_query(hostname: str, record_type: str, *, timeout: float = 4.0) -> dict:
    hostname = canonical_hostname(hostname)
    if record_type not in KNOWN:
        raise ValueError("UNSUPPORTED_RECORD_TYPE")
    query = urllib.parse.urlencode({"name": hostname, "type": record_type, "cd": "false"})
    request = urllib.request.Request(
        "https://dns.google/resolve?" + query,
        headers={"Accept": "application/dns-json", "User-Agent": "LuHmOS-Canon-ReadOnly-Audit/1"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read(50_000)
    parsed = json.loads(payload)
    if type(parsed) is not dict or type(parsed.get("Status")) is not int:
        raise ValueError("UNTRUSTED_DOH_RESPONSE")
    rows = parsed.get("Answer", [])
    if not isinstance(rows, list):
        raise ValueError("BAD_DOH_ANSWER")
    records = [str(row.get("data", ""))[:512] for row in rows
               if isinstance(row, dict) and row.get("type") == KNOWN[record_type]]
    return {"rcode": parsed["Status"], "answers": records[:30]}


def inspect(data: dict, resolver=dns_google_query) -> dict:
    fqdn = data["fqdn"]
    ns = {}
    zone = canonical_hostname(fqdn["zone"])
    for typ in ("NS", "SOA"):
        try:
            ns[typ] = resolver(zone, typ)
        except (OSError, ValueError, TimeoutError) as err:
            ns[typ] = {"status": "UNKNOWN", "errorType": type(err).__name__}
    results = []
    for row in fqdn["forward"]:
        host = canonical_hostname(row["fqdn"])
        checks = {}
        for typ in ("A", "AAAA", "CNAME"):
            try:
                checks[typ] = resolver(host, typ)
            except (OSError, ValueError, TimeoutError) as err:
                checks[typ] = {"status": "UNKNOWN", "errorType": type(err).__name__}
        observed = any(checks[typ].get("answers") for typ in ("A", "AAAA", "CNAME"))
        observed_empty = all(checks[typ].get("rcode") == 0 and
                             not checks[typ].get("answers") for typ in ("A", "AAAA", "CNAME"))
        expected = fqdn["publicMcpOrigin"] + "."
        cname_answers = checks["CNAME"].get("answers", [])
        candidate_cname_match = (expected in cname_answers) if row["id"] == "publicMcp" else None
        results.append({
            "id": row["id"], "hostname": host, "sourceKind": row["kind"],
            "forwardEvidence": ("OBSERVED_DNS_ANSWERS_NOT_TLS_OR_HOST_PROOF" if observed else
                                "OBSERVED_NO_FORWARD_A_AAAA_CNAME" if observed_empty else
                                "UNVERIFIED_FORWARD"),
            "candidateMcpCnameTargetMatch": candidate_cname_match,
            "records": checks,
        })
    reverse = fqdn["reversedLabelNamespace"]
    ns_answers = ns.get("NS", {}).get("answers", [])
    ns_matches_provider = bool(ns_answers) and all(
        value.lower().endswith(".ns.cloudflare.com.") for value in ns_answers
    )
    return {
        "schema": "luhmOs.fqdnForwardReverseProbe.v1",
        "zone": zone,
        "nameserverAndSoaEvidence": ns,
        "nsMatchesConfiguredProviderPattern": ns_matches_provider,
        "forward": results,
        "internalReverseLabels": {
            "source": reverse["forward"], "resolvedIdentity": reverse["reverse"],
            "isDnsRecord": False, "isPtrRecord": False,
        },
        "ipPtr": {
            "status": "SKIPPED_SHARED_IP_PREFIX_NOT_OWNED",
            "provisioningAttempted": False,
        },
        "tlsAndMcpHostVerification": "NOT_CHECKED",
        "cloudflareApiUsed": False, "dnsChanges": False,
        "overallNetworkReady": "UNVERIFIED_REQUIRES_OWNER_ZONE_AND_TLS_MCP_PROOF",
        "crownStatus": "STOP",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true", help="Read-only public DNS-over-HTTPS")
    parser.add_argument("--output", type=Path, help="Sanitized JSON receipt path")
    args = parser.parse_args()
    data = json.loads(POLICY.read_text(encoding="utf-8"))
    if args.probe:
        result = inspect(data)
    else:
        result = {
            "schema": "luhmOs.fqdnForwardReverseProbe.v1",
            "status": "DRY_RUN_ONLY_NO_DNS_QUERIED",
            "hosts": [canonical_hostname(row["fqdn"]) for row in data["fqdn"]["forward"]],
            "reverseLabel": data["fqdn"]["reversedLabelNamespace"]["reverse"],
            "ptrQueried": False, "cloudflareApiUsed": False,
            "tlsAndMcpHostVerification": "NOT_CHECKED", "crownStatus": "STOP",
        }
    report = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
