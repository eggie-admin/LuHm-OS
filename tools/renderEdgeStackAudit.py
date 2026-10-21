#!/usr/bin/env python3
"""Fail-closed source checks for the existing Render Python/Godot/static split.

This does not imply Render dashboard settings or Cloudflare zone have changed.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GODOT_URL = "https://luhm-os-godot-harness-green.onrender.com/harness/godot-export/index.html"
OLD_URL = "https://luhm-os-harness-green.onrender.com/harness/godot-export/index.html"

def verify(blueprint: str, pocket: str, library: dict, front: dict, lock: dict, edge: dict) -> list[str]:
    failures = []
    def need(ok: bool, label: str) -> None:
        if not ok:
            failures.append(label)
    blocks = re.findall(r"(?m)^  - type: web\n(?:^(?!  - type: web).*(?:\n|$))*", blueprint)
    roles = {}
    for block in blocks:
        match = re.search(r"(?m)^    name: ([a-z0-9-]+)$", block)
        if match:
            roles[match.group(1)] = block
    need(len(blocks) == len(roles), "duplicate_render_service")
    names = {"luhm-os-harness-green", "luhm-os-godot-harness-green", "luhm-os-publication-site"}
    need(names.issubset(roles), "missing_existing_render_role")
    py = roles.get("luhm-os-harness-green", "")
    godot = roles.get("luhm-os-godot-harness-green", "")
    static = roles.get("luhm-os-publication-site", "")
    for name, text in (( "python", py), ("godot", godot), ("static", static)):
        need("autoDeployTrigger: off" in text, name + "_manual_release")
    need("runtime: python" in py and "pip install -r host/mcp/requirements.txt" in py, "python_origin")
    need("tools/buildGodotWebHarness.sh" not in py, "godot_build_coupled_to_mcp")
    need("runtime: python" in godot and "tools/buildGodotWebHarness.sh" in godot, "missing_godot_builder")
    need("runtime: static" in static and "staticPublishPath: publicationSite" in static, "missing_static_cdn")
    need("npm install" not in py and "npm install" not in godot, "npm_in_python_runtime")
    need("name: Cache-Control\n        value: no-cache" in static, "static_html_cache")
    need("name: X-Content-Type-Options\n        value: nosniff" in static, "static_nosniff")
    need(pocket.count(GODOT_URL) == 2 and OLD_URL not in pocket, "wrong_godot_service_link")
    need("<script src=" not in pocket and "<link rel=\"stylesheet\"" not in pocket, "external_runtime_cdn")
    need(front.get("private") is True and front.get("dependencies", {}).get("jquery") == "3.7.1", "npm_exact_lock_manifest")
    need(lock.get("packages", {}).get("", {}).get("dependencies", {}).get("jquery") == "3.7.1", "npm_lock_root")
    need(lock.get("packages", {}).get("node_modules/jquery", {}).get("integrity", "").startswith("sha512-"), "npm_integrity")
    need(library.get("productionPolicy") == "vendored-or-self-hosted-only", "no_runtime_third_party_cdns")
    need(library.get("chatWidgetExternalCdnAllowed") is False, "chat_widget_cdn_block")
    need(any(p.get("name") == "Vue 3" and p.get("load") == "not-bundled-by-default" for p in library.get("libraries", [])), "vue_not_yet_canonically_bundled")
    cdn = edge.get("cdn", {})
    need(cdn.get("immutablePublicHashedOnly") is True, "cdn_immutable_must_be_hashed")
    need(cdn.get("cacheRulesNotEffectiveOnDnsOnlyHosts") is True, "cdn_dns_only_not_proxy")
    need(all(path in cdn.get("bypassPaths", []) for path in ("/mcp","/api","/healthz")), "mcp_api_not_cache_bypassed")
    need(edge.get("lanes", {}).get("chatGptMcp", {}).get("plannedCloudflareProxy") is False, "cloudflare_mcp_proxy_unapproved")
    need(edge.get("changes", {}).get("mayMutateCloudflareZone") is False, "zone_mutation_without_proof")
    return failures

def main() -> None:
    read = lambda file: (ROOT / file).read_text(encoding="utf-8")
    data = (
        read("render.yaml"), read("publicationSite/pocketLab.html"),
        json.loads(read("host/harness/libraryPolicy.json")),
        json.loads(read("frontEnd/package.json")),
        json.loads(read("frontEnd/package-lock.json")),
        json.loads(read("doctrine/cloudflareEdgeHardeningV1.json")),
    )
    assert not verify(*data), "RED_RENDER_EDGE_STACK " + ",".join(verify(*data))
    blueprint, pocket, library, front, lock, edge = data
    cases = [
        ("missing_godot_url", (blueprint, pocket.replace(GODOT_URL, OLD_URL), library, front, lock, edge)),
        ("unlocked_jquery", (blueprint, pocket, library, front | {"dependencies": {"jquery": "^3.7.1"}}, lock, edge)),
        ("cdn_mcp_cache", (blueprint, pocket, library, front, lock, edge | {"cdn": edge["cdn"] | {"bypassPaths": []}})),
        ("cloudflare_bypass", (blueprint, pocket, library, front, lock, edge | {"changes": edge["changes"] | {"mayMutateCloudflareZone": True}})),
        ("godot_builder_missing", (blueprint.replace("tools/buildGodotWebHarness.sh", "missing-builder"), pocket, library, front, lock, edge)),
    ]
    for label, candidate in cases:
        assert verify(*candidate), "RED_NEGATIVE_CONTROL_" + label
    print("GREEN_RENDER_PYTHON_NPM_STATIC_CDN_GODOT_SOURCE")
    print("VUE3=LOCKED_OPT_IN_CANDIDATE_NOT_IN_PRODUCTION")
    print("CLOUDFLARE_LIVE_ZONE=UNVERIFIED_NO_MUTATION")
    print("RENDER_DASHBOARD_SETTINGS=VERIFY_SEPARATELY")
if __name__ == "__main__":
    main()
