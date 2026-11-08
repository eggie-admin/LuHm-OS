#!/usr/bin/env python3
"""Offline 4×4×4×4 source-policy check for the LuHm-OS full ChatGPT plugin.
256 independently declared assertions, each mapped to existing CAST hex coordinates.
No live Site, Cloudflare, Google, Render or ChatGPT host claims; no key material read.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/fullChatGptPluginHex256V1.json"
CAST = ROOT / "doctrine/fnCastV1.yaml"  # JSON-compatible YAML 1.2 subset
IDENTITY = re.compile(r"^[a-z][A-Za-z0-9]*$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SURFACES = ("privateSite", "portablePlugin", "npmFrontend", "pythonMcp")
OPS = frozenset({"jsonEquals", "jsonIncludes", "jsonArrayLength", "textHas", "textLacks", "fileExists", "filesEqual"})
BLOCKED_COMPONENTS = frozenset({"node_modules", ".git", "dist", ".env", "__pycache__", "private", "secrets"})
ALLOW_ROOTS = frozenset({"doctrine", "plugins", "frontEnd", "host", "tools", ".github", "publicationSite"})


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_file(rel: str) -> Path:
    if not isinstance(rel, str) or not rel or rel.startswith(("/", ".")) and not rel.startswith(".github/"):
        raise ValueError("unsafe source path")
    value = Path(rel)
    parts = value.parts
    if not parts or parts[0] not in ALLOW_ROOTS or any(x in ("", "..", ".") or x in BLOCKED_COMPONENTS for x in parts):
        raise ValueError("unsafe source path")
    full = (ROOT / rel).resolve()
    if not full.is_relative_to(ROOT) or not full.is_file():
        raise ValueError("missing or escaping source file")
    if full.stat().st_size > 250_000:
        raise ValueError("source file outside bounded size")
    return full


def at(value, components):
    if not isinstance(components, list) or len(components) > 10 or not components:
        raise ValueError("invalid field path")
    for comp in components:
        if not isinstance(comp, str) or comp in ("__proto__", "__class__", ".."):
            raise ValueError("invalid field component")
        if isinstance(value, dict):
            if comp not in value:
                raise ValueError("missing source key")
            value = value[comp]
        elif isinstance(value, list) and comp.isdecimal():
            idx = int(comp)
            if idx >= len(value):
                raise ValueError("missing source list index")
            value = value[idx]
        else:
            raise ValueError("wrong source type")
    return value


def assert_check(check, cache: dict[str, str]) -> bool:
    if not isinstance(check, dict) or not IDENTITY.fullmatch(check.get("id", "")):
        return False
    op = check.get("op")
    if op not in OPS:
        return False
    try:
        file_name = check.get("file")
        path = safe_file(file_name)
        if op == "fileExists":
            return True
        if op == "filesEqual":
            return path.read_bytes() == safe_file(check.get("compareFile")).read_bytes()
        if file_name not in cache:
            cache[file_name] = path.read_text(encoding="utf-8")
        text = cache[file_name]
        if op == "textHas":
            needle = check.get("needle")
            return isinstance(needle, str) and 3 <= len(needle) <= 250 and needle in text
        if op == "textLacks":
            needle = check.get("needle")
            return isinstance(needle, str) and 3 <= len(needle) <= 250 and needle not in text
        if not file_name.endswith((".json", ".yaml")):
            return False
        result = at(json.loads(text), check.get("key"))
        expected = check.get("expected")
        if op == "jsonEquals":
            return type(result) is type(expected) and result == expected
        if op == "jsonIncludes":
            return isinstance(result, list) and expected in result
        if op == "jsonArrayLength":
            return isinstance(result, list) and isinstance(expected, int) and len(result) == expected
    except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        return False
    return False


def inspect(doc, cast):
    errors: list[str] = []
    def need(ok, why):
        if not ok:
            errors.append(why)
    axis = cast["castMatrix"]
    need(doc.get("schema") == "luhmOs.fullChatGptPluginHex256.v1"
         and doc.get("status") == "CANDIDATE_SOURCE_ONLY_NOT_HOST_RUNTIME", "sourceOnly")
    need(doc.get("product") == cast.get("displayBrand") == "LuHm-OS", "publicCaseSensitiveName")
    need(doc.get("foundation") == "doctrine/fnCastV1.yaml", "castSourceBinding")
    need(doc.get("axis", {}).get("stages") == axis["stages"]
         and doc.get("axis", {}).get("beats") == axis["beats"]
         and doc.get("axis", {}).get("tiers") == axis["tiers"], "actualCastAxis")
    need(len(axis["stages"]) == len(axis["beats"]) == len(axis["tiers"]) == 4, "4By4By4")
    need(doc.get("axis", {}).get("coordinatesPerSurface") == 64
         and doc.get("axis", {}).get("sourceAssertions") == 256, "4Times64SourceChecks")
    need([x.get("id") for x in doc.get("surfaces", [])] == list(SURFACES)
         and len(doc.get("checks", [])) == 4
         and [x.get("surface") for x in doc.get("checks", [])] == list(SURFACES), "fourProfiles")
    need(doc.get("digest", {}).get("algorithm") == "sha256"
         and doc.get("digest", {}).get("encoding") == "lowercaseHex64", "hex64Digest")
    need(doc.get("base64", {}).get("notEncryption") is True
         and doc.get("base64", {}).get("notAuditAxis") is True, "base64IsNotSecurity")
    need(doc.get("mayMutatePrivateSite") is False
         and doc.get("mayActivateAgents") is False
         and doc.get("mayPromoteCrown") is False
         and doc.get("crownStatus") == "STOP", "authorityFence")
    need(doc.get("npm", {}).get("publish") is False, "npmNoPublish")
    need(doc.get("runtimeProofs", {}).get("chatGptInlineHostMount") == "UNVERIFIED"
         and doc.get("runtimeProofs", {}).get("npmArtifactInstalled") == "NOT_INSTALLED", "hostNotProven")
    ids: set[str] = set()
    checks_by_profile = {}
    source_cache = {}
    for group in doc.get("checks", []):
        surface = group.get("surface", "UNKNOWN")
        checks = group.get("coordinates", [])
        need(len(checks) == 64, f"{surface}:64Cells")
        count = 0
        for index, rec in enumerate(checks):
            if index >= 64:
                break
            expected_stage = axis["stages"][index // 16]
            expected_beat = axis["beats"][(index % 16) // 4]
            expected_tier = axis["tiers"][index % 4]
            need(rec.get("hex") == f"0x{index:02X}"
                 and rec.get("stage") == expected_stage
                 and rec.get("beat") == expected_beat
                 and rec.get("tier") == expected_tier,
                 f"{surface}:{index:02X}:coordinateDrift")
            assertion = rec.get("assertion", {})
            cid = assertion.get("id", "")
            need(cid not in ids, f"{surface}:{index:02X}:duplicateAssertId")
            ids.add(cid)
            passed = assert_check(assertion, source_cache)
            if not passed:
                errors.append(f"{surface}:{index:02X}:{cid}:FAIL")
            else:
                count += 1
        checks_by_profile[surface] = count
    need(len(ids) == 256, "256DistinctAssertionIds")
    need(sum(checks_by_profile.values()) == 256, "all256SourceAssertionsPass")
    return errors, checks_by_profile


def self_test():
    doc, cast = load(CONTRACT), load(CAST)
    errors, counts = inspect(doc, cast)
    if errors:
        return errors, counts
    controls = []
    def reject(mutator):
        trial = deepcopy(doc)
        mutator(trial)
        bad, _ = inspect(trial, cast)
        controls.append(bool(bad))
    reject(lambda x: x["axis"].update(sourceAssertions=200))
    reject(lambda x: x["checks"][0]["coordinates"][0].update(hex="0xFF"))
    reject(lambda x: x["checks"][1]["coordinates"][1]["assertion"].update(id=x["checks"][0]["coordinates"][0]["assertion"]["id"]))
    reject(lambda x: x.update(crownStatus="GREEN"))
    reject(lambda x: x["checks"][2]["coordinates"][0]["assertion"].update(file="../../private/secrets.env"))
    reject(lambda x: x["runtimeProofs"].update(chatGptInlineHostMount="GREEN"))
    reject(lambda x: x["checks"][3]["coordinates"][0]["assertion"].update(expected="notTheTrueSource"))
    reject(lambda x: x["npm"].update(publish=True))
    if not all(controls):
        errors.append("negativeControlsMissing")
    return errors, counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-controls", action="store_true")
    args = parser.parse_args()
    errors, counts = self_test() if args.negative_controls else inspect(load(CONTRACT), load(CAST))
    digest = sha256(CONTRACT.read_bytes()).hexdigest()
    if not HEX64.fullmatch(digest):
        errors.append("sha256DigestMalformed")
    print(json.dumps({
        "schema": "luhmOs.fullChatGptPluginHexAuditReceipt.v1",
        "product": "LuHm-OS",
        "matrix": "4×4×4×4",
        "coordinates": 256,
        "passed": sum(counts.values()),
        "bySurface": counts,
        "manifestSha256": digest,
        "source": "CANDIDATE_ONLY",
        "liveSiteBackendVerified": False,
        "chatGptHostMountVerified": False,
        "cdnRuntimeVerified": False,
        "negativeControls": "8" if args.negative_controls and not errors else "UNVERIFIED",
        "errors": errors[:64],
        "crownStatus": "STOP"
    }, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
