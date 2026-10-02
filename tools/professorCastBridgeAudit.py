#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = (ROOT / ".github/workflows/professor-cast-bridge.yml").read_text(encoding="utf-8")
doctrine = json.loads((ROOT / "doctrine/PROFESSOR_CAST_BRIDGE_V1.json").read_text(encoding="utf-8"))

errors = []

def require(ok, msg):
    if not ok:
        errors.append(msg)

for token in (
    "issue_comment:",
    "types: [created]",
    "github.event.issue.pull_request",
    "github.event.comment.user.login == github.repository_owner",
    "github.event.comment.body == 'CAST'",
    "github.event.comment.body == 'castBridge'",
    "startsWith(github.event.comment.body, '/cast ')",
    "gh api \"repos/$GITHUB_REPOSITORY/branches/main\" --jq '.commit.sha'",
    "Short CAST aliases are diagnostic only",
    "::error title=Invalid CAST syntax",
    "REQUESTED_SHA",
    "MAIN_SHA",
    "gh workflow run android-testing-build.yml",
    "--ref main",
    "-f cast=cast",
    "-f milestoneId=androidWeb3Cockpit",
    "-f sourceRef=\"$SOURCE_REF\"",
    "-f professorActor=\"$PROFESSOR_ACTOR\"",
    "-f castOriginRunId=\"$CAST_ORIGIN_RUN_ID\"",
    "-f publishPrerelease=true",
):
    require(token in workflow, f"bridge missing required guard/control: {token}")

require("actions: write" in workflow, "bridge needs scoped actions: write to dispatch")
require(workflow.count("actions: write") == 1, "actions write permission must appear exactly once")
require("contents: write" not in workflow, "bridge may not write repository contents")
require("pull_request_target" not in workflow, "pull_request_target forbidden")
require("push:" not in workflow, "push trigger forbidden")
require("schedule:" not in workflow, "scheduled CAST forbidden")
require(re.search(r"\^/cast\[\[:space:\]\]\+androidWeb3Cockpit", workflow) is not None,
        "exact CAST syntax regex missing")
require("requested=$REQUESTED_SHA currentMain=$MAIN_SHA" in workflow,
        "source drift failure path missing")
require('echo "professorActor=$PROFESSOR_ACTOR"' in workflow,
        "bridge must export Professor actor")
require('echo "castOriginRunId=$GITHUB_RUN_ID"' in workflow,
        "bridge must export origin run ID")

require(doctrine.get("authority") == "Professor", "Professor authority drift")
trigger = doctrine.get("trigger", {})
require(trigger.get("requiredActor") == "github.repository_owner", "owner-only actor rule drift")
require(trigger.get("exactMainMatch") is True, "exact-main rule drift")
safety = doctrine.get("safety", {})
for key in ("noPersistentBuildAuthorization","noWildcardActor","noSourceDrift",
            "noStableRelease","noProductionSigning","noMergeAuthority","noCrownAuthority",
            "noBotImpersonation","botMayTransportAuthorizationOnlyWithVerifiedOrigin"):
    require(safety.get(key) is True, f"safety flag must remain true: {key}")
require(doctrine.get("crownStatus") == "STOP", "Crown must remain STOP")

print(json.dumps({
    "schema":"luhm-os.professor-cast-bridge-audit.v1",
    "status":"GREEN_PROFESSOR_CAST_BRIDGE" if not errors else "RED_PROFESSOR_CAST_BRIDGE",
    "errors":errors,
    "crownStatus":"STOP"
}, indent=2))
sys.exit(0 if not errors else 2)
