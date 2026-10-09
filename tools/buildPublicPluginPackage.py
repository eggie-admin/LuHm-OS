#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "luhm-os"
MEMBERS = [
    "plugin.json",
    "mcp.json",
    "skills/luhm-agent-workflow/SKILL.md",
    "assets/logo.svg",
]
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
MCP_URL = "https://luhm-os-harness-green.onrender.com/mcp"

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_documents(plugin: dict, mcp: dict, review_tests: dict) -> list[str]:
    errors = []
    if plugin.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        errors.append("plugin manifest schema reference is invalid")
    if (
        plugin.get("name") != "luhm-os"
        or not isinstance(plugin.get("version"), str)
        or not plugin.get("version")
    ):
        errors.append("plugin manifest identity or version is invalid")
    extensions = plugin.get("extensions")
    openai = extensions.get("com.openai") if isinstance(extensions, dict) else None
    openai = openai if isinstance(openai, dict) else {}
    interface = openai.get("interface")
    interface = interface if isinstance(interface, dict) else {}
    if interface.get("capabilities") != ["Read"]:
        errors.append("plugin manifest must remain read-only")
    for field in ("displayName", "shortDescription", "longDescription", "developerName"):
        if not isinstance(interface.get(field), str) or not interface[field]:
            errors.append(f"plugin interface is missing {field}")
    for field in ("logo", "composerIcon"):
        asset_path = interface.get(field)
        if (
            not isinstance(asset_path, str)
            or not asset_path.startswith("./")
            or ".." in pathlib.PurePosixPath(asset_path[2:]).parts
            or asset_path[2:] not in MEMBERS
        ):
            errors.append(f"plugin interface has an invalid {field} asset path")

    if mcp.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        errors.append("MCP manifest schema reference is invalid")
    servers = mcp.get("mcpServers")
    if not isinstance(servers, dict) or set(servers) != {"luhm"}:
        errors.append("MCP manifest must declare only the luhm server")
    else:
        server = servers["luhm"]
        if not isinstance(server, dict) or server.get("type") != "streamable-http" or server.get("url") != MCP_URL:
            errors.append("MCP server must use the canonical HTTPS endpoint and transport")

    for polarity, expected_count in (("positive", 5), ("negative", 3)):
        cases = review_tests.get(polarity)
        if not isinstance(cases, list) or len(cases) != expected_count:
            errors.append(f"review tests require exactly {expected_count} {polarity} cases")
        elif any(
            not isinstance(case, dict) or not case.get("prompt") or not case.get("expected")
            for case in cases
        ):
            errors.append(f"{polarity} review cases require prompt and expected behavior")
    return errors


def load_package_inputs() -> tuple[dict, dict, dict, dict]:
    try:
        plugin = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
        mcp = json.loads((PLUGIN / "mcp.json").read_text(encoding="utf-8"))
        review_tests = json.loads((PLUGIN / "review-tests.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"PACKAGE_INPUT_INVALID {error}") from error
    if not all(isinstance(value, dict) for value in (plugin, mcp, review_tests)):
        raise SystemExit("PACKAGE_INPUT_INVALID manifests and review tests must be JSON objects")
    errors = validate_documents(plugin, mcp, review_tests)
    if errors:
        raise SystemExit("PACKAGE_INPUT_INVALID " + "; ".join(errors))
    for member in MEMBERS:
        path = PLUGIN / member
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(PLUGIN.resolve()):
            raise SystemExit(f"missing package member: {member}")
    for field in ("logo", "composerIcon"):
        asset = PLUGIN / plugin["extensions"]["com.openai"]["interface"][field][2:]
        if not asset.is_file() or asset.stat().st_size == 0:
            raise SystemExit(f"missing plugin asset: {field}")
    return plugin, mcp, review_tests, {
        "portableManifestContract": "PASS",
        "portableMcpContract": "PASS",
        "httpsMcp": "PASS",
        "reviewCases": "5_positive_3_negative",
        "assetPaths": "PASS",
    }


def build_package(source_ref: str, out_dir: pathlib.Path, actual_source_ref: str) -> pathlib.Path:
    if len(source_ref) != 40 or any(c not in "0123456789abcdef" for c in source_ref):
        raise SystemExit("source-ref must be a lowercase 40-character git SHA")
    if actual_source_ref != source_ref:
        raise SystemExit(f"SOURCE_DRIFT expected={source_ref} actual={actual_source_ref}")

    manifest, _, _, package_checks = load_package_inputs()
    version = manifest["version"]
    short = source_ref[:8]
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = out_dir / f"LuHm-OS-plugin-{version}-{short}.zip"

    with zipfile.ZipFile(artifact, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for member in sorted(MEMBERS):
            data = (PLUGIN / member).read_bytes()
            info = zipfile.ZipInfo(member, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, data)

    receipt = {
        "schema": "luhmOs.publicPluginPackageBuildReceipt.v1",
        "status": "BUILT_CANDIDATE",
        "sourceRef": source_ref,
        "buildScope": "publicPluginPackage",
        "artifact": {
            "filename": artifact.name,
            "sha256": sha256(artifact),
            "bytes": artifact.stat().st_size,
        },
        "members": sorted(MEMBERS),
        "packageChecks": package_checks,
        "publicationAuthority": False,
        "releaseAuthority": False,
        "crownAuthority": False,
    }
    receipt_path = out_dir / "publicPluginPackageBuildReceipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("PUBLIC_PLUGIN_PACKAGE=BUILT")
    print(f"sourceRef={source_ref}")
    print(f"artifact={artifact}")
    print(f"sha256={receipt['artifact']['sha256']}")
    print("publicationAuthority=false")
    return artifact


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source-ref", required=True)
    p.add_argument("--out-dir", required=True)
    args = p.parse_args()

    actual = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    build_package(args.source_ref, pathlib.Path(args.out_dir), actual)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
