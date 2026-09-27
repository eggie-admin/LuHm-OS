#!/usr/bin/env python3
"""Fail-closed audit for LuHm OS CycloneDX SBOM and release provenance."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SPEC = "1.7"
EXPECTED_COMMUNITY = 77
EXPECTED_SUPPORT = 2
EXPECTED_DONORS = 2
EXPECTED_WEBGLASS = "LUHM_WEBGLASS"


def fail(msg: str) -> None:
    raise SystemExit("RED_RELEASE_PROVENANCE_AUDIT:" + msg)


def load(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing:{path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-dir", type=Path, required=True)
    ap.add_argument("--source-sha", required=True)
    ap.add_argument("--bom", type=Path, required=True)
    ap.add_argument("--provenance", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    doctrine = load(ROOT / "doctrine/releaseSupplyChain-20260927.json")
    if doctrine.get("product") != "LuHm OS" or doctrine.get("scope") != "FULL_GAME":
        fail("doctrine_scope")
    if doctrine.get("sbom", {}).get("format") != "CycloneDX" or doctrine.get("sbom", {}).get("spec_version") != EXPECTED_SPEC:
        fail("doctrine_sbom_version")
    if doctrine.get("security", {}).get("provider_secret_required") is not False:
        fail("provider_secret_boundary")
    if doctrine.get("security", {}).get("signing_secret_recorded") is not False:
        fail("signing_secret_boundary")

    b = args.build_dir
    apk_sha_line = (b / "sha256.txt").read_text(encoding="utf-8").strip().split()
    if not apk_sha_line:
        fail("apk_sha_receipt")
    expected_apk_sha = apk_sha_line[0]
    expected_source = (b / "source-commit.txt").read_text(encoding="utf-8").strip()
    if expected_source != args.source_sha:
        fail("source_receipt")

    bom = load(args.bom)
    provenance = load(args.provenance)
    if bom.get("bomFormat") != "CycloneDX" or bom.get("specVersion") != EXPECTED_SPEC:
        fail("bom_identity")
    if not str(bom.get("serialNumber", "")).startswith("urn:uuid:"):
        fail("bom_serial")
    root = bom.get("metadata", {}).get("component", {})
    if root.get("name") != "LuHm OS Crown Cathedral":
        fail("root_component")
    root_hashes = {x.get("alg"): x.get("content") for x in root.get("hashes", [])}
    if root_hashes.get("SHA-256") != expected_apk_sha:
        fail("bom_apk_hash")
    root_props = {x.get("name"): x.get("value") for x in root.get("properties", [])}
    if root_props.get("luhm.source.sha") != args.source_sha:
        fail("bom_source_sha")
    if root_props.get("luhm.runtime.identity") != EXPECTED_WEBGLASS:
        fail("bom_webglass_identity")
    if root_props.get("luhm.scope") != "FULL_GAME":
        fail("bom_scope")

    components = bom.get("components", [])
    refs = {str(x.get("bom-ref")): x for x in components}
    community_refs = [r for r in refs if r.startswith("community:res://")]
    support_refs = [r for r in refs if r.startswith("community-support:res://")]
    donor_refs = [r for r in refs if r.startswith("donor:")]
    if len(community_refs) != EXPECTED_COMMUNITY:
        fail(f"community_count:{len(community_refs)}")
    if len(support_refs) != EXPECTED_SUPPORT:
        fail(f"support_count:{len(support_refs)}")
    if len(donor_refs) != EXPECTED_DONORS:
        fail(f"donor_count:{len(donor_refs)}")
    if "framework:godot@4.7.2" not in refs:
        fail("godot_component")
    if "library:luhm-webglass" not in refs:
        fail("webglass_component")
    if "file:lum-base" not in refs or "file:lum-running" not in refs:
        fail("lum_components")
    webglass_props = {x.get("name"): x.get("value") for x in refs["library:luhm-webglass"].get("properties", [])}
    if webglass_props.get("luhm.runtime.identity") != EXPECTED_WEBGLASS:
        fail("webglass_component_identity")
    if webglass_props.get("luhm.authority") != "false":
        fail("compatibility_authority")
    for r in donor_refs:
        props = {x.get("name"): x.get("value") for x in refs[r].get("properties", [])}
        if props.get("luhm.donor.authority") != "false":
            fail("donor_authority")

    dependencies = bom.get("dependencies", [])
    root_ref = root.get("bom-ref")
    root_dep = next((x for x in dependencies if x.get("ref") == root_ref), None)
    if root_dep is None:
        fail("dependency_root")
    depends_on = set(root_dep.get("dependsOn", []))
    if not set(refs).issubset(depends_on):
        fail("dependency_incomplete")

    if provenance.get("schema") != "luhm-os.release-provenance.v1":
        fail("provenance_schema")
    if provenance.get("product") != "LuHm OS" or provenance.get("scope") != "FULL_GAME":
        fail("provenance_scope")
    if provenance.get("source_sha") != args.source_sha:
        fail("provenance_source")
    android = provenance.get("android", {})
    if android.get("apk_sha256") != expected_apk_sha:
        fail("provenance_apk_hash")
    if android.get("debuggable") is not False or android.get("internet_permission") is not False or android.get("profileable_shell") is not False:
        fail("provenance_android_hardening")
    sbom = provenance.get("sbom", {})
    if sbom.get("format") != "CycloneDX" or sbom.get("spec_version") != EXPECTED_SPEC:
        fail("provenance_sbom_identity")
    if sbom.get("sha256") != sha256(args.bom):
        fail("provenance_sbom_hash")
    if int(sbom.get("component_count", -1)) != len(components):
        fail("provenance_component_count")
    inputs = provenance.get("inputs", {})
    if inputs.get("community_asset_count") != EXPECTED_COMMUNITY or inputs.get("community_support_file_count") != EXPECTED_SUPPORT:
        fail("provenance_community_counts")
    if inputs.get("game_donor_count") != EXPECTED_DONORS or inputs.get("game_donor_authority") is not False:
        fail("provenance_donor_boundary")
    authority = provenance.get("authority", {})
    if authority.get("crown") != "Professor":
        fail("provenance_crown")
    if authority.get("kai9000_donor_only") is not True or authority.get("kai9000_widget_authority") is not False:
        fail("provenance_kai_boundary")
    if authority.get("webglass_runtime_identity") != EXPECTED_WEBGLASS:
        fail("provenance_webglass_identity")
    if authority.get("canonical_main_promoted") is not False:
        fail("provenance_canonical_promotion")
    gates = provenance.get("gates", {})
    if gates.get("full_game_scope_green") is not True:
        fail("full_game_gate")
    if gates.get("provider_secret_in_apk") is not False:
        fail("provider_secret_gate")
    if gates.get("private_nexus_payload_in_shared_candidate") is not False:
        fail("nexus_gate")
    if provenance.get("deterministic") is not True or provenance.get("unknown_is_not_green") is not True:
        fail("provenance_truth_law")

    out = {
        "schema": "luhm-os.release-provenance-audit.v1",
        "status": "GREEN",
        "source_sha": args.source_sha,
        "apk_sha256": expected_apk_sha,
        "sbom_format": "CycloneDX",
        "sbom_spec_version": EXPECTED_SPEC,
        "sbom_sha256": sha256(args.bom),
        "component_count": len(components),
        "community_assets": len(community_refs),
        "community_support_files": len(support_refs),
        "game_donors": len(donor_refs),
        "lum_components": 2,
        "webglass_runtime_identity": EXPECTED_WEBGLASS,
        "kai9000_donor_only": True,
        "kai9000_widget_authority": False,
        "provider_secret_in_apk": False,
        "private_nexus_payload_in_shared_candidate": False,
        "canonical_main_promoted": False,
        "unknown_is_not_green": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"RELEASE_PROVENANCE_AUDIT=PASS components={len(components)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
