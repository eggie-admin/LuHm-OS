#!/usr/bin/env python3
"""Read-only consistency gate for the proposed vidIQ/OpenAI long-form Canon bridge.

Runs on source files only. Never connects vidIQ, activates an agent, posts to
YouTube, changes privileges, or promotes a candidate.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys


def load(root: Path, rel: str) -> dict:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def validate(bridge: dict, campaign: dict, brands: dict, quarantine: dict, lanes: dict) -> list[str]:
    errors: list[str] = []

    def need(condition: bool, label: str) -> None:
        if not condition:
            errors.append(label)

    identity = bridge.get("identities", {})
    yt = identity.get("youtube", {})
    route = bridge.get("route", {})
    gates = bridge.get("hardGates", {})
    approval = bridge.get("approval", {})
    evidence = bridge.get("observedSessionEvidence", {})
    need(bridge.get("schema") == "luhmOs.vidIqOpenAiCanonBridge.v1", "schema")
    need(bridge.get("status") == "PROPOSED_SOURCE_ONLY", "candidateOnly")
    need(bridge.get("scopeId") == "youtubeLongFormReadOnlyAndDrafts", "scope")
    need(bridge.get("authority") == "Professor", "authority")
    need(identity.get("product") == "LuHm-OS", "product")
    need(identity.get("project") == "Project Premonition", "project")
    need(identity.get("projectLegacyAlias") == "Project Hydra", "legacy")
    need(identity.get("publisher") == "Eggie Bagelface", "publisher")
    need(identity.get("studio") == "PIRATE DADDIES FILM", "studio")
    need(
        yt.get("channelId") == "UCBx56jOoR5Md2dAQJk2BLDA"
        and re.fullmatch(r"UC[A-Za-z0-9_-]{22}", str(yt.get("channelId", ""))) is not None,
        "verifiedChannelId",
    )
    need(yt.get("title") == "Geoffrey Ward" and yt.get("handle") == "@geoffreyward3606", "observedChannelLabel")
    need(yt.get("primaryFormat") == "long", "longFormFocus")
    need(yt.get("identityConfirmedBy") == "vidiq_user_channels", "channelObservation")
    need(
        campaign.get("channels", {}).get("youtube", {}).get("role")
        == "longerBuildProofDevlogAndDemo",
        "campaignYouTubeRole",
    )
    b = brands.get("publicBrands", {})
    need(b.get("luhmOs", {}).get("displayName") == identity.get("product"), "canonicalProduct")
    need(b.get("luhmOs", {}).get("publisher") == identity.get("publisher"), "canonicalPublisher")
    need(b.get("eggieBagelface", {}).get("displayName") == identity.get("publisher"), "publicPublisher")
    need(b.get("pirateDaddiesFilm", {}).get("displayName") == identity.get("studio"), "studioBrand")
    need(route.get("existingDockModule") == "social", "existingSocialDock")
    need(route.get("runtimeStatus") == "NOT_PROVEN", "runtimeNotProven")
    for key in ("roleLabelsOnly",):
        need(route.get(key) is True, key)
    for key in ("independentAgentRuntime", "crossPluginInvocationVerified", "luHmMcpAppHostInstalledVerified"):
        need(route.get(key) is False, key)
    need(
        quarantine.get("state") == "QUARANTINED"
        and quarantine.get("activeTaskWorkersAllowed") is False
        and gates.get("noAutomaticAgentRelease") is True,
        "quarantineBoundary",
    )
    need(lanes.get("lanes", {}).get("cathedralPublic", {}).get("publicDistributionAllowed") is True, "publicLane")
    need(lanes.get("lanes", {}).get("privateMutation", {}).get("publicDistributionAllowed") is False, "privateLane")
    for key in (
        "publishRequiresExactChannelVideoAndFinalValues",
        "thumbnailChangeRequiresExactFinalImageApproval",
        "commentReplyRequiresExactCommentAndReplyApproval",
        "instagramPublishingIsSeparateAuthorization",
        "noAutomaticPosting",
        "noAutomaticCrossPosting",
        "noAutomaticRepoMerge",
        "noAutomaticAgentRelease",
        "noPaidApiActivation",
        "noBillableGenerationWithoutTaskSpecificBudget",
        "noRawPersonalOrPrivateMediaInPublicGit",
        "noPrivateDriveIdsOrTokensInPublicGit",
        "noAssumedExternalMcpToolBridge",
        "noUnlicensedOrPrivateOnlyArtInPublicOutputs",
        "noSubstituteVidIqForVertexVeo",
        "retainExistingBrandWithoutRenamingYoutubeChannel",
    ):
        need(gates.get(key) is True, "gate:" + key)
    need(approval.get("sourceDraftAllowed") is True, "sourceDraftAllowed")
    for key in ("release", "publicMarketing", "productionWrite"):
        need(approval.get(key) is False, "approval:" + key)
    need(approval.get("crownStatus") == "STOP", "crownStop")
    need(evidence.get("observationOnly") is True, "historicalObservation")
    need(evidence.get("authenticatedAccountIdentifiersExcluded") is True, "privateAccountExclusion")
    need(evidence.get("longFormUploadList", {}).get("count") == 0, "observedUploadCount")
    need(
        sorted(evidence.get("longFormUploadList", {}).get("includesPrivacyStatuses", []))
        == ["private", "public", "unlisted"],
        "uploadPrivacyScope",
    )
    need(bridge.get("validation", {}).get("liveMobileWidgetProof") is False, "noMobileProof")
    need(bridge.get("validation", {}).get("sourceCandidateIsNotDeployed") is True, "noDeployClaim")
    need(
        "@" not in json.dumps(bridge.get("observedSessionEvidence", {})),
        "privateOwnerAccountAbsent",
    )
    return errors


def negative_controls(bridge: dict, campaign: dict, brands: dict, quarantine: dict, lanes: dict) -> list[str]:
    tests = {
        "differentChannel": ("identities", "youtube", "channelId", "UCaaaaaaaaaaaaaaaaaaaaaa"),
        "automaticPublishing": ("hardGates", "noAutomaticPosting", None, False),
        "falseHostProof": ("route", "crossPluginInvocationVerified", None, True),
        "wrongPrimaryFormat": ("identities", "youtube", "primaryFormat", "short"),
        "removedQuarantineGate": ("hardGates", "noAutomaticAgentRelease", None, False),
    }
    failures = []
    for name, (parent, field, subfield, value) in tests.items():
        changed = deepcopy(bridge)
        if subfield:
            changed[parent][field][subfield] = value
        else:
            changed[parent][field] = value
        if not validate(changed, campaign, brands, quarantine, lanes):
            failures.append(name)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root
    required = {
        "bridge": "doctrine/vidIqOpenAiCanonBridgeV1.json",
        "campaign": "doctrine/unifiedCampaignWorkbenchV1.json",
        "brands": "doctrine/organizationBrandRegistryV1.json",
        "quarantine": "doctrine/companyWideOperationalQuarantineV1.json",
        "lanes": "doctrine/contentLaneDoctrineV1.json",
    }
    try:
        sources = {key: load(root, path) for key, path in required.items()}
        problems = validate(
            sources["bridge"], sources["campaign"], sources["brands"],
            sources["quarantine"], sources["lanes"],
        )
        negative_failures = negative_controls(
            sources["bridge"], sources["campaign"], sources["brands"],
            sources["quarantine"], sources["lanes"],
        )
        result = {
            "status": "VIDIQ_CANON_BRIDGE_SOURCE_GREEN"
            if not (problems or negative_failures) else "VIDIQ_CANON_BRIDGE_SOURCE_RED",
            "scope": "source consistency only",
            "channelId": sources["bridge"]["identities"]["youtube"]["channelId"],
            "negativeControls": 5,
            "problems": problems,
            "negativeControlFailures": negative_failures,
            "runtimeProven": False,
            "publicationAuthorized": False,
        }
        print(json.dumps(result, sort_keys=True))
        return int(bool(problems or negative_failures))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({
            "status": "VIDIQ_CANON_BRIDGE_SOURCE_RED",
            "failureKind": type(error).__name__,
            "runtimeProven": False,
            "publicationAuthorized": False,
        }))
        return 1


if __name__ == "__main__":
    sys.exit(main())
