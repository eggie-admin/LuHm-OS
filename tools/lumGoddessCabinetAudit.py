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
    law=cab.get("acquaintanceLaw",{})
    for k in ("sharedCabinetContextRequired","everyMemberKnowsAllRoles","everyMemberKnowsAuthorityBoundary","everyMemberKnowsHandoffVocabulary","helpersSpeakToLum","readOnlyPeerAwareness","disagreementReturnsToLum","professorFinalAuthority"):
        need(law.get(k) is True,f"acquaintance law missing {k}")
    need(law.get("goddessesDoNotRecruitEachOther") is True,"goddess recruitment leak")
    need(law.get("directCrossGoddessExecution") is False,"cross-goddess execution leak")
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
    "status":"greenLumGoddessCabinetCandidate" if not errors else "redLumGoddessCabinetCandidate",
    "members":["lum","urdDoctorGoddess","belldandySecretary","skuldResearch"],
    "mutualRoleAwareness":not errors,
    "consensusAuthority":False,
    "crownStatus":"stop",
    "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)
