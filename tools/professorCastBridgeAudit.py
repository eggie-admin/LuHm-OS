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
completion = json.loads((ROOT / "doctrine/chatGptPluginCastCompletionV1.json").read_text(encoding="utf-8"))

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

require("steps.cast.outputs.requestedMilestone == 'androidProposedDebug'" in workflow, "missing PROPOSED exact CAST route")
require("-f milestoneId=androidProposedDebug" in workflow, "missing private PROPOSED build milestone")
require("-f publishPrerelease=false" in workflow, "PROPOSED build must not publish a prerelease")
require(doctrine.get("dispatch",{}).get("androidProposedDebug",{}).get("publishPrerelease") is False, "PROPOSED doctrine unexpectedly publishes")
require(doctrine.get("dispatch",{}).get("androidProposedDebug",{}).get("destination") == "ephemeralPrivateGitHubActionsArtifactOnly", "PROPOSED output destination drift")
android_build = (ROOT / ".github/workflows/android-testing-build.yml").read_text(encoding="utf-8")
require(
    "inputs.publishPrerelease && inputs.milestoneId != 'androidProposedDebug'" in android_build
    or (
        "\n  publish-prerelease:" in android_build
        and "    if: ${{ false }}" in android_build.split("\n  publish-prerelease:", 1)[1].split("\n    steps:", 1)[0]
    ),
    "PROPOSED publish guard missing at build workflow",
)

require("actions: write" in workflow, "bridge needs scoped actions: write to dispatch")
require(workflow.count("actions: write") == 1, "actions write permission must appear exactly once")
require("contents: write" not in workflow, "bridge may not write repository contents")
require("pull_request_target" not in workflow, "pull_request_target forbidden")
require("push:" not in workflow, "push trigger forbidden")
require("schedule:" not in workflow, "scheduled CAST forbidden")
for bad in ("MAIN_SHA", "REQUESTED_SHA", "SOURCE_REF", "RELEASE_TAG", "TASK_ID", "PROFESSOR_ACTOR", "CAST_ORIGIN_RUN_ID"):
    require(bad not in workflow, f"non-camelHump internal shell variable forbidden: {bad}")
require(re.search(r"\^/cast\[\[:space:\]\]\+\(androidProposedDebug\|androidWeb3Cockpit\|publicPluginPackage\)", workflow) is not None,
        "exact multi-milestone CAST syntax regex missing")
require("requested=$requestedSha currentMain=$mainSha" in workflow,
        "source drift failure path missing")
require('echo "professorActor=$professorActor"' in workflow,
        "bridge must export Professor actor")
require('echo "castOriginRunId=$GITHUB_RUN_ID"' in workflow,
        "bridge must export origin run ID")
require('-f professorActor="$professorActor"' in workflow,
        "bridge must pass professorActor to public package CAST")
require('-f castOriginRunId="$castOriginRunId"' in workflow,
        "bridge must pass castOriginRunId to public package CAST")

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

require(doctrine.get("authority") == "Professor", "Professor authority drift")
require(doctrine.get("schema") == "luhm-os.professor-cast-bridge.v5", "bridge schema drift")
require(doctrine.get("completionContract") == "doctrine/chatGptPluginCastCompletionV1.json",
        "CAST completion contract pointer missing")
trigger = doctrine.get("trigger", {})
require(trigger.get("requiredActor") == "github.repository_owner", "owner-only actor rule drift")
require(trigger.get("allowedMilestones") == ["androidProposedDebug","androidWeb3Cockpit","publicPluginPackage"], "allowed CAST milestones drift")
require(trigger.get("exactMainMatch") is True, "exact-main rule drift")
safety = doctrine.get("safety", {})
for key in (
    "noPersistentBuildAuthorization",
    "noWildcardActor",
    "noSourceDrift",
    "noStableRelease",
    "noProductionSigning",
    "noMergeAuthority",
    "noCrownAuthority",
    "noBotImpersonation",
    "botMayTransportAuthorizationOnlyWithVerifiedOrigin",
    "noPackageEqualsFinalPluginCast",
    "noForgedChatGptHostReceipt",
):
    require(safety.get(key) is True, f"safety flag must remain true: {key}")
require(doctrine.get("crownStatus") == "STOP", "Crown must remain STOP")
plugin_dispatch = doctrine.get("dispatch", {}).get("publicPluginPackage", {})
require(plugin_dispatch.get("workflow") == "public-plugin-package-cast.yml", "public plugin CAST dispatch missing")
require(plugin_dispatch.get("completionMeaning") == "PACKAGE_READY_ONLY",
        "package workflow may not claim final plugin CAST")
require(plugin_dispatch.get("finalCastRequires") == [
    "chatGptHostInstallProved",
    "currentConversationInvocationProved",
    "luhmOpenCockpitRuntimeProved",
], "final plugin CAST requirements drift")
require(trigger.get("diagnosticAliases") == ["CAST", "castBridge"], "diagnostic alias contract drift")
require(trigger.get("diagnosticAliasesDispatch") is False, "short aliases must never dispatch")
require(trigger.get("invalidAuthorizationFailsLoud") is True, "invalid authorization must fail loud")
require(safety.get("noImplicitShortAliasDispatch") is True, "implicit short-alias dispatch forbidden")

require(completion.get("command") == "CAST", "completion contract CAST command drift")
require(completion.get("automationLaw", {}).get("packageSuccessMustNotBeReportedAsFinalCast") is True,
        "completion contract allows package/final conflation")
require(completion.get("chatGptHost", {}).get("requiredRuntimeTool") == "luhm_open_cockpit",
        "completion contract runtime tool drift")


# Additional private PR411 route. This deliberately does not expand the
# generic current-main public/package milestone allowlist.
godotWebWorkflow = (ROOT / ".github/workflows/godot-web-harness.yml").read_text(encoding="utf-8")
expectedSourceRef = "55a10a74f4101ae557d37081cc671de1ceb74ff1"
for expectedToken in (
    "github.event.comment.user.login == github.repository_owner",
    'approvedSha="' + expectedSourceRef + '"',
    'prHead="$(gh api "repos/$GITHUB_REPOSITORY/pulls/411" --jq \'.head.sha\')"',
    'firstOwnerCommandId="$(gh api --paginate "repos/$GITHUB_REPOSITORY/issues/411/comments?per_page=100"',
    'if: steps.cast.outputs.requestedMilestone == \'witchingHourWeb\'',
    '-f milestoneId=proposedWitchingHourWeb20261025',
    '-f castOriginCommentId="$castOriginCommentId"',
    "privateArtifactOnly=true",
):
    require(expectedToken in workflow, "PR411 owner-bound CAST Bridge route missing: " + expectedToken)

for expectedToken in (
    "approvedPr=411",
    'approvedCommentId="$castOriginCommentId"',
    'expectedCommand="/cast witchingHourWeb $sourceRef"',
    'expectedMilestone="proposedWitchingHourWeb20261025"',
    'expectedTask="proposedWitchingHourFinalBoss"',
    '[[ "$approvalBody" == "$expectedCommand" ]]',
    '[[ "$firstOwnerCommandId" == "$castOriginCommentId" ]]',
    '[[ "$(gh api "repos/$GITHUB_REPOSITORY/pulls/$approvedPr" --jq \'.head.sha\')" == "$sourceRef" ]]',
):
    require(expectedToken in godotWebWorkflow, "PR411 delegated Godot gate missing: " + expectedToken)

require(expectedSourceRef in godotWebWorkflow, "PR411 exact source SHA not pinned in Godot gate")
require("noImplicitShortAliasDispatch" in safety and safety.get("noImplicitShortAliasDispatch") is True,
        "short diagnostic alias must not grant new PR411 CAST authority")

print(json.dumps({
    "schema":"luhm-os.professor-cast-bridge-audit.v2",
    "status":"GREEN_PROFESSOR_CAST_BRIDGE" if not errors else "RED_PROFESSOR_CAST_BRIDGE",
    "errors":errors,
    "pluginPackageCompletion":"PACKAGE_READY_ONLY",
    "finalPluginCast":"REQUIRES_CHATGPT_HOST_INSTALL_AND_CURRENT_CHAT_PROOF",
    "crownStatus":"STOP"
}, indent=2))
sys.exit(0 if not errors else 2)
