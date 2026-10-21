#!/usr/bin/env python3
"""Fail closed on plugin identity drift and unsupported public beta invitation claims."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/pluginBetaInviteGateV1.json"
MANIFEST = ROOT / "plugins/luhm-os/plugin.json"
MCP = ROOT / "plugins/luhm-os/mcp.json"
RECON = ROOT / "doctrine/hydraPublicBetaReconciliation20261021.json"
TRUTH = ROOT / "doctrine/currentSourceTruthV3.json"

def read(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"not a JSON object: {path}")
    return obj

def validate(contract: dict, manifest: dict, mcp: dict, reconciliation: dict, truth: dict) -> list[str]:
    issues: list[str] = []
    def require(condition: bool, label: str) -> None:
        if not condition:
            issues.append(label)
    require(contract.get("schema") == "luhmOs.pluginBetaInviteGate.v1", "contract schema drift")
    require(contract.get("authority") == "Professor", "owner authority missing")
    require(contract.get("status") == "CANDIDATE_SOURCE_ONLY_NOT_INVITE_READY", "unsupported beta-ready status")
    require(contract.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "source law drift")
    require(contract.get("baselineMain") == reconciliation.get("rollbackRef") or
            len(str(contract.get("baselineMain", ""))) == 40,
            "baseline commit malformed")
    identity = contract.get("identity", {})
    personal = identity.get("personalPlugin", {})
    bundled = identity.get("repoPlugin", {})
    historical_personal = reconciliation.get("chatGptPersonalPlugin", {})
    historical_repo = reconciliation.get("repositoryPlugin", {})
    require(personal.get("version") == historical_personal.get("versionObserved"), "personal version drift")
    require(personal.get("scope") == "USER" and personal.get("discoverability") == "PRIVATE", "personal scope drift")
    require(personal.get("sourceMapping") == "UNPROVEN", "unsourced personal-to-repo package mapping")
    require(personal.get("externalSharing") == "UNVERIFIED", "unsupported private plugin sharing")
    require(bundled.get("version") == historical_repo.get("versionObserved") == manifest.get("version"), "repo plugin version drift")
    require(personal.get("version") != bundled.get("version"), "distinct version identities collapsed")
    require(identity.get("crossVersionPromotionAllowed") is False, "cross-version automatic promotion")
    require(manifest.get("name") == "luhm-os", "repo plugin identity drift")
    interface = manifest.get("extensions", {}).get("com.openai", {}).get("interface", {})
    require(interface.get("capabilities") == ["Read"] == bundled.get("capabilities"), "public plugin permissions not read-only")
    actual_url = mcp.get("mcpServers", {}).get("luhm", {}).get("url")
    require(actual_url == bundled.get("endpoint") == historical_repo.get("endpointConfigured"), "MCP origin or endpoint mismatch")
    access = contract.get("access", {})
    github = access.get("github", {})
    chatgpt = access.get("chatgpt", {})
    require(github.get("repositoryVisibility") == "PUBLIC", "public GitHub access boundary lost")
    require(github.get("publicReadNeedsCollaboratorInvite") is False, "public GitHub viewing requires no invite")
    require(github.get("writeInvitationState") == "NOT_SENT", "GitHub invitation falsely declared")
    require(github.get("githubHandleVerified") is False, "GitHub handle verification falsely claimed")
    require(chatgpt.get("externalTesterAccess") == "NOT_GRANTED", "external plugin access falsely declared")
    require(chatgpt.get("directoryStatus") == "NOT_PUBLISHED", "directory publication falsely declared")
    require(chatgpt.get("distributionChannel") == "NOT_SELECTED", "external sharing route selected without review")
    require(access.get("testerEmailInPublicRepository") is False, "PII storage rule drift")
    require(access.get("inviteTarget") == "NAMED_TESTER_PRIVATE_CHAT_ONLY", "do not put tester contact in source")
    require(access.get("allowAutomaticInvites") is False and
            access.get("allowAutomaticPublication") is False and
            access.get("explicitOwnerApprovalForExternalAccess") is True, "unsupervised access control")
    security = contract.get("security", {})
    required = ["noPrivateMedia","noSecretsInPackage","noUserSpecificDataInAnonymousMcp",
                "noWriteTools","oauth21RequiredBeforePrivateUserData","rightsAndPrivacyReviewRequired",
                "receiptMustBindExactSource","hostToolInvocationCannotBeInferredFromCi",
                "deploymentMatchCannotBeInferredFromCi","denyClaimOfProductionGreenWithoutExternalProof"]
    for field in required:
        require(security.get(field) is True, f"security gate removed: {field}")
    experience = contract.get("intendedExperience", {})
    require(experience.get("currentHostTools") == ["luhmConnectionStatus","luhm_open_cockpit"], "host tool scope invented")
    require(experience.get("interactiveGuiOnTesterDevice") == "UNVERIFIED", "outside GUI proof invented")
    require(experience.get("inChatGodotInteractive") == "UNVERIFIED", "Godot in-chat gameplay overclaim")
    require(experience.get("independentWorkers") == "QUARANTINED", "agent quarantine release invented")
    gates = contract.get("gates", {})
    wanted = {"sourceCandidateChecks","personalToRepoReleaseMapping","currentLiveMcpCommit",
              "cleanExternalHostInstall","externalTesterToolInvocation","actualInteractiveGuiRender",
              "privacyTermsRightsReview","distributionAndAccessEligibility",
              "professorExactArtifactApproval"}
    require(set(gates) == wanted and all(str(v).startswith("PENDING") for v in gates.values()), "unproved beta gate asserted")
    release = contract.get("release", {})
    for key, expected in {
        "candidateBranchOnly":True,"repositoryMainMutation":False,
        "personalPluginMutation":False,"pluginInviteSent":False,
        "githubInviteSent":False,"publicBetaReleased":False,
        "directoryPublished":False,"promoted":False,"crownStatus":"STOP",
    }.items():
        require(release.get(key) == expected, f"release authority drift: {key}")
    require(truth.get("pluginLayer", {}).get("publicationAuthority") is False, "current source truth publication authority changed")
    require(truth.get("crownStatus") == "STOP", "global Crown unexpectedly promoted")
    return issues

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-beta-ready", action="store_true", help="Fail closed until external reviews are independently proven")
    args = parser.parse_args()
    problems = validate(read(CONTRACT), read(MANIFEST), read(MCP), read(RECON), read(TRUTH))
    if problems:
        print(json.dumps({"sourcePolicy":"RED", "betaRelease":"BLOCKED", "errors":problems}, indent=2))
        return 1
    print(json.dumps({"sourcePolicy":"GREEN_GUARD_ONLY","betaRelease":"BLOCKED_EXTERNAL_PROOFS",
                      "pluginInvite":"NOT_SENT","githubInvite":"NOT_SENT",
                      "hostProof":"THIS_AUDIT_IS_NOT_HOST_PROOF","crown":"STOP"}, indent=2))
    if args.require_beta_ready:
        print("BETA_READY_DENIED: source/CI can never self-prove external access, publication, or tester runtime")
        return 3
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
