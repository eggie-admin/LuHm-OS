#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine" / "belldandyHousekeepingV1.json"
CONTROL = ROOT / "doctrine" / "luhmAiControlPlaneV1.json"
TRAINING = ROOT / "doctrine" / "agentTrainingSealV1.json"
SKILL = ROOT / "agents" / "belldandyQualityOni" / "SKILL.md"
PLUGIN_SKILL = ROOT / "plugins" / "luhm-os" / "skills" / "belldandy-housekeeping" / "SKILL.md"

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

errors: list[str] = []
policy = load(POLICY)
control = load(CONTROL)
training = load(TRAINING)
skill = SKILL.read_text(encoding="utf-8")
plugin_skill = PLUGIN_SKILL.read_text(encoding="utf-8")

window = policy.get("commitWindow", {})
if window.get("automaticCheckpointEveryCommits") != 25:
    errors.append("automatic checkpoint interval must be 25 commits")
if window.get("warningAtCommits") != 40:
    errors.append("warning threshold must be 40 commits")
if window.get("hardStopAtCommits") != 50:
    errors.append("hard stop must be 50 commits")
if window.get("ordinaryAuditHistoryMaxCommits") != 50:
    errors.append("ordinary audit history maximum must be 50 commits")
if policy.get("authorityBoundary", {}).get("belldandyMayMutate") is not False:
    errors.append("Belldandy must remain read-only")
if policy.get("prRunCleanup", {}).get("autoMerge") is not False:
    errors.append("Belldandy may not auto-merge")
if policy.get("prRunCleanup", {}).get("autoDeleteBranches") is not False:
    errors.append("Belldandy may not auto-delete branches")
if policy.get("crownStatus") != "STOP":
    errors.append("Crown must remain STOP")

belldandy = control.get("agents", {}).get("belldandySecretary", {})
for capability in (
    "housekeepingWindow",
    "snapshotPlanning",
    "prRunReconciliation",
    "doctrineSweep",
):
    if capability not in belldandy.get("capabilities", []):
        errors.append(f"missing Belldandy capability: {capability}")

if training.get("trainingState", {}).get("housekeepingTeaching") != "completeCandidate":
    errors.append("housekeeping training is not completeCandidate")
for phrase in ("50-commit", "automatic checkpoint", "Kugi"):
    if phrase.lower() not in skill.lower():
        errors.append(f"Belldandy skill missing housekeeping phrase: {phrase}")
if "read-only" not in plugin_skill.lower():
    errors.append("plugin housekeeping skill must remain read-only")

if errors:
    print(json.dumps({"status":"RED_BELLDANDY_HOUSEKEEPING","errors":errors}, indent=2))
    raise SystemExit(1)

print(json.dumps({
    "status":"GREEN_BELLDANDY_HOUSEKEEPING_SOURCE_CANDIDATE",
    "checkpointEveryCommits":25,
    "warningAtCommits":40,
    "hardStopAtCommits":50,
    "belldandyMutationAuthority":False,
    "automaticMerge":False,
    "automaticDelete":False,
    "crownStatus":"STOP"
}, indent=2))
