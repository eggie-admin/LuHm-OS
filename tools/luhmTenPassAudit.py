#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."
CANONICAL_MAIN = "506e486cb142f6c81f7df71d007fdf05e47e82ed"
GAME_BRANCH = "candidate/crown-cathedral-audit-hardening-20260927"
AGENT_BRANCH = "feature/oni-pet-activity-dock-v2-20260927"
LAST_GAME_CI_GREEN = "52cdb6e948be91dd0939264cdd09ff8284292d85"
REMOTE_MCP = "https://mcp.eggiebagelface.art/mcp"
ROLES = {"Lum", "Kiri", "Tetsu", "Kaji", "Momo", "Shiori", "DrNao", "Kugi", "Fumi", "Sumi", "Koe", "Yume"}


def load(path: str) -> dict:
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f"RED_TEN_PASS_MISSING:{path}")
    value = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"RED_TEN_PASS_NOT_OBJECT:{path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"RED_TEN_PASS:{message}")


def pass_record(number: int, lane: str, status: str, evidence: list[str], blockers: list[str] | None = None) -> dict:
    return {
        "pass": number,
        "lane": lane,
        "status": status,
        "evidence": evidence,
        "blockers": blockers or [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-sha", default="UNKNOWN")
    parser.add_argument("--output", type=Path, default=Path("build/ten-pass/luhm-ten-pass-audit.json"))
    args = parser.parse_args()

    root = load("doctrine/SOURCE_OF_TRUTH.json")
    game = load("doctrine/luhmFullGameSourceTruth-20260927.json")
    release = load("doctrine/RELEASE_BOUNDARY.json")
    control = load("doctrine/ONI_MESH_CONTROL_PLANE_V2.json")
    deploy = load("doctrine/openAiLumOniDeployment-20260927.json")
    plugin = load("plugins/luhm-os/plugin.json")
    plugin_mcp = load("plugins/luhm-os/mcp.json")
    plugin_mcp_local = load("plugins/luhm-os/mcp.local.json")
    device = load("doctrine/deviceProof-52cdb6e-20260927.json")

    passes: list[dict] = []

    # 1. Authority and source identity.
    require(root.get("product") == "LuHm OS" and root.get("scope") == "FULL_GAME", "root product/scope drift")
    require(root.get("authority") == "Professor" and root.get("source_law") == LAW, "root authority/source-law drift")
    require(root.get("canonicalMain", {}).get("sha") == CANONICAL_MAIN, "canonical main drift")
    require(root.get("canonicalMain", {}).get("promoted") is False, "unproven main promotion")
    passes.append(pass_record(1, "Authority / source identity", "GREEN_STATIC", [
        "canonical main pinned",
        "Professor remains final authority",
        "promotion=false",
        "source law exact",
    ]))

    # 2. Doctrine convergence and lane separation.
    require(root.get("currentFullGameCandidate", {}).get("branch") == GAME_BRANCH, "game candidate branch drift")
    require(root.get("agentWorkflowCandidate", {}).get("branch") == AGENT_BRANCH, "agent candidate branch drift")
    require(root.get("historicalSealsOverrideCurrentFullGame") is False, "historical seal override enabled")
    require(game.get("historical_seals_override_current_full_game") is False, "full-game historical override enabled")
    require(release.get("source_law") == LAW and deploy.get("source_law") == LAW, "subsystem source-law drift")
    passes.append(pass_record(2, "Doctrine convergence", "GREEN_STATIC", [
        "full-game and agent lanes are distinct",
        "historical seals do not override current truth",
        "shared source law converged",
    ]))

    # 3. Exact build/CI evidence lineage.
    candidate = root.get("currentFullGameCandidate", {})
    require(candidate.get("latestExactCiGreenHead") == LAST_GAME_CI_GREEN, "latest exact CI-green game head drift")
    latest_ci = candidate.get("latestExactCiProof", {})
    require(len(latest_ci) >= 7 and all(isinstance(v, int) and v > 0 for v in latest_ci.values()), "latest exact CI proof incomplete")
    require(device.get("candidateHead") == LAST_GAME_CI_GREEN and device.get("ciState") == "EXACT_HEAD_GREEN", "device receipt/CI identity drift")
    passes.append(pass_record(3, "Build determinism / exact CI", "GREEN_EVIDENCE", [
        f"full-game exact CI green head {LAST_GAME_CI_GREEN}",
        "Samsung candidate, full-game, community, Oni dual-build, WebGlass, Lum rig and source-truth runs recorded",
    ]))

    # 4. Android security/release boundary.
    android = root.get("android", {})
    require(android.get("targetSdk") == 36, "target SDK drift")
    require(android.get("internetPermission") is False, "Android INTERNET permission doctrine drift")
    require(android.get("production_signer") is False, "unproven production signer")
    deny = set(release.get("deny", []))
    for item in ("production signing", "publishing", "remote shell execution", "embedded provider secrets"):
        require(item in deny, f"release deny-list missing: {item}")
    passes.append(pass_record(4, "Android / application security", "GREEN_STATIC", [
        "targetSdk 36",
        "INTERNET permission false",
        "provider secrets excluded from APK",
        "remote shell denied",
    ], ["persistent Crown-owned signing still pending"]))

    # 5. Game assets and rights boundary.
    require("77 Kenney CC0" in root.get("gameContract", {}).get("communityAssets", ""), "77-asset game contract drift")
    donor = root.get("donorPolicy", {})
    require(donor.get("unknownRights") == "FAIL_CLOSED", "unknown-rights policy drift")
    require(donor.get("privateLegacyRelicPayloads") is False, "private legacy relic payload enabled")
    require(donor.get("ciDriveFetch") is False, "private donor vault exposed to CI")
    require(game.get("donor_boundary", {}).get("runtime_network") is False, "game donor runtime network drift")
    passes.append(pass_record(5, "Godot game assets / provenance", "GREEN_STATIC", [
        "77 CC0 runtime asset contract",
        "unknown rights fail closed",
        "private donor vault excluded from CI",
        "runtime network disabled for donor delivery",
    ]))

    # 6. WebGlass/chat/proof system.
    for path in (
        "cockpit/jquery/luhm.deck.js",
        "cockpit/jquery/luhm.proof.viewer.js",
        "cockpit/app.js",
        "native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/ProofVault.kt",
    ):
        require((ROOT / path).is_file(), f"missing proof/chat surface: {path}")
    proof_vault = root.get("agentWorkflowCandidate", {}).get("androidProofVault")
    require(proof_vault and (ROOT / proof_vault).is_file(), "proof vault source truth pointer invalid")
    passes.append(pass_record(6, "WebGlass / chat / embedded proof", "GREEN_STATIC", [
        "chat workbench present",
        "embedded proof viewer present",
        "Android app-private proof vault present",
        "proof import has no GREEN authority",
    ]))

    # 7. Lum/Oni agent mesh.
    topology = control.get("topology", {})
    require(control.get("boss") == "Lum" and control.get("humanAuthority") == "Professor", "agent authority drift")
    require(set(control.get("roles", {})) == ROLES, "Oni role roster drift")
    require(topology.get("helperRecruitment") is False, "recursive helper recruitment enabled")
    require(topology.get("maxParallelSupportWorkers") == 3, "support parallelism drift")
    require(topology.get("maxMutableSourceLanesPerCandidate") == 1, "mutable source lane drift")
    passes.append(pass_record(7, "Lum boss / Oni mesh / skills", "GREEN_STATIC", [
        "Lum sole boss",
        "12 canonical roles",
        "max 3 support workers",
        "single mutable source lane",
        "recursive recruitment disabled",
    ]))

    # 8. ChatGPT plugin and MCP enterprise edge.
    capabilities = plugin.get("extensions", {}).get("com.openai", {}).get("interface", {}).get("capabilities", [])
    require(capabilities == ["Read"], "plugin capability drift")
    prod = plugin_mcp.get("mcpServers", {}).get("luhm", {})
    local = plugin_mcp_local.get("mcpServers", {}).get("luhm_local", {})
    require(prod.get("url") == REMOTE_MCP and prod.get("type") == "streamable-http", "production MCP manifest drift")
    require(local.get("url") == "http://127.0.0.1:8788/mcp", "local MCP manifest drift")
    remote = deploy.get("remoteMcp", {})
    require(remote.get("provider") == "Render" and remote.get("dnsRebindingProtection") is True, "remote MCP hardening drift")
    require(remote.get("mutationAuthority") is False and remote.get("releaseAuthority") is False, "remote MCP authority drift")
    passes.append(pass_record(8, "ChatGPT plugin / MCP / Render", "AMBER_EXTERNAL", [
        "portable plugin is read-only",
        "local and production MCP profiles separated",
        "Render HTTPS service staged",
        "DNS rebinding protection and request size ceiling declared",
    ], [
        "custom mcp.eggiebagelface.art DNS/TLS verification pending",
        "ChatGPT/OpenAI remote connection proof pending",
        "Render free tier is staging-only",
    ]))

    # 9. Enterprise/release controls.
    gates = root.get("remainingExternalGates", {})
    require(root.get("enterpriseReady") is False, "unproven enterprise-ready claim")
    require(root.get("publication_authority") is False and root.get("promotion") is False, "release authority drift")
    require(gates.get("persistentCrownOwnedSigning") == "PENDING", "signing gate drift")
    require(str(gates.get("branchControls", "")).startswith("RED_MAIN_UNPROTECTED"), "branch-control observation drift")
    passes.append(pass_record(9, "Enterprise release / signing / branch controls", "RED_EXTERNAL", [
        "publication and promotion remain false",
        "main observed unprotected",
        "persistent signing explicitly absent",
    ], [
        "protect main / enforce required checks",
        "establish persistent Crown-owned Android signing lineage",
        "move Render off staging/free behavior before enterprise production",
    ]))

    # 10. Physical device and Crown gate.
    require(device.get("deviceEvidence", {}).get("result") == "RED_PRESENTATION", "device result no longer matches source truth")
    require(device.get("promotionBlocked") is True, "device RED failed to block promotion")
    require(root.get("status") == "RED_DEVICE_PRESENTATION_BLOCKS_CROWN", "root status does not reflect device RED")
    passes.append(pass_record(10, "Physical Samsung / Crown", "RED_DEVICE", [
        "52cdb6e exact-head CI is green",
        "physical Samsung world and WebGlass rendered",
        "Lum was not visibly rendered in the recorded device proof",
        "Crown promotion blocked",
    ], ["new exact-build Samsung proof required after presentation/runtime correction"]))

    overall = "RED_BLOCKED"
    result = {
        "schema": "luhm-os.ten-pass-audit.v1",
        "sourceSha": args.source_sha,
        "auditExecution": "10_OF_10_PASSES_EVALUATED",
        "overallSystemStatus": overall,
        "statePrecedence": ["ERROR", "RED", "UNKNOWN", "AMBER", "GREEN"],
        "passes": passes,
        "crownAuthorized": False,
        "canonicalMainMutationAuthorized": False,
        "unknownIsNotGreen": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("LUHM_TEN_PASS_AUDIT_COMPLETE", json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
