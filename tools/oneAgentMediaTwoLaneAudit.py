#!/usr/bin/env python3
"""Source-only acceptance gate for the single coordinator/two visible lane cockpit.

This test does not deploy, poll, stream media, access personal files, or start agents.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BAD = []

def need(ok: bool, label: str) -> None:
    if not ok:
        BAD.append(label)

def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")

def main() -> int:
    try:
        contract = json.loads(read("doctrine/oneAgentMediaTwoLaneV1.json"))
        quarantine = json.loads(read("doctrine/companyWideOperationalQuarantineV1.json"))
        experience = json.loads(read("doctrine/inChatExperienceV1.json"))
        media = json.loads(read("doctrine/localMediaDeckV1.json"))
        pets = json.loads(read("doctrine/characterPetPresentationV1.json"))
        atlas = json.loads(read("doctrine/agentLoadingSpriteManifestV1.json"))
        widget = read("host/harness/widget.html")
        mobile = read("host/harness/mobileCockpitWidget.html")
        standalone = read("host/harness/index.html")
        script = read("host/harness/twoThreadDesk.js")
        styles = read("host/harness/cockpit.css")
        server = read("host/mcp/luhmHarness.py")
        manual = read("manual/one-agent-media-two-lane.md")
        need(contract.get("schema") == "luhmOs.oneAgentMediaTwoLane.v1", "contractSchema")
        need(contract.get("status") == "SOURCE_CANDIDATE_NOT_DEPLOYED", "sourceOnly")
        need(contract.get("authority") == "Professor", "humanAuthority")
        need(contract.get("identity", {}).get("product") == "LuHm-OS", "productIdentity")
        op = contract.get("operator", {})
        need(op.get("singleConductor") == experience.get("boss") == "lum", "singleLum")
        need(op.get("conductorMode") == "SUPERVISED_CONVERSATION_ROLE_ONLY", "conductorNotWorker")
        need(op.get("activeExternalWorkers") == 0 and op.get("claimedDeploy") is False, "zeroWorkers")
        need(quarantine.get("state") == op.get("companyQuarantine") == "QUARANTINED" and
             quarantine.get("activeTaskWorkersAllowed") is False, "quarantine")
        need(quarantine.get("registeredCount") == 15, "rosterCount")
        p = contract.get("presentation", {})
        need(p.get("threadsAreUiLanesNotProcesses") is True and p.get("sameChatSurface") is True, "twoVisualLanes")
        need(p.get("top", {}).get("polling") is False and p.get("top", {}).get("hiddenAgent") is False, "noHiddenMonitor")
        need(p.get("bottom", {}).get("maxBubbleLines") == pets.get("petSystem", {}).get("bubble", {}).get("maxLines") == 3, "bubbleBudget")
        need(p.get("bottom", {}).get("pet") == atlas.get("agentIds", [None])[0] == "lum", "petBoss")
        for text, title in ((widget, "widget"), (mobile, "mobile"), (standalone, "standalone")):
            a, b = text.find('id="monitorThread"'), text.find('id="petChatThread"')
            if title == "standalone":
                a, b = text.find('id="laneMonitor"'), text.find('id="lanePetChat"')
            need(a >= 0 and b > a, title + "TopAboveBottom")
            need("aria-live" in text and "role=\"status\"" in text, title + "Accessibility")
            need(not re.search(r'<script[^>]+src=["\']https?://', text, re.I), title + "NoRemoteScript")
        need('id="twoLaneMobileChat"' in mobile and "renderTwoLane(d)" in mobile, "mobileHostData")
        need("renderTwoThread(payload)" in widget and "wireTwoThread()" in widget, "inChatHostData")
        need("renderTwoThread(null)" in widget and "renderTwoLane(null)" in mobile, "failClosed")
        need('src="/harness/assets/twoThreadDesk.js"' in standalone, "standaloneScript")
        need('"twoThreadDesk.js"' in server and '"cockpit.js"' in server, "assetRouteAllowlist")
        need('addEventListener("click"' in script and 'fetch("/harness/config.json"' in script, "onDemandRead")
        need("AbortController" in script and "clearTimeout" in script, "boundedRead")
        need("no worker" in script.lower() and "no worker" in widget.lower(), "noFakeWorker")
        need("prefers-reduced-motion" in styles and "prefers-reduced-motion" in mobile, "reducedMotion")
        need(media.get("vlc", {}).get("browserVlcPlugin") is False and media.get("backend", {}).get("mediaUpload") is False, "localMediaLaw")
        m = contract.get("media", {})
        need(m.get("vlc", {}).get("browserPlugin") is False and m.get("vlc", {}).get("rawHttpInterface") is False, "vlcBoundary")
        need(m.get("kodi", {}).get("legacyAlias") == "XBMC" and m.get("kodi", {}).get("remoteJsonRpcDefault") is False, "kodiBoundary")
        need(m.get("plex", {}).get("serverBundled") is False and m.get("plex", {}).get("localOrRemoteOwnerAuthRequired") is True, "plexBoundary")
        need(contract.get("cody", {}).get("installed") is False, "codyNotClaimed")
        release = contract.get("release", {})
        for x in ("noSilentCrossPost", "noNewDaemons", "noNewServers", "noPaidProviderByDefault", "noConfigSecretLogging", "noAutoMerge", "noAutoPublish", "noAutoDeploy", "noAgentUnquarantine"):
            need(release.get(x) is True, x)
        need(release.get("crown") == "STOP", "crownStop")
        need("zero autonomous agents" in manual.lower(), "manualQuarantine")
        print(json.dumps({
            "status": "ONE_AGENT_MEDIA_TWO_LANE_SOURCE_GREEN" if not BAD else "ONE_AGENT_MEDIA_TWO_LANE_SOURCE_RED",
            "failed": BAD, "workers": 0, "runtimeProven": False, "mobileChatGptHostProven": False,
            "publishAuthorized": False,
        }, sort_keys=True))
        return int(bool(BAD))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "ONE_AGENT_MEDIA_TWO_LANE_SOURCE_RED", "errorKind": type(exc).__name__, "runtimeProven": False}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
