#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

cab_path=root/"doctrine/lumGoddessCabinetV1.json"
ctl_path=root/"doctrine/luhmAiControlPlaneV1.json"
chat_path=root/"doctrine/projectChatCanonV1.json"
truth_path=root/"doctrine/SOURCE_OF_TRUTH.json"

for p in (cab_path,ctl_path,chat_path,truth_path):
    need(p.is_file(),f"missing {p.relative_to(root)}")

if cab_path.is_file():
    cab=json.loads(cab_path.read_text())
    need(cab.get("boss")=="lum","Lum boss drift")
    members={m.get("id") for m in cab.get("members",[])}
    expected={"lum","urdDoctorGoddess","belldandySecretary","skuldResearch"}
    need(members==expected,f"cabinet members drift: {sorted(members)}")
    binding=cab.get("covenantBinding",{})
    need(binding.get("contract")=="doctrine/everlastingCovenantV1.json","covenant contract drift")
    need((root/"doctrine/everlastingCovenantV1.json").is_file(),"missing covenant source")
    need(set(binding.get("requiredForMembers",[]))==expected,"covenant member coverage drift")
    for key in ("loadBeforeWork","acknowledgementRequired","evidenceRequiredForClaims","unknownRemainsUnknown"):
        need(binding.get(key) is True,f"covenant binding missing {key}")
    for key in ("acknowledgementGrantsAuthority","selfApproval","runtimeAcknowledgementsProven"):
        need(binding.get(key) is False,f"covenant unsupported authority or runtime claim: {key}")
    requiredAck={"taskId","scopeId","sourceRef","workerId","covenantRef","covenantDigest","observedAt"}
    need(set(binding.get("acknowledgementFields",[]))==requiredAck,"covenant acknowledgement identity drift")
    need(binding.get("missingOrMismatchedAcknowledgement")=="STOP","covenant acknowledgement fails open")
    need(bool(binding.get("truthfulRepresentation")),"missing truthful representation law")
    need({"covenantRef","covenantDigest"}.issubset(cab.get("sharedContextPacket",[])),"covenant missing from shared context")
    loop=cab.get("cabinetLoop",[])
    need("verifyCovenantAcknowledgements" in loop and "goddessesReturnIndependentSpecialtyPackets" in loop and loop.index("verifyCovenantAcknowledgements") < loop.index("goddessesReturnIndependentSpecialtyPackets"),"covenant acknowledgement must precede work results")
    law=cab.get("acquaintanceLaw",{})
    for k in ("sharedCabinetContextRequired","everyMemberKnowsAllRoles","everyMemberKnowsAuthorityBoundary","everyMemberKnowsHandoffVocabulary","helpersSpeakToLum","readOnlyPeerAwareness","disagreementReturnsToLum","professorFinalAuthority"):
        need(law.get(k) is True,f"acquaintance law missing {k}")
    need(law.get("goddessesDoNotRecruitEachOther") is True,"goddess recruitment leak")
    need(law.get("directCrossGoddessExecution") is False,"cross-goddess execution leak")
    need(law.get("residentDuringActiveTaskEnvelope") is True,"goddess cabinet not resident during active task")
    need(law.get("residentPresenceDoesNotImplyHiddenAsync") is True,"resident presence hidden async ambiguity")
    resident_ops=cab.get("residentOperations",{})
    need(resident_ops.get("residentGoddesses")==["urdDoctorGoddess","belldandySecretary","skuldResearch"],"resident goddess triplet drift")
    need(resident_ops.get("stateWhileTaskEnvelopeOpen")=="RESIDENT","resident task state drift")
    need(resident_ops.get("stateWithoutTaskEnvelope")=="PARKED","resident parked state drift")
    need(resident_ops.get("specialtyStateWhenRouted")=="ACTIVE","specialty active state drift")
    need(resident_ops.get("nonSpecialtyResidentState")=="RESIDENT","non-specialty resident state drift")
    need(resident_ops.get("hiddenAsyncExecution") is False,"resident operations hidden async leak")
    need(resident_ops.get("residentPresenceGrantsAuthority") is False,"resident presence authority leak")
    bhand=cab.get("handoffs",{}).get("lum->belldandySecretary",{})
    need("dictationIntake" in bhand.get("when",[]),"Belldandy dictation intake ownership missing")
    need("normalizedIntentPacket" in bhand.get("asksFor",[]),"Belldandy normalized intent packet missing")
    conflict=cab.get("conflictLaw",{})
    need(conflict.get("majorityVoteForbidden") is True,"majority-vote authority leak")
    need(conflict.get("deterministicRedBeatsAiConsensus") is True,"AI consensus may override deterministic RED")
    need(conflict.get("lumMayNotSilenceMinorityEvidence") is True,"Lum minority-evidence suppression allowed")
    peer=cab.get("peerAwareness",{})
    for who,others in {
        "urdDoctorGoddess":["lum","belldandySecretary","skuldResearch"],
        "belldandySecretary":["lum","urdDoctorGoddess","skuldResearch"],
        "skuldResearch":["lum","urdDoctorGoddess","belldandySecretary"],
    }.items():
        knows=peer.get(who,{}).get("knows",{})
        for other in others:
            need(other in knows,f"{who} does not know {other}")

skills={
    "lum":"agents/lum/SKILL.md",
    "urdDoctorGoddess":"agents/urdMutationOni/SKILL.md",
    "belldandySecretary":"agents/belldandyQualityOni/SKILL.md",
    "skuldResearch":"agents/skuldResearchOni/SKILL.md",
}
for ident,rel in skills.items():
    p=root/rel
    need(p.is_file(),f"missing skill {rel}")
    if p.is_file():
        txt=p.read_text()
        need("doctrine/lumGoddessCabinetV1.json" in txt,f"{ident} missing cabinet binding")
        need("CONFLICT" in txt,f"{ident} missing explicit conflict law")

if ctl_path.is_file():
    ctl=json.loads(ctl_path.read_text())
    gc=ctl.get("goddessCabinet",{})
    need(gc.get("contract")=="doctrine/lumGoddessCabinetV1.json","control plane cabinet contract drift")
    need(gc.get("consensusAuthority") is False,"cabinet consensus authority leak")

if chat_path.is_file():
    chat=json.loads(chat_path.read_text())
    need(chat.get("alwaysLoadedCore",{}).get("goddessCabinet")=="doctrine/lumGoddessCabinetV1.json","cabinet not always loaded")
    need("doctrine/lumGoddessCabinetV1.json" in chat.get("loadOrder",[]),"cabinet missing from load order")

if truth_path.is_file():
    truth=json.loads(truth_path.read_text())
    core=truth.get("goddessCore",{})
    need(core.get("cabinetContract")=="doctrine/lumGoddessCabinetV1.json","source truth cabinet contract drift")
    need(core.get("consensusAuthority") is False,"source truth consensus authority leak")

print(json.dumps({
    "schema":"luhmOs.lumGoddessCabinetAudit.v1",
    "status":"GREEN_LUM_GODDESS_CABINET_CANDIDATE" if not errors else "RED_LUM_GODDESS_CABINET_CANDIDATE",
    "members":["lum","urdDoctorGoddess","belldandySecretary","skuldResearch"],
    "mutualRoleAwareness":not errors,
    "consensusAuthority":False,
    "crownStatus":"STOP",
    "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)
