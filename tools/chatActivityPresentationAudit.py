#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors: list[str] = []

def require(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)

doctrine = json.loads((root / "doctrine/chatActivityPresentationV1.json").read_text(encoding="utf-8"))
cockpit = (root / "frontEnd/jquery/luhm.cockpit.js").read_text(encoding="utf-8")
html = (root / "frontEnd/index.html").read_text(encoding="utf-8")
godot = (root / "scripts/game/activityLoading.gd").read_text(encoding="utf-8")

require(doctrine.get("authority") == "Professor", "activity authority must remain Professor")
require(doctrine.get("crownStatus") == "STOP", "activity presentation may not grant Crown")
require(doctrine.get("safety", {}).get("noFakeProgress") is True, "fake progress must remain forbidden")
for key in ("noShellAuthority", "noReleaseAuthority", "noInstallAuthority", "noCrownAuthority", "typedBoundaryOnly"):
    require(doctrine.get("safety", {}).get(key) is True, f"safety flag must remain true: {key}")
require(doctrine.get("art", {}).get("automaticCanonPromotion") is False, "art preview may not auto-promote canon")
require(doctrine.get("art", {}).get("maximumConcurrentGenerationJobs") == 3, "media generation cap drift")
for event_type in ("taskStarted", "stageChanged", "imageCandidateReady", "taskComplete", "taskFailed"):
    require(event_type in doctrine.get("eventTypes", []), f"missing typed event: {event_type}")
require("activityEvent" in cockpit and "luhm:activity:update" in cockpit, "cockpit activity event missing")
require("typeof next.progress" in cockpit, "cockpit must distinguish measurable progress")
require("data-luhm-activity-progress" in html, "activity progress surface missing")
require("progress_bar.indeterminate = true" in godot, "Godot must support unknown progress")
require("present_activity(activity: Dictionary)" in godot, "Godot typed activity presenter missing")
for forbidden in ("OS.execute", "JavaScriptBridge.eval", "get_tree().quit"):
    require(forbidden not in godot, f"presentation layer forbidden capability: {forbidden}")

report = {
    "schema": "luhmOs.chatActivityPresentationAudit.v1",
    "status": "GREEN_CHAT_ACTIVITY_PRESENTATION" if not errors else "RED_CHAT_ACTIVITY_PRESENTATION",
    "errors": errors,
    "crownStatus": "STOP",
}
print(json.dumps(report, indent=2))
sys.exit(0 if not errors else 2)
