#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = (ROOT / ".github/workflows/professor-cast-bridge.yml").read_text(encoding="utf-8")
package_workflow = (ROOT / ".github/workflows/public-plugin-package-cast.yml").read_text(encoding="utf-8")
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
    "requestedSha",
    "mainSha",
    "gh workflow run android-testing-build.yml",
    "gh workflow run public-plugin-package-cast.yml",
    "--ref main",
    "-f cast=cast",
    "-f milestoneId=androidWeb3Cockpit",
    "-f sourceRef=\"$sourceRef\"",
    "-f professorActor=\"$professorActor\"",
    "-f castOriginRunId=\"$castOriginRunId\"",
    "-f publishPrerelease=true",
    "-f milestoneId=publicReleaseCandidate",
):
    require(token in workflow, f"bridge missing required guard/control: {token}")

require("actions: write" in workflow, "bridge needs scoped actions: write to dispatch")
require(workflow.count("actions: write") == 1, "actions write permission must appear exactly once")
require("contents: write" not in workflow, "bridge may not write repository contents")
require("pull_request_target" not in workflow, "pull_request_target forbidden")
require("push:" not in workflow, "push trigger forbidden")
require("schedule:" not in workflow, "scheduled CAST forbidden")
for bad in ("MAIN_SHA", "REQUESTED_SHA", "SOURCE_REF", "RELEASE_TAG", "TASK_ID", "PROFESSOR_ACTOR", "CAST_ORIGIN_RUN_ID"):
    require(bad not in workflow, f"non-camelHump internal shell variable forbidden: {bad}")
require(re.search(r"\^/cast\[\[:space:\]\]\+\(androidWeb3Cockpit\|publicPluginPackage\)", workflow) is not None,
        "exact multi-milestone CAST syntax regex missing")
require("requested=$requestedSha currentMain=$mainSha" in workflow,
        "source drift failure path missing")
require('echo "professorActor=$professorActor"' in workflow,
        "bridge must export Professor actor")
require('echo "castOriginRunId=$GITHUB_RUN_ID"' in workflow,
        "bridge must export origin run ID")

require(doctrine.get("authority") == "Professor", "Professor authority drift")
trigger = doctrine.get("trigger", {})
require(trigger.get("requiredActor") == "github.repository_owner", "owner-only actor rule drift")
require(trigger.get("allowedMilestones") == ["androidWeb3Cockpit","publicPluginPackage"], "allowed CAST milestones drift")
require(trigger.get("exactMainMatch") is True, "exact-main rule drift")
safety = doctrine.get("safety", {})
for key in ("noPersistentBuildAuthorization","noWildcardActor","noSourceDrift",
            "noStableRelease","noProductionSigning","noMergeAuthority","noCrownAuthority",
            "noBotImpersonation","botMayTransportAuthorizationOnlyWithVerifiedOrigin"):
    require(safety.get(key) is True, f"safety flag must remain true: {key}")
require(doctrine.get("crownStatus") == "STOP", "Crown must remain STOP")
require(doctrine.get("dispatch",{}).get("publicPluginPackage",{}).get("workflow") == "public-plugin-package-cast.yml", "public plugin CAST dispatch missing")
require(trigger.get("diagnosticAliases") == ["CAST", "castBridge"], "diagnostic alias contract drift")
require(trigger.get("diagnosticAliasesDispatch") is False, "short aliases must never dispatch")
require(trigger.get("invalidAuthorizationFailsLoud") is True, "invalid authorization must fail loud")
require(safety.get("noImplicitShortAliasDispatch") is True, "implicit short-alias dispatch forbidden")

print(json.dumps({
    "schema":"luhm-os.professor-cast-bridge-audit.v1",
    "status":"GREEN_PROFESSOR_CAST_BRIDGE" if not errors else "RED_PROFESSOR_CAST_BRIDGE",
    "errors":errors,
    "crownStatus":"STOP"
}, indent=2))
sys.exit(0 if not errors else 2)

for token in (
    "professorActor:",
    "castOriginRunId:",
    "actions: read",
    'GITHUB_ACTOR" == "github-actions[bot]"',
    'originEvent" != "issue_comment"',
    'originActor" != "$PROFESSOR_ACTOR"',
    'originSha" != "$SOURCE_REF"',
    '--actor "$PROFESSOR_ACTOR"',
):
    require(token in package_workflow, f"public package CAST provenance missing: {token}")

require('-f professorActor="$professorActor"' in workflow,
        "bridge must pass professorActor to public package CAST")
require('-f castOriginRunId="$castOriginRunId"' in workflow,
        "bridge must pass castOriginRunId to public package CAST")
