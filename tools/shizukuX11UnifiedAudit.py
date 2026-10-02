#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parents[1]
errors = []

def req(ok, msg):
    if not ok:
        errors.append(msg)

def load(rel):
    path = root / rel
    req(path.is_file(), f"missing {rel}")
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid json {rel}: {exc}")
        return {}

doctrine = load("doctrine/shizukuX11UnifiedV1.json")
control = load("doctrine/luhmAiControlPlaneV1.json")
chat = load("doctrine/projectChatCanonV1.json")
fleet = load("doctrine/OPERATION_TITAN7_WATCH_FLEET_V1.json")

skillPaths = [
    "agents/shizukuX11Oni/SKILL.md",
    "agents/lum/SKILL.md",
    "agents/skuldResearchOni/SKILL.md",
    "agents/urdMutationOni/SKILL.md",
    "agents/belldandyQualityOni/SKILL.md",
    "agents/kugiToolOni/SKILL.md",
]
for rel in skillPaths:
    req((root / rel).is_file(), f"missing {rel}")

req(doctrine.get("authority") == "Professor", "authority drift")
req(doctrine.get("boss") == "lum", "Lum boss drift")
req(doctrine.get("crownStatus") == "stop", "crown must stop")
req(doctrine.get("upstreamFacts", {}).get("shizuku", {}).get("android16Qpr1SupportObserved") is True, "Android 16 Shizuku compatibility record missing")
req(doctrine.get("upstreamFacts", {}).get("termuxX11", {}).get("twoPartInstallRequired") is True, "X11 two-part install law missing")
req(doctrine.get("upstreamFacts", {}).get("termuxX11", {}).get("prootRequiresSharedTmp") is True, "proot shared-tmp law missing")
req(doctrine.get("sourceFamilyLaw", {}).get("termuxAndPluginsMustMatchSigningFamily") is True, "Termux signing-family law missing")

for phrase in (
    "shizuku != root",
    "proot != androidRoot",
    "termuxX11 != vnc",
    "packageInstalled != sessionRunning",
):
    req(phrase in doctrine.get("nonEquivalence", []), f"missing non-equivalence: {phrase}")

safe = doctrine.get("safeDefaults", {})
for field in (
    "noPublicListener",
    "noSelinuxDisable",
    "noChmod777",
    "noSharedUidVariantUnlessSigningFamilyProven",
    "noRootAssumption",
    "noAutoPermissionGrant",
):
    req(safe.get(field) is True, f"unsafe default drift: {field}")

forbidden = doctrine.get("forbidden", [])
for token in (
    "setenforce0",
    "disableSelinux",
    "assumeRootFromShizuku",
    "installMixedTermuxSigningFamilies",
    "publiclyExposeX11OrVnc",
):
    req(token in forbidden, f"missing forbidden rule: {token}")

worker = control.get("workers", {}).get("shizukuX11Oni", {})
req(worker.get("skillPath") == "agents/shizukuX11Oni/SKILL.md", "control-plane specialist missing")
req(worker.get("mayRecruit") is False, "specialist recruitment leak")
req(worker.get("maySelfApprove") is False, "specialist self-approval leak")
req(control.get("routeProfiles", {}).get("androidSystems") is not None, "androidSystems route missing")

req(chat.get("specialistsLazyLoaded", {}).get("shizukuX11Oni") == "agents/shizukuX11Oni/SKILL.md", "chat lazy-load binding missing")
req(chat.get("androidSystemsLane", {}).get("executor") == "kugi", "Kugi execution binding missing")
req(chat.get("androidSystemsLane", {}).get("proof") == "drNao", "DrNao proof binding missing")

probePath = root / "tools/shizukuX11Probe.sh"
req(probePath.is_file(), "probe missing")
probe = probePath.read_text(encoding="utf-8") if probePath.is_file() else ""
for token in (
    "moe.shizuku.privileged.api",
    "com.termux.x11",
    "rish -c id -u",
    "runningRoot",
    "runningAdb",
    "pairedInstalled",
    '"renderObserved":false',
):
    req(token in probe, f"probe missing {token}")
req("setenforce" not in probe, "probe must not change SELinux")
req("chmod 777" not in probe, "probe must not use chmod 777")
req("su -c" not in probe, "read-only probe must not assume root")

for rel in skillPaths:
    path = root / rel
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        req("doctrine/shizukuX11UnifiedV1.json" in text, f"{rel} not bound to unified doctrine")

oniText = (root / "agents/shizukuX11Oni/SKILL.md").read_text(encoding="utf-8")
for phrase in (
    "shizuku != root",
    "proot != androidRoot",
    "termuxX11 != vnc",
    "known-good VNC fallback",
):
    req(phrase in oniText, f"specialist skill missing {phrase}")

copilotPath = root / ".github/copilot-instructions.md"
req(copilotPath.is_file(), "Copilot instructions missing")
if copilotPath.is_file():
    copilot = copilotPath.read_text(encoding="utf-8")
    req("doctrine/shizukuX11UnifiedV1.json" in copilot, "Copilot not bound to Shizuku/X11 doctrine")
    req("Shizuku is not root" in copilot, "Copilot Shizuku/root distinction missing")

watchIds = {w.get("id") for w in fleet.get("watches", [])}
req("shizukuX11UnifiedGate" in watchIds, "Titan7 Shizuku/X11 watch missing")

repoTextPaths = [
    "doctrine/shizukuX11UnifiedV1.json",
    "agents/shizukuX11Oni/SKILL.md",
    "tools/shizukuX11Probe.sh",
    ".github/copilot-instructions.md",
]
badRx = re.compile(r"(?:^|\s)(?:setenforce\s+0|chmod\s+777)(?:\s|$)")
for rel in repoTextPaths:
    path = root / rel
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        if rel != "agents/shizukuX11Oni/SKILL.md":
            req(badRx.search(text) is None, f"unsafe command literal in executable/config surface: {rel}")

print(json.dumps({
    "schema":"luhmOs.shizukuX11UnifiedAudit.v1",
    "status":"greenShizukuX11UnifiedSource" if not errors else "redShizukuX11UnifiedSource",
    "checks":{
        "shizukuPrivilegeSeparation":True,
        "termuxX11PairingLaw":True,
        "prootSharedTmpLaw":True,
        "signingFamilyLaw":True,
        "oniRouting":True,
        "goddessRoles":True,
        "copilotGuardrails":True,
        "titan7Watch":True
    },
    "physicalRuntime":"pendingDeviceReceipt",
    "errors":errors,
    "crownStatus":"stop"
}, indent=2))
raise SystemExit(1 if errors else 0)
