#!/usr/bin/env python3
import json, os, re, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
control=load("doctrine/luhmAiControlPlaneV1.json")
covenant=load("doctrine/everlastingCovenantV1.json")
truth=load("doctrine/currentSourceTruthV3.json")
lane=load("doctrine/proposedWorkingLaneV1.json")
naming=load("doctrine/camelHumpDoctrineLawV1.json")
urd_evidence=load("doctrine/urdEvidenceAdjudicationV1.json")
manifest_law=load("doctrine/aiManifestFormatV1.json")
chat=load("doctrine/projectChatCanonV1.json")
terms=load("doctrine/termResolutionV1.json")
progress=load("doctrine/chatProgressStreamV1.json")
sprites=load("doctrine/agentLoadingSpriteManifestV1.json")
runtime_sprites=json.loads((ROOT/"host/harness/agent-loading-sprites.json").read_text(encoding="utf-8"))
expected=["sanityCheck","audit","ingest","mutation","test","apply","continue","deploy"]
human=["so let it be written so let it be done","Do not tell me of the old magic, for I was there when we first wrote them","This is the law and our everlasting covenant."]
checks=[]
def add(name,ok): checks.append((name,bool(ok)))
by_id={x["agentId"]:x for x in sprites.get("sprites",[])}
for ident,a in control.get("agents",{}).items():
    item=by_id.get(ident,{})
    add(f"agent.{ident}.identity",ident in control["agents"])
    add(f"agent.{ident}.displayName",item.get("displayName")==a.get("displayName"))
    add(f"agent.{ident}.skillPath",item.get("skillPath")==a.get("skillPath"))
    add(f"agent.{ident}.capabilities",bool(a.get("capabilities")) and a.get("defaultAuthority") in control.get("authorityClasses",[]))
global_checks=[
("covenant.canonicalStatus",covenant.get("status")=="canonicalLaw" and covenant.get("professorApproval") is True and covenant.get("crownStatus")=="crownedMilestone" and covenant.get("crownReceipt")=="doctrine/everlastingCovenantCrownReceiptV1.json" and truth.get("everlastingCovenant",{}).get("status")=="CANONICAL_LAW"),
("covenant.humanLaw",covenant.get("humanLaw")==human),
("covenant.guardRailOrder",covenant.get("guardRail",{}).get("orderedStates")==expected),
("covenant.redUnknownFailClosed",covenant.get("guardRail",{}).get("redLaw","").startswith("RED, UNKNOWN")),
("covenant.sourceRepairRestarts","restart" in covenant.get("guardRail",{}).get("mutationLoop","").lower()),
("covenant.noSelfPromotionOrCrown",covenant.get("guardRail",{}).get("selfPromotion") is False and covenant.get("guardRail",{}).get("automaticCrown") is False),
("covenant.mutationsRemainProposed",covenant.get("proposedLane",{}).get("currentDoctrineMutationsRemainProposed") is True),
("bindings.controlChatTruthLane",control.get("covenant",{}).get("guardRail")==expected and chat.get("workflowGuardRail",{}).get("orderedStates")==expected and truth.get("everlastingCovenant",{}).get("guardRail")==expected and lane.get("guardRail")==expected),
("bindings.sharedProtocols",all("sanityCheck -> audit -> ingest -> mutation -> test -> apply -> continue -> deploy" in (ROOT/p).read_text(encoding="utf-8") for p in ["agents/shared/ONI_PROTOCOL_V2.md","AGENTS.md",".github/copilot-instructions.md"])),
("agents.noSelfApprovalOrRecruitment",all(a.get("maySelfApprove") is False and a.get("mayRecruit") is False for a in control.get("agents",{}).values())),
("goddesses.exactTriad",sprites.get("goddessGroup",{}).get("machineIds")==["urdDoctorGoddess","belldandySecretary","skuldResearch"]),
("goddesses.canonicalRoles",all(control["agents"][i].get("kind")==r for i,r in [("urdDoctorGoddess","doctorGoddess"),("belldandySecretary","secretaryGoddess"),("skuldResearch","researchGoddess")])),
("goddesses.readOnly",all(control["agents"][i].get("defaultAuthority")=="READ_ONLY" for i in ["urdDoctorGoddess","belldandySecretary","skuldResearch"])),
("goddesses.noGroupConsensus",terms.get("groups",{}).get("goddessTriad",{}).get("consensusAuthority") is False),
("terms.schema",terms.get("schema")=="luhmOs.termResolution.v1"),
("terms.dreamchanTarget",terms.get("aliases",{}).get("dreamchan",{}).get("canonicalAgentId")=="yume"),
("terms.dreamchanVoiceOnly",terms.get("aliases",{}).get("dreamchan",{}).get("acceptedInputModality")==["voiceDictation"]),
("terms.typedDreamchanUnknown",terms.get("aliases",{}).get("dreamchan",{}).get("typedTextBehavior")=="UNKNOWN_REQUIRES_CLARIFICATION" and terms.get("aliases",{}).get("dreamchan",{}).get("mayCreateAgent") is False),
("terms.explicitLearningOnly",terms.get("learningPolicy",{}).get("persistCanonicalAliasOnlyAfter")==["explicitUserConfirmation","unambiguousExplicitCorrection"] and terms.get("learningPolicy",{}).get("inferFromSingleTypo") is False),
("terms.goddessGroupExpansion",terms.get("groups",{}).get("goddessTriad",{}).get("members")==["urdDoctorGoddess","belldandySecretary","skuldResearch"]),
("terms.ambiguityFailsClosed",terms.get("failureBehavior",{}).get("ambiguous")=="UNKNOWN_REQUIRES_CLARIFICATION"),
("progress.schema",progress.get("schema")=="luhmOs.chatProgressStream.v1"),
("progress.identityBound",set(["taskId","sourceRef","scopeId"]).issubset(progress.get("event",{}).get("required",[]))),
("progress.compact",progress.get("presentation",{}).get("default")=="compact" and progress.get("presentation",{}).get("maxVisibleLines",99)<=5),
("progress.realTransitionsOnly",progress.get("event",{}).get("emitWhen")=="actual stage transition only"),
("progress.noChainOfThought",progress.get("presentation",{}).get("includeChainOfThought") is False),
("progress.noRawLogs",progress.get("presentation",{}).get("includeRawLogs") is False),
("progress.noHiddenAsync",progress.get("execution",{}).get("hiddenAsyncExecution") is False and progress.get("execution",{}).get("visibleBackgroundProcess")=="GitHub Actions pull-request checks" and progress.get("execution",{}).get("scheduledRuns") is False),
("identity.externalAuthEvidence",chat.get("externalIdentityEvidence",{}).get("googleDriveConnector")=="CONNECTED" and chat.get("externalIdentityEvidence",{}).get("googleIdentityOAuthCallback")=="UNVERIFIED" and chat.get("externalIdentityEvidence",{}).get("sentryMonitoringEvents")=="UNVERIFIED" and bool(chat.get("externalIdentityEvidence",{}).get("checkedAt"))),
("sprites.schema",sprites.get("schema")=="luhmOs.agentLoadingSpriteManifest.v1"),
("sprites.completeRoster",sprites.get("agentIds")==list(control.get("agents",{}).keys()) and set(by_id)==set(control.get("agents",{})) and [x.get("agentId") for x in runtime_sprites.get("sprites",[])]==sprites.get("agentIds")),
("sprites.largeFourByFourAtlas",sprites.get("grid",{}).get("columns")==4 and sprites.get("grid",{}).get("rows")==4 and struct.unpack(">II",(ROOT/sprites["assetPath"]).read_bytes()[16:24])==(1254,1254) and (ROOT/sprites["assetPath"]).read_bytes()[25] in (4,6)),
("sprites.loadingOnly",sprites.get("usage",{}).get("allowed")==["loadingScreen"] and sprites.get("usage",{}).get("loadingOnly") is True and sprites.get("usage",{}).get("avatarReplacement") is False and sprites.get("usage",{}).get("marketing") is False and "agentLoadingScreen" in (ROOT/"host/harness/index.html").read_text(encoding="utf-8") and "agent-roster-v1.png" in (ROOT/"host/mcp/luhmHarness.py").read_text(encoding="utf-8")),
("sprites.assetPresent",(ROOT/sprites.get("assetPath","")).is_file()),
("fleet.removed",all(not (ROOT/p).exists() for p in [".github/workflows/operation-titan7-watch-fleet.yml","doctrine/OPERATION_TITAN7_WATCH_FLEET_V1.json","tools/titan7WatchFleet.py"])),
("fleet.noScheduledTitan7",not any(re.search(r"^\\s*schedule\\s*:",p.read_text(encoding="utf-8",errors="ignore"),re.MULTILINE) and "titan7" in (p.name+p.read_text(encoding="utf-8",errors="ignore")).lower() for p in (ROOT/".github/workflows").glob("*") if p.is_file())),
("currentTruth.schema",truth.get("schema")=="luhmOs.currentSourceTruth.v3"),
("naming.currentLaw",truth.get("namingLaw",{}).get("contract")=="doctrine/camelHumpDoctrineLawV1.json" and naming.get("currentNaming",{}).get("machineIdentifiers")=="lowerCamelHump"),
("urd.drNaoRetired","drNao" not in control.get("agents",{}) and urd_evidence.get("legacyTreatment",{}).get("drNaoActiveAgent") is False),
("manifest.kebabCurrent",control.get("aiTaskManifest",{}).get("template")=="doctrine/aiTaskManifestV2.template.json" and manifest_law.get("fileNaming",{}).get("instanceFilenameStyle")=="kebab-case"),
]
for name,ok in global_checks: add(name,ok)
if len(checks)!=100: raise SystemExit(f"AUDIT_CONFIGURATION_ERROR expected=100 actual={len(checks)}")
source=os.environ.get("LUHM_SOURCE_REF","working-tree")
task=os.environ.get("GITHUB_RUN_ID","local-audit")
scope=os.environ.get("LUHM_SCOPE_ID","PR-134-doctrine-candidate")
print(f"[progress] {task} {source} {scope} doctrineAudit=active")
failed=[]
for i,(name,ok) in enumerate(checks,1):
    print(f"{'PASS' if ok else 'FAIL'} {i:03d}/100 {name}")
    if not ok: failed.append(name)
state="GREEN" if not failed else "RED"
summary=["## Doctrine lane audit",f"- Source: `{source}`",f"- Scope: `{scope}`",f"- Audit: **{state}** ({100-len(failed)}/100)","- Progress: visible CI only; no scheduled fleet or hidden execution.","- Google OAuth callback and Sentry event delivery: **UNVERIFIED**.","- Lane: **PROPOSED_ONLY** · Covenant Crown: **SCOPED MILESTONE** · Future doctrine Crown: **STOP**"]
out=os.environ.get("GITHUB_STEP_SUMMARY")
if out:
    with open(out,"a",encoding="utf-8") as f: f.write("\n".join(summary)+"\n")
print(f"[progress] {task} {source} {scope} doctrineAudit={state.lower()}")
if failed: raise SystemExit("AUDIT=RED failed="+",".join(failed))
print("EVERLASTING_COVENANT=GREEN")
print("passes=100/100")
print("lane=PROPOSED_ONLY")
print("deployMeaning=proposedCandidateOnly")
print("crown=STOP")
