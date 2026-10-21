#!/usr/bin/env python3
"""Fail-closed four lane external tester policy audit. No external action permitted."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/pluginBetaFourLaneV1.json"
INVITE = ROOT / "doctrine/pluginBetaInviteGateV1.json"
QUARANTINE = ROOT / "doctrine/companyWideOperationalQuarantineV1.json"
REPO_PLUGIN = ROOT / "plugins/luhm-os/plugin.json"

def read(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("contract must be object")
    return result

def validate(policy: dict, invite: dict, quarantine: dict, plugin: dict) -> list[str]:
    issues: list[str] = []
    def need(ok: bool, name: str) -> None:
        if not ok:
            issues.append(name)
    need(policy.get("schema") == "luhmOs.pluginBetaFourLane.v1", "schema")
    need(policy.get("status") == "SOURCE_POLICY_CANDIDATE_ONLY", "policy falsely promoted")
    need(policy.get("authority") == "Professor" and policy.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "authority")
    need(policy.get("relatedInviteGate") == "doctrine/pluginBetaInviteGateV1.json", "invite link")
    need(invite.get("status") == "CANDIDATE_SOURCE_ONLY_NOT_INVITE_READY", "invite status falsely upgraded")
    personal = policy.get("currentOwnerPlugin", {})
    invite_personal = invite.get("identity", {}).get("personalPlugin", {})
    need(personal.get("version") == invite_personal.get("version") == "1.0.8", "owner release drift")
    need(personal.get("scope") == "USER" and personal.get("discoverability") == "PRIVATE", "owner private boundary")
    need(personal.get("shareableExternally") is False and personal.get("appBindingPreserved") is True, "unsupported personal plugin distribution")
    need(plugin.get("version") == "0.5.2" and plugin.get("name") == "luhm-os", "repository package identity")
    in_chat = policy.get("inChatTarget", {})
    need(in_chat.get("primarySurface") == "CHATGPT_APP_IN_CONVERSATION", "website substituted for chat experience")
    need(in_chat.get("resourceUri") == "ui://luhm-os/cockpit-v2.html" and in_chat.get("tool") == "luhm_open_cockpit", "in-chat MCP identity drift")
    for key in ("outsideTesterNeedsChatGptPluginInstall", "openInAppMustStayInChat", "currentOwnerPrivatePluginNotShareableByLink", "workspacePluginSharingAndSiteViewerRightsBothRequiredWhenApplicable", "noWebPreviewSubstitution", "visualStatusOnlyNoAuthority"):
        need(in_chat.get(key) is True, "in-chat distribution guard disabled: "+key)
    for key in ("standaloneRenderAsTesterDelivery","inChatUiMountProvenForTester"):
        need(in_chat.get(key) is False, "external website or invented UI mount proof: "+key)
    need(in_chat.get("preferredDistribution") == "eligibleInvitedWorkspacePluginWithSiteViewerAccess", "invitation route unsupported")
    # Source gates prevent a policy green light when the actual MCP host UI is missing.
    widget = (ROOT / "host/harness/widget.html").read_text(encoding="utf-8")
    harness = (ROOT / "host/mcp/luhmHarness.py").read_text(encoding="utf-8")
    need('data-luhm-in-chat-beta' in widget and 'data-luhm-beta-lane="betaLts"' in widget, "in-chat four-lane UI absent")
    need('betaLanes": beta_lanes' in harness, "MCP tool response omits beta lane policy")
    need("setOpenInAppUrl" not in widget, "web harness selected as ChatGPT open-in-app")
    snapshots = policy.get("sourceSnapshots", {})
    sha = lambda v: isinstance(v, str) and re.fullmatch(r"[0-9a-f]{40}", v) is not None
    main = snapshots.get("cockpitLiveCommit")
    godot = snapshots.get("godotLiveCommit")
    need(sha(main) and sha(godot), "unverified rollback source format")
    need(snapshots.get("observedState") == "RENDER_LIVE_HISTORICAL_REVERIFY_BEFORE_ACTION" and snapshots.get("frozenCandidateOnly") is True, "receipt promoted without new check")
    lanes = policy.get("lanes", [])
    need(isinstance(lanes, list) and len(lanes) == 4, "not exactly four lanes")
    expected = [
        ("testing", "SOURCE_CI_CANDIDATE"),
        ("proposed", "PENDING_EXACT_PR_HEAD_REVIEW"),
        ("beta", "BLOCKED_EXTERNAL_ACCESS_UNVERIFIED"),
        ("betaLts", "FROZEN_CANDIDATE_UNPROMOTED")
    ]
    if isinstance(lanes, list) and len(lanes) == 4:
        for lane, (name, stage) in zip(lanes, expected):
            need(lane.get("id") == name and lane.get("stage") == stage, "lane ordering or stage: " + name)
            for field in ("externalAccess", "publicRelease", "autoPromote", "realUserData"):
                need(lane.get(field) is False, "forbidden "+field+" in "+name)
            need(lane.get("rollbackRequired") is True, "rollback missing in "+name)
            need(bool(lane.get("accept")) and bool(lane.get("entry")), "incomplete gate "+name)
        freeze = lanes[3].get("freeze", {})
        need(freeze.get("pinnedCockpitRollbackCommit") == main and freeze.get("pinnedGodotRollbackCommit") == godot, "lts rollback changed")
        need(freeze.get("publicVersionAssigned") is False and freeze.get("immutableReleaseArtifactObserved") is False and freeze.get("securityOnlyUntilApproval") is True, "lts promotion invented")
    gates = policy.get("gateStates", {})
    need(len(gates) == 8 and all(str(v).startswith("PENDING") for v in gates.values()), "unproven external evidence")
    dist = policy.get("distribution", {})
    for key in ("personalPrivateOwnerReleaseCannotBeAssumedShareable","publicRenderDemoLinkIsNotPrivatePluginAccess","workspaceAccessRequiresActualMembershipAndPublishingEligibility","publicDirectoryWouldNeedExternalReviewAndSeparateOwnerDecision","noAutomaticInvitation","noAutomaticPublication"):
        need(dist.get(key) is True, "unsafe distribution flag: "+key)
    security = policy.get("security", {})
    for key in ("readOnly","privateDriveAssetsExcluded","privateConversationDataExcluded","providerKeysExcluded","arbitraryWritesExcluded","anonymousTesterAccountDataExcluded","clearConsentRequired","collectMinimalFeedback","sensitiveFeedbackOnlyInPrivateChannel","quarantinedWorkersCannotBeActivated","androidInstallNotImplied"):
        need(security.get(key) is True, "security failed: "+key)
    release = policy.get("release", {})
    for key in ("betaInviteSent","githubInviteSent","publicDirectoryPublished","betaReleased","betaLtsPromoted"):
        need(release.get(key) is False, "release falsely declared: "+key)
    need(release.get("crownStatus") == "STOP", "Crown must remain STOP")
    need(quarantine.get("state") == "QUARANTINED" and quarantine.get("activeTaskWorkersAllowed") is False, "worker quarantine changed")
    target = str(policy.get("target", ""))
    need("@" not in target and "Alex" not in target, "tester contact leaked into public contract")
    return issues

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-beta-ready", action="store_true")
    args = parser.parse_args()
    problems = validate(read(POLICY), read(INVITE), read(QUARANTINE), read(REPO_PLUGIN))
    if problems:
        print(json.dumps({"fourLanePolicy":"RED","problems":problems},indent=2))
        return 1
    print(json.dumps({"fourLanePolicy":"GREEN_SOURCE_ONLY","testing":"CANDIDATE","proposed":"REVIEW","beta":"BLOCKED_EXTERNAL_PROOFS","betaLts":"FROZEN_CANDIDATE","invitation":"NOT_SENT","crown":"STOP"},indent=2))
    if args.require_beta_ready:
        print("BETA_READY_DENIED: source CI cannot attest real tester consent, permissions, host invocation or private access")
        return 3
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
