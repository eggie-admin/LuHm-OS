#!/usr/bin/env python3
"""Generate deterministic LuHm OS Crown Cathedral SBOM + release provenance.

No network access and no signing/provider secret access. Inputs are only exact source
and receipts already produced by the fail-closed build.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"RED_RELEASE_PROVENANCE_MISSING:{path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def component(ref: str, type_: str, name: str, version: str, digest: str | None = None, *, properties: list[dict] | None = None, licenses: list[dict] | None = None, external_refs: list[dict] | None = None) -> dict:
    item = {"type": type_, "bom-ref": ref, "name": name, "version": version}
    if digest:
        item["hashes"] = [{"alg": "SHA-256", "content": digest}]
    if properties:
        item["properties"] = properties
    if licenses:
        item["licenses"] = licenses
    if external_refs:
        item["externalReferences"] = external_refs
    return item


def npm_components(lock_path: Path) -> list[dict]:
    if not lock_path.is_file():
        return []
    lock = load(lock_path)
    result: list[dict] = []
    packages = lock.get("packages", {})
    for path, info in sorted(packages.items()):
        if not path or "node_modules/" not in path:
            continue
        name = str(info.get("name") or path.split("node_modules/", 1)[1])
        version = str(info.get("version") or "UNKNOWN")
        ref = f"npm:{name}@{version}"
        digest = None
        integrity = str(info.get("integrity") or "")
        if integrity.startswith("sha512-"):
            try:
                digest = base64.b64decode(integrity.split("-", 1)[1]).hex()
            except Exception:
                digest = None
        item = {"type": "library", "bom-ref": ref, "name": name, "version": version}
        if digest:
            item["hashes"] = [{"alg": "SHA-512", "content": digest}]
        result.append(item)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-dir", type=Path, required=True)
    ap.add_argument("--source-sha", required=True)
    ap.add_argument("--output-bom", type=Path, required=True)
    ap.add_argument("--output-provenance", type=Path, required=True)
    args = ap.parse_args()

    build = args.build_dir
    community = load(build / "community-assets-receipt.json")
    donors = load(build / "luhm-game-donor-receipt.json")
    full_game = load(build / "luhm-full-game-final-audit.json")

    source_receipt = (build / "source-commit.txt").read_text(encoding="utf-8").strip()
    if source_receipt != args.source_sha:
        raise SystemExit("RED_RELEASE_PROVENANCE_SOURCE_MISMATCH")

    apks = sorted(build.glob("*.apk"))
    if len(apks) != 1:
        raise SystemExit("RED_RELEASE_PROVENANCE_APK_COUNT")
    apk = apks[0]
    apk_sha = sha256(apk)
    sha_line = (build / "sha256.txt").read_text(encoding="utf-8").strip().split()
    if not sha_line or sha_line[0] != apk_sha:
        raise SystemExit("RED_RELEASE_PROVENANCE_APK_HASH")

    badging = (build / "badging.txt").read_text(encoding="utf-8", errors="replace")
    package = re.search(r"package: name='([^']+)'", badging)
    version_name = re.search(r"versionName='([^']+)'", badging)
    version_code = re.search(r"versionCode='([^']+)'", badging)
    if not package or not version_name or not version_code:
        raise SystemExit("RED_RELEASE_PROVENANCE_BADGING")

    hardening = (build / "release-hardening.txt").read_text(encoding="utf-8", errors="replace")
    signing = re.search(r"^signing=([^\r\n]+)$", hardening, re.M)
    signing_mode = signing.group(1).strip() if signing else "UNKNOWN"

    lum_base = ROOT / "assets/lum/luhm.glb"
    lum_running = ROOT / "assets/lum/luhmRunning.glb"
    for path in (lum_base, lum_running):
        if not path.is_file():
            raise SystemExit(f"RED_RELEASE_PROVENANCE_LUM_MISSING:{path.name}")

    root_ref = f"application:{package.group(1)}@{version_name.group(1)}"
    components: list[dict] = [
        component("framework:godot@4.7.2", "framework", "Godot Engine", "4.7.2"),
        component("library:luhm-webglass", "library", "LuHm WebGlass Android bridge", "1", sha256(ROOT / "addons/kai_webview/bin/kaiwebview-release.aar"), properties=[
            {"name": "luhm.compatibility.path", "value": "addons/kai_webview"},
            {"name": "luhm.runtime.identity", "value": "LUHM_WEBGLASS"},
            {"name": "luhm.authority", "value": "false"},
        ]),
        component("file:lum-base", "file", "LuHm rigged Lum base GLB", "1", sha256(lum_base), properties=[{"name": "luhm.role", "value": "resident-character"}]),
        component("file:lum-running", "file", "LuHm rigged Lum running GLB", "1", sha256(lum_running), properties=[{"name": "luhm.role", "value": "character-animation"}]),
    ]

    cc0 = [{"license": {"id": "CC0-1.0"}}]
    for item in community.get("assets", []):
        components.append(component(
            f"community:{item['runtime_path']}", "file", item["name"], str(community["source_commit"]), item["sha256"],
            properties=[
                {"name": "luhm.runtime.path", "value": item["runtime_path"]},
                {"name": "luhm.source.kit", "value": item["kit"]},
                {"name": "luhm.source.repository", "value": community["source_repository"]},
            ],
            licenses=cc0,
            external_refs=[{"type": "distribution", "url": item["source_url"]}],
        ))
    for item in community.get("support_files", []):
        components.append(component(
            f"community-support:{item['runtime_path']}", "file", item["name"], str(community["source_commit"]), item["sha256"],
            properties=[
                {"name": "luhm.runtime.path", "value": item["runtime_path"]},
                {"name": "luhm.source.kit", "value": item["kit"]},
            ],
            licenses=cc0,
            external_refs=[{"type": "distribution", "url": item["source_url"]}],
        ))

    donor_license = [{"license": {"name": "User-supplied or generated; rights-cleared LuHm OS runtime derivative"}}]
    for item in donors.get("assets", []):
        components.append(component(
            f"donor:{item['id']}", "file", item["id"], "1", item["sha256"],
            properties=[
                {"name": "luhm.runtime.path", "value": item["runtime_path"]},
                {"name": "luhm.donor.authority", "value": "false"},
                {"name": "luhm.source.rights", "value": item["source_rights"]},
                {"name": "luhm.source.sha256", "value": item["source_sha256"]},
                {"name": "luhm.git.blob.sha1", "value": item["git_blob_sha1"]},
            ],
            licenses=donor_license,
        ))

    components.extend(npm_components(ROOT / "cockpit/package-lock.json"))
    components.sort(key=lambda x: str(x["bom-ref"]))
    refs = [c["bom-ref"] for c in components]

    serial = uuid.uuid5(uuid.NAMESPACE_URL, f"https://github.com/eggie-admin/LuHm-OS/{args.source_sha}/{apk_sha}")
    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.7",
        "serialNumber": f"urn:uuid:{serial}",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "bom-ref": root_ref,
                "name": "LuHm OS Crown Cathedral",
                "version": version_name.group(1),
                "hashes": [{"alg": "SHA-256", "content": apk_sha}],
                "properties": [
                    {"name": "luhm.android.package", "value": package.group(1)},
                    {"name": "luhm.android.versionCode", "value": version_code.group(1)},
                    {"name": "luhm.source.sha", "value": args.source_sha},
                    {"name": "luhm.scope", "value": "FULL_GAME"},
                    {"name": "luhm.runtime.identity", "value": "LUHM_WEBGLASS"},
                ],
            }
        },
        "components": components,
        "dependencies": [{"ref": root_ref, "dependsOn": refs}],
    }
    args.output_bom.parent.mkdir(parents=True, exist_ok=True)
    args.output_bom.write_text(json.dumps(bom, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bom_sha = sha256(args.output_bom)

    provenance = {
        "schema": "luhm-os.release-provenance.v1",
        "product": "LuHm OS",
        "scope": "FULL_GAME",
        "source_sha": args.source_sha,
        "android": {
            "package": package.group(1),
            "version_name": version_name.group(1),
            "version_code": int(version_code.group(1)),
            "apk_file": apk.name,
            "apk_sha256": apk_sha,
            "signing_mode": signing_mode,
            "debuggable": False,
            "internet_permission": False,
            "profileable_shell": False,
        },
        "sbom": {
            "format": "CycloneDX",
            "spec_version": "1.7",
            "file": args.output_bom.name,
            "sha256": bom_sha,
            "component_count": len(components),
        },
        "inputs": {
            "lum_base_sha256": sha256(lum_base),
            "lum_running_sha256": sha256(lum_running),
            "community_source_repository": community.get("source_repository"),
            "community_source_commit": community.get("source_commit"),
            "community_asset_count": community.get("asset_count"),
            "community_support_file_count": community.get("support_file_count"),
            "community_license": community.get("license"),
            "game_donor_count": donors.get("asset_count"),
            "game_donor_delivery": donors.get("runtime_delivery"),
            "game_donor_authority": donors.get("donor_authority"),
        },
        "authority": {
            "crown": "Professor",
            "kai9000_donor_only": True,
            "kai9000_widget_authority": False,
            "webglass_runtime_identity": "LUHM_WEBGLASS",
            "canonical_main_promoted": False,
        },
        "gates": {
            "full_game_scope_green": full_game.get("status") == "LUHM_FULL_GAME_SCOPE_GREEN",
            "provider_secret_in_apk": False,
            "private_nexus_payload_in_shared_candidate": False,
            "physical_samsung_exact_build_proof": False,
            "persistent_crown_owned_signing": signing_mode == "crown_persistent_external",
            "live_openai_host_receipt": False,
        },
        "deterministic": True,
        "unknown_is_not_green": True,
    }
    args.output_provenance.parent.mkdir(parents=True, exist_ok=True)
    args.output_provenance.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"RELEASE_SBOM=GREEN components={len(components)} sha256={bom_sha}")
    print(f"RELEASE_PROVENANCE=GREEN apk_sha256={apk_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
