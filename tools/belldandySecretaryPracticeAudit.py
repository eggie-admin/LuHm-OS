#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

control=json.loads((root/"doctrine/luhmAiControlPlaneV1.json").read_text(encoding="utf-8"))
cabinet=json.loads((root/"doctrine/lumGoddessCabinetV1.json").read_text(encoding="utf-8"))
naming=json.loads((root/"doctrine/namingNamespaceCanonV1.json").read_text(encoding="utf-8"))
help_doc=json.loads((root/"doctrine/commandHelpV1.json").read_text(encoding="utf-8"))
voice=json.loads((root/"doctrine/voiceAmbientIntentV1.json").read_text(encoding="utf-8"))
bel=(root/"agents/belldandyQualityOni/SKILL.md").read_text(encoding="utf-8")
koe=(root/"agents/koeDictationOni/SKILL.md").read_text(encoding="utf-8")

b=control.get("agents",{}).get("belldandySecretary",{})
lane=b.get("secretaryLane",{})
need(b.get("defaultAuthority")=="READ_ONLY","Belldandy authority drift")
need(lane.get("dictationScribe")=="koe","Koe secretary binding missing")
need(lane.get("recordsRegistrar")=="fumi","Fumi secretary binding missing")
need(lane.get("deterministicExecutionBridge")=="kugi","Kugi bridge missing")
need(lane.get("evidenceDoctor")=="urdDoctorGoddess","Urd secretary consult missing")
need(lane.get("technicalInterpreter")=="skuldResearch","Skuld secretary consult missing")
need(lane.get("conversationalBoss")=="lum","Lum boss drift")

need(cabinet.get("secretaryLane",{}).get("owner")=="belldandySecretary","cabinet secretary owner drift")
loop=cabinet.get("professorDictationLoop",[])
for step in ("koePreserveAndNormalize","belldandyBindContinuityAndCanonicalNames","urdEvidenceCheckWhenClaimOrRiskRequiresIt","skuldTechnicalMeaningWhenTechnologyRequiresIt","lumRouteOrPresent"):
    need(step in loop,f"dictation loop missing: {step}")

recovery=naming.get("personCenteredDegradation",{}).get("recoveryLaw",{})
need(recovery.get("canonicalIdentityNeverDiscarded") is True,"canonical name discard allowed")
need(recovery.get("helpMustResolveEveryRegisteredAlias") is True,"alias help recovery missing")
need(help_doc.get("behavior",{}).get("helpMayMutate") is False,"help authority leak")

aliases=voice.get("voiceAliases",{}).get("projectContextAliases",{})
need(aliases.get("Mom",{}).get("canonical")=="Lum","Mom->Lum project alias missing")
need(aliases.get("Bell dandy",{}).get("canonical")=="Belldandy","Belldandy dictation alias missing")
need(aliases.get("Skull",{}).get("canonical")=="Skuld","Skuld dictation alias missing")

for phrase in ("Professor dictation desk","Person-centered naming desk","Secretary Oni helpers"):
    need(phrase in bel,f"Belldandy skill missing: {phrase}")
for phrase in ("Project-context alias normalization","Person-centered naming packet"):
    need(phrase in koe,f"Koe skill missing: {phrase}")

print(json.dumps({
  "schema":"luhmOs.belldandySecretaryPracticeAudit.v1",
  "status":"GREEN_BELLDANDY_SECRETARY_CANDIDATE" if not errors else "RED_BELLDANDY_SECRETARY_CANDIDATE",
  "errors":errors,
  "mutationAuthority":False,
  "crownStatus":"STOP"
},indent=2))
raise SystemExit(1 if errors else 0)
