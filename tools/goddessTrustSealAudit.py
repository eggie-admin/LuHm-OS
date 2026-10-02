#!/usr/bin/env python3
import json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1]
p=root/"doctrine/goddessTrustSealV1.json"
d=json.loads(p.read_text())
bad=[]
principles=d.get("principles",{})
requiredTrue=["personalityIsNotAuthority","memoryIsNotProof","leastCapability","failClosed","exactSourceIdentityRequired"]
for k in requiredTrue:
    if principles.get(k) is not True: bad.append(["principleNotTrue",k])
requiredFalse=["selfApprovalAllowed","recursiveRecruitmentAllowed","implicitCrownAllowed","unsupportedGreenAllowed"]
for k in requiredFalse:
    if principles.get(k) is not False: bad.append(["principleNotFalse",k])
for name,role in d.get("roles",{}).items():
    if role.get("maySelfApprove") is True: bad.append(["selfApprovalLeak",name])
if d.get("roles",{}).get("urd",{}).get("role")!="unassignedUntilSealed":
    bad.append(["urdAuthorityInvented","urd"])
if d.get("crownStatus")!="stop": bad.append(["crownNotStopped",d.get("crownStatus")])
if bad:
    print(json.dumps({"status":"red","violations":bad},indent=2)); sys.exit(1)
print(json.dumps({"status":"greenTrustSealSourceAudit","selfApproval":False,"implicitCrown":False,"urdAuthority":"unassignedUntilSealed"},indent=2))
