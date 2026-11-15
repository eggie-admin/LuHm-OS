#!/usr/bin/env python3
"""LuHm Crown Cathedral: idempotent Cloudflare Email Routing setup.

Only owner-operated. Never logs tokens or a Gmail destination.
No DNS, nameserver, TLS, MX, SPF, DKIM, or DMARC mutation.
Default is read-only audit; writes require explicit command.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ZONE_NAME = "eggiebagelface.art"
ALIASES = (
    "admin", "web", "webmaster", "postmaster", "hostmaster",
    "security", "abuse", "support", "certs", "errors", "dmarc",
    "studios", "film", "art",
)


class RoutingError(RuntimeError):
    pass


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RoutingError("missing environment variable: " + name)
    return value


def api(method: str, path: str, body: dict | None = None) -> object:
    token = required("CLOUDFLARE_API_TOKEN")
    payload = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4" + path,
        data=payload,
        method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            output = json.load(resp)
    except urllib.error.HTTPError as exc:
        raise RoutingError("Cloudflare API HTTP " + str(exc.code)) from None
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RoutingError("Cloudflare API unavailable or invalid reply") from None
    if not output.get("success", False):
        codes = [str(e.get("code", "?")) for e in output.get("errors", [])]
        raise RoutingError("Cloudflare API error code(s): " + ",".join(codes))
    return output.get("result")


def list_pages(path: str) -> list[dict]:
    results: list[dict] = []
    page = 1
    while True:
        suffix = ("&" if "?" in path else "?") + "page=" + str(page) + "&per_page=50"
        token = required("CLOUDFLARE_API_TOKEN")
        req = urllib.request.Request(
            "https://api.cloudflare.com/client/v4" + path + suffix,
            headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.load(resp)
        except urllib.error.HTTPError as exc:
            raise RoutingError("Cloudflare API HTTP " + str(exc.code)) from None
        except (urllib.error.URLError, TimeoutError, ValueError):
            raise RoutingError("Cloudflare API unavailable or invalid reply") from None
        if not data.get("success", False) or not isinstance(data.get("result"), list):
            raise RoutingError("Cloudflare list request failed")
        batch = data["result"]
        results.extend(batch)
        pages = data.get("result_info", {}).get("total_pages", 0)
        if (pages and page >= pages) or (not pages and len(batch) < 50):
            break
        page += 1
        if page > 100:
            raise RoutingError("pagination bound exceeded")
    return results


def existing_recipient(rule: dict) -> str | None:
    for matcher in rule.get("matchers", []):
        if matcher.get("type") == "literal" and matcher.get("field") == "to":
            return str(matcher.get("value", "")).lower()
    return None


def audit_state(zone: str, account: str, destination: str) -> tuple[bool, bool, list[dict]]:
    status = api("GET", "/zones/" + zone + "/email/routing")
    if not isinstance(status, dict):
        raise RoutingError("unexpected routing settings")
    ready = status.get("status") == "ready" and status.get("enabled") is True
    addresses = list_pages("/accounts/" + account + "/email/routing/addresses")
    matched = [a for a in addresses if str(a.get("email", "")).lower() == destination.lower()]
    verified = any(bool(a.get("verified")) for a in matched)
    rules = list_pages("/zones/" + zone + "/email/routing/rules")
    print("Cloudflare Email Routing ready:", ready)
    print("Gmail destination verified:", verified)
    print("Existing custom routing rule count:", len(rules))
    print("Required alias count:", len(ALIASES))
    return ready, verified, rules


def check_mx(zone: str) -> None:
    path = "/zones/" + zone + "/dns_records?type=MX&name=" + urllib.parse.quote(ZONE_NAME)
    mx = list_pages(path)
    targets = [str(item.get("content", "")).rstrip(".").lower() for item in mx]
    if not targets or any(not t.endswith(".mx.cloudflare.net") for t in targets):
        raise RoutingError("MX does not exclusively target Cloudflare Email Routing; no writes")
    print("Existing Cloudflare MX records verified:", len(targets))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choices = parser.add_mutually_exclusive_group()
    choices.add_argument("--audit", action="store_true", help="Read-only default")
    choices.add_argument("--request-verification", action="store_true", help="Ask Cloudflare to send owner Gmail verification")
    choices.add_argument("--apply-rules", action="store_true", help="Add missing aliases only after Gmail verified and Cloudflare MX ready")
    args = parser.parse_args()
    account = required("CLOUDFLARE_ACCOUNT_ID")
    zone = required("CLOUDFLARE_ZONE_ID")
    destination = required("LUHM_MAIL_DESTINATION")
    if not destination.lower().endswith("@gmail.com"):
        raise RoutingError("destination must be the verified owner Gmail address")
    ready, verified, rules = audit_state(zone, account, destination)
    if args.request_verification:
        if verified:
            print("Gmail destination already verified; no action.")
        else:
            current = list_pages("/accounts/" + account + "/email/routing/addresses")
            if any(str(a.get("email", "")).lower() == destination.lower() for a in current):
                raise RoutingError("destination exists but is unverified; use Cloudflare dashboard to resend verification")
            api("POST", "/accounts/" + account + "/email/routing/addresses", {"email": destination})
            print("Cloudflare destination verification requested. Owner must approve the Gmail link.")
        return 0
    if args.apply_rules:
        if not ready or not verified:
            raise RoutingError("routing or destination is not verified; refusing writes")
        check_mx(zone)
        by_recipient: dict[str, list[dict]] = {}
        for rule in rules:
            addr = existing_recipient(rule)
            if addr:
                by_recipient.setdefault(addr, []).append(rule)
        pending = []
        for local in ALIASES:
            address = local + "@" + ZONE_NAME
            found = by_recipient.get(address, [])
            if len(found) > 1:
                raise RoutingError("duplicate rules for " + local + "; refuse to change")
            if found:
                actions = found[0].get("actions", [])
                expected = [{"type": "forward", "value": [destination]}]
                if actions != expected or found[0].get("enabled") is not True:
                    raise RoutingError("existing " + local + " rule differs; refuse to overwrite")
                print("Already configured:", local)
            else:
                pending.append((local, address))
        for local, address in pending:
            api("POST", "/zones/" + zone + "/email/routing/rules", {
                "name": "LuHm Crown Cathedral / " + local,
                "enabled": True,
                "matchers": [{"type": "literal", "field": "to", "value": address}],
                "actions": [{"type": "forward", "value": [destination]}],
            })
            print("Created routing alias:", local)
        print("Done creating missing rules. Independently test delivery for each alias.")
    else:
        print("Audit complete; no provider settings changed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RoutingError as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(2)
