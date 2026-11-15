#!/usr/bin/env python3
"""Read-only LuHm external HTTPS chain, issuer, and expiry probe.

Uses the operating system trusted CA store, HTTPS SNI, and hostname checking.
Fails for invalid, expired, self-signed, non-Let's-Encrypt or too-short-lived
certificates. Only public certificate metadata is written to stdout.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import socket
import ssl
import sys


def probe(host: str, min_valid_days: int, timeout: float) -> dict:
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    with socket.create_connection((host, 443), timeout=timeout) as raw:
        with context.wrap_socket(raw, server_hostname=host) as sock:
            decoded = sock.getpeercert()
            der = sock.getpeercert(binary_form=True)
            if not decoded or not der:
                raise ValueError("missing trusted server certificate")
            issuer_parts = [
                str(key) + "=" + str(value)
                for rdn in decoded.get("issuer", ())
                for key, value in rdn
            ]
            issuer = ", ".join(issuer_parts)
            not_after = dt.datetime.fromtimestamp(
                ssl.cert_time_to_seconds(decoded["notAfter"]), dt.timezone.utc
            )
            not_before = dt.datetime.fromtimestamp(
                ssl.cert_time_to_seconds(decoded["notBefore"]), dt.timezone.utc
            )
            now = dt.datetime.now(dt.timezone.utc)
            remaining_days = (not_after - now).total_seconds() / 86400
            if "let's encrypt" not in issuer.lower() and "lets encrypt" not in issuer.lower():
                raise ValueError("certificate issuer is not Let's Encrypt: " + issuer)
            if remaining_days < min_valid_days:
                raise ValueError("certificate expires inside threshold")
            return {
                "hostname": host,
                "trustedChain": True,
                "hostnameMatches": True,
                "issuer": issuer,
                "san": [
                    value for kind, value in decoded.get("subjectAltName", ())
                    if kind == "DNS"
                ],
                "notBeforeUtc": not_before.isoformat(),
                "notAfterUtc": not_after.isoformat(),
                "remainingDays": round(remaining_days, 1),
                "leafSha256": hashlib.sha256(der).hexdigest(),
                "tlsVersion": sock.version(),
                "letsEncrypt": True,
                "status": "GREEN",
            }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", action="append", required=True,
                   help="DNS hostname to probe (repeat for each active public endpoint)")
    p.add_argument("--min-valid-days", type=int, default=14)
    p.add_argument("--timeout", type=float, default=10)
    p.add_argument("--json", action="store_true", help="Output JSON receipts")
    opts = p.parse_args()
    if opts.min_valid_days < 0 or opts.timeout <= 0:
        p.error("min-valid-days must be nonnegative; timeout positive")
    results = []
    failed = False
    for host in dict.fromkeys(opts.host):
        try:
            value = probe(host, opts.min_valid_days, opts.timeout)
        except (OSError, ssl.SSLError, ValueError, KeyError) as exc:
            value = {"hostname": host, "status": "RED", "error": str(exc)}
            failed = True
        results.append(value)
    if opts.json:
        print(json.dumps({"schema": "luhmOs.publicTlsTrustReceipt.v1",
                          "results": results, "allGreen": not failed}, indent=2))
    else:
        for item in results:
            print(item["hostname"], item["status"],
                  item.get("issuer", item.get("error", "")))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
