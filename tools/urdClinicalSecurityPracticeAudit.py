#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

practice=json.loads((root/"doctrine/urdClinicalSecurityPracticeV1.json").read_text(encoding="utf-8"))
rooms=json.loads((root/"doctrine/escalationWorkflowRoomsV1.json").read_text(encoding="utf-8"))
control=json.loads((root/"doctrine/luhmAiControlPlaneV1.json").read_text(encoding="utf-8"))
truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text(encoding="utf-8"))
orientation=json.loads((root/"doctrine/enterpriseOrientationBridgeV1.json").read_text(encoding="utf-8"))

need(practice.get("schema")=="luhmOs.urdClinicalSecurityPractice.v1","Urd practice schema drift")
need(practice.get("owner")=="urdDoctorGoddess","Urd practice owner drift")
need(practice.get("reportsTo")=="lum","Urd reporting line drift")
need(practice.get("hipaaInspiredDiscipline",{}).get("legalComplianceClaim") is False,"HIPAA compliance overclaim")
need(practice.get("clinicalLibrary",{}).get("epicIntegrationClaim") is False,"Epic integration overclaim")
need(practice.get("clinicalLibrary",{}).get("accessMayGrantProjectAuthority") is False,"clinical library authority leak")
need(practice.get("escalationToLum",{}).get("urdMayApproveCorporatePolicy") is False,"Urd policy approval leak")
need(practice.get("escalationToLum",{}).get("lumMaySelfCrown") is False,"Lum self-Crown leak")
need(practice.get("escalationToLum",{}).get("professorFinalAuthority") is True,"Professor authority drift")
need(practice.get("technologyBoundary",{}).get("skuldTechnicalLevel")=="deepestResearchCompatibilityAndArchitectureSpecialist","Skuld technical role drift")

need(rooms.get("schema")=="luhmOs.escalationWorkflowRooms.v1","escalation room schema drift")
need(rooms.get("rooms",{}).get("forFuckSake",{}).get("passTarget")==25,"FFS tier drift")
need(rooms.get("rooms",{}).get("scorchedEarth",{}).get("passTarget")==50,"Scorched Earth tier drift")
need(rooms.get("rooms",{}).get("finalForm",{}).get("passTarget")=="STRUCTURAL","Final Form tier drift")
need(rooms.get("roleMap",{}).get("lum")=="supremeWitchPresidentChairPolicyAndLogistics","Lum escalation role drift")
need(rooms.get("roleMap",{}).get("urdDoctorGoddess")=="doctorPatientHealthSecurityAndSanity","Urd escalation role drift")

need(control.get("inherits",{}).get("urdClinicalSecurityPractice")=="doctrine/urdClinicalSecurityPracticeV1.json","control-plane Urd practice pointer missing")
need(control.get("inherits",{}).get("escalationWorkflowRooms")=="doctrine/escalationWorkflowRoomsV1.json","control-plane room pointer missing")
need(control.get("invariants",{}).get("lumSupremeWitch") is True,"Lum supreme-witch invariant missing")
need(control.get("invariants",{}).get("urdDoctorDoesNotOwnCorporateLogistics") is True,"Urd logistics separation missing")

need(truth.get("agentLayer",{}).get("lumOwnsCorporateLogistics") is True,"source-truth Lum logistics missing")
need(truth.get("agentLayer",{}).get("urdOwnsCorporateLogistics") is False,"source-truth Urd logistics drift")

corp=orientation.get("corporateOperatingModel",{})
need(corp.get("lum",{}).get("supremeWitch") is True,"enterprise Lum supreme-witch drift")
need(corp.get("professor",{}).get("title")=="mainStakeholderAndFinalCrownAuthority","Professor stakeholder role drift")
need(orientation.get("cabinetIntroductions",{}).get("urdDoctorGoddess",{}).get("canonicalTitle")=="doctorClinicalSecuritySanityAndEvidence","enterprise Urd canonical title drift")

print(json.dumps({
  "schema":"luhmOs.urdClinicalSecurityPracticeAudit.v1",
  "status":"GREEN_URD_CLINICAL_SECURITY_CANDIDATE" if not errors else "RED_URD_CLINICAL_SECURITY_CANDIDATE",
  "errors":errors,
  "crownStatus":"STOP"
},indent=2))
raise SystemExit(1 if errors else 0)
