#!/usr/bin/env python3
"""No-network IPv4/IPv6 Cloudflare DNS change planner. NEVER modifies DNS.

Use only after observing the local host's public IPv6; this file is safe for
offline planning and tests. DNS update execution is deliberately absent.
"""
from __future__ import annotations
import argparse
import ipaddress
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/localDualStackGatewayV1.json"
HOST = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$")
PROTECTED = {"eggiebagelface.art", "mcp.eggiebagelface.art",
             "system.eggiebagelface.art", "assets.eggiebagelface.art",
             "art.eggiebagelface.art", "ai.eggiebagelface.art"}


def load_policy():
    return json.loads(POLICY.read_text(encoding="utf-8"))


def public_ip(value: str, family: int) -> str:
    """Refuse LAN, ULA, mapped, 6to4, Teredo, documentation and ambiguous IPs."""
    if type(value) is not str:
        raise ValueError("IP input must be a string")
    try:
        ip = ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValueError("invalid IP address") from exc
    if ip.version != family or not ip.is_global:
        raise ValueError("only a globally routable public IP of the requested family is allowed")
    if family == 6 and (ip.ipv4_mapped is not None or ip.sixtofour is not None
                         or ip.teredo is not None):
        raise ValueError("transition and mapped IPv6 addresses are not accepted")
    return ip.compressed


def candidate_hostname(fqdn: str, zone: str) -> str:
    if type(fqdn) is not str or len(fqdn) > 253:
        raise ValueError("invalid hostname")
    hostname = fqdn.rstrip(".").lower()
    if not HOST.fullmatch(hostname) or not hostname.endswith("." + zone):
        raise ValueError("hostname is not an approved-zone subdomain")
    if hostname in PROTECTED:
        raise ValueError("existing Canon hostname must not be altered by DDNS planner")
    return hostname


def plan(fqdn: str, ipv6: str, ipv4: str | None = None) -> dict:
    policy = load_policy()
    dns = policy["dns"]
    if dns["dynamicUpdate"]["execution"] != "DRY_RUN_OFFLINE_ONLY" or dns["dynamicUpdate"]["automatedProviderWrites"]:
        raise ValueError("mutating dynamic DNS policy forbidden")
    host = candidate_hostname(fqdn, dns["zone"])
    records = [{"type": "AAAA", "name": host, "content": public_ip(ipv6, 6)}]
    if ipv4 is not None:
        records.append({"type": "A", "name": host, "content": public_ip(ipv4, 4)})
    return {
        "schema": "luhmOs.dynamicDnsDryRun.v1",
        "status": "PROPOSAL_ONLY_NOT_APPLIED",
        "sourceScope": policy["schema"],
        "hostname": host,
        "records": records,
        "noIpv4ToIpv6DnsRedirect": True,
        "noCnameCoexistence": True,
        "noCertificateGenerated": True,
        "noCloudflareApiCall": True,
        "crown": "STOP",
    }


def self_test():
    # These test-only public addresses are not asserted to be owned by LuHm.
    ok = plan("candidate.eggiebagelface.art", "2606:4700:4700::1111", "1.1.1.1")
    assert [v["type"] for v in ok["records"]] == ["AAAA", "A"]
    assert plan("new.eggiebagelface.art", "2606:4700:4700::1111")["crown"] == "STOP"
    bad_address = [
        "::1", "::", "fe80::1", "fc00::1", "fd12::123", "ff02::1",
        "2001:db8::1", "::ffff:8.8.8.8", "2002:c000:0201::1",
        "2001:0000:4136:e378:8000:63bf:3fff:fdd2", "127.0.0.1",
        "192.168.1.1", "not-an-ip"
    ]
    for address in bad_address:
        try:
            public_ip(address, 6)
        except ValueError:
            continue
        raise AssertionError("unsafe address accepted: " + address)
    bad_v4 = ["127.0.0.1", "10.0.0.1", "192.168.1.1", "172.16.2.3", "169.254.1.1", "198.51.100.3", "2606:4700:4700::1111"]
    for address in bad_v4:
        try:
            public_ip(address, 4)
        except ValueError:
            continue
        raise AssertionError("unsafe IPv4 accepted: " + address)
    bad_host = [
        "system.eggiebagelface.art", "mcp.eggiebagelface.art",
        "art.eggiebagelface.art", "eggiebagelface.art",
        "system.eggiebagelface.art.evil.test",
        "noteggiebagelface.art", "localhost", "x..eggiebagelface.art",
        "evil/host.eggiebagelface.art"
    ]
    for hostname in bad_host:
        try:
            candidate_hostname(hostname, "eggiebagelface.art")
        except ValueError:
            continue
        raise AssertionError("unsafe host accepted: " + hostname)
    assert "requests" not in globals() and "urllib" not in globals()
    print("PASS_DDNS_OFFLINE_PLANNER_2_POSITIVE_29_NEGATIVE")


def main():
    parser = argparse.ArgumentParser(description="LuHm DNS candidate planner. No network or writes.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fqdn", help="future separate, owner-approved DNS-only hostname")
    parser.add_argument("--ipv6", help="locally observed global IPv6 address, NEVER inferred")
    parser.add_argument("--ipv4", help="optional real, reachable public IPv4 origin")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.fqdn and args.ipv6:
        print(json.dumps(plan(args.fqdn, args.ipv6, args.ipv4), sort_keys=True, indent=2))
    else:
        parser.error("pass --self-test, or both --fqdn and --ipv6; NO --apply action exists")


if __name__ == "__main__":
    main()
