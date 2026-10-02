#!/usr/bin/env python3
import json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1]
d=json.loads((root/"doctrine/goddessTrustSealV1.json").read_text())
bad=[]
p=d.get("principles",{})
for k in ["personalityIsNotAuthority","memoryIsNotProof","leastCapability","failClosed","exactSourceIdentityRequired"]:
    if p.get(k) is not True: bad.append(["principleNotTrue",k])
for k in ["selfApprovalAllowed","recursiveRecruitmentAllowed","implicitCrownAllowed","unsupportedGreenAllowed"]:
    if p.get(k) is not False: bad.append(["principleNotFalse",k])
roles=d.get("roles",{})
expected={"lum":"orchestrator","urd":"doctorGoddess","belldandy":"secretary","skuld":"research"}
for name,role in expected.items():
    if roles.get(name,{}).get("role")!=role: bad.append(["roleDrift",name,roles.get(name,{}).get("role"),role])
for name,role in roles.items():
    if role.get("maySelfApprove") is True: bad.append(["selfApprovalLeak",name])
if d.get("sharedSystemsPracticeRef")!="agents/goddessSharedSystemsPractice/SKILL.md": bad.append(["sharedPracticeDrift",d.get("sharedSystemsPracticeRef")])
watch=d.get("activeWorkWatch",{})
if watch.get("required") is not True or watch.get("mode")!="readOnlyCheckpointMonitoring": bad.append(["watchLoopMissing",watch])
if watch.get("mutationAuthority") is not False or watch.get("crownAuthority") is not False: bad.append(["watchAuthorityLeak",watch])
if d.get("crownStatus")!="stop": bad.append(["crownNotStopped",d.get("crownStatus")])
if bad:
    print(json.dumps({"status":"red","violations":bad},indent=2)); sys.exit(1)
print(json.dumps({"status":"greenTrustSealSourceAudit","sharedSystemsPractice":True,"activeWorkWatch":True,"goddessRoles":{"urd":"doctorGoddess","belldandy":"secretary","skuld":"research"},"selfApproval":False,"implicitCrown":False},indent=2))
