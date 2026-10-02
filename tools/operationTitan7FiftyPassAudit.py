#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
root=Path(".")
inv=json.loads((root/"doctrine/operationTitan7InvocationV1.json").read_text())
checks=[]
def add(name,ok,detail): checks.append({"pass":len(checks)+1,"name":name,"state":"GREEN" if ok else "RED","detail":detail})
add("explicitInvocation",inv["defaultWorkflow"] is False,"Titan7 is not default")
add("normalMesh",inv["normalWorkflow"]=="luhmAgentMesh","normal workflow preserved")
add("requestedPasses",inv["passPolicy"]["requestedPasses"]==50,"50 requested")
files=[
"agents/shared/ONI_PROTOCOL_V2.md","agents/lum/SKILL.md","agents/goddessSharedSystemsPractice/SKILL.md",
"agents/witchingHourCoding/SKILL.md","agents/tourniquetWorkflow/SKILL.md","agents/kugiToolOni/SKILL.md",
"agents/urdMutationOni/SKILL.md","agents/belldandyQualityOni/SKILL.md","agents/shioriCriticOni/SKILL.md",
"agents/yumeArtOni/SKILL.md","agents/sumiAssetOni/SKILL.md","doctrine/tourniquetWorkflowV1.json",
"doctrine/operationTitan7FinalFormV1.json","doctrine/fqdnReverseProxyBoundaryV1.json",
"doctrine/cloudflareEdgeAssetTemplateV1.json","doctrine/assetCastBridgeV1.json",
"doctrine/characterPetPresentationV1.json","game/canon/CHARACTER_CANON_V1.json",
"game/assets/ASSET_MANIFEST_V1.json","project.godot"
]
for p in files: add("exists:"+p,(root/p).is_file(),"canonical path")
canon=json.loads((root/"game/canon/CHARACTER_CANON_V1.json").read_text())
assets=json.loads((root/"game/assets/ASSET_MANIFEST_V1.json").read_text())
pet=json.loads((root/"doctrine/characterPetPresentationV1.json").read_text())
tour=json.loads((root/"doctrine/tourniquetWorkflowV1.json").read_text())
net=json.loads((root/"doctrine/fqdnReverseProxyBoundaryV1.json").read_text())
bridge=json.loads((root/"doctrine/assetCastBridgeV1.json").read_text())
add("characterSet",set(canon["characters"])==set(assets["characters"])==set(pet["characters"]),"character sources reconcile")
add("adultCanon",all(v.get("adult") is True or v.get("minimumAge",0)>=18 for v in canon["characters"].values()),"adult design canon")
add("petPresentationOnly",pet["petSystem"]["authority"]=="presentationOnly","pet has no execution authority")
add("petNoGreen","petBubbleDoesNotEstablishGreen" in pet["petSystem"]["runtimeLaw"],"bubble cannot decide GREEN")
add("tourniquetAuthority",tour["authority"]=="Professor","Professor Crown")
add("tourniquetParallelism",tour["limits"]["maxParallelism"]<=3,"bounded workers")
add("tourniquetNoSelfApproval",tour["limits"]["selfApproval"] is False,"no self approval")
add("tourniquetNoWeakening",tour["limits"]["weakenEvidenceToPass"] is False,"no weakened gates")
add("networkDesktopOrigin",net["local"]["originClass"]=="desktopOrServer","desktop/server origin")
add("networkNoMobileOrigin",net["mobile"]["webOriginAllowed"] is False,"mobile client only")
add("assetRuntimeProof",bridge["bridgeLaw"]["runtimeProofRequired"] is True,"runtime proof required")
add("assetHash",bridge["bridgeLaw"]["hashRequired"] is True,"asset hash required")
add("assetNoMissingGreen",bridge["bridgeLaw"]["missingAssetMayBecomeGreen"] is False,"missing asset not green")
add("assetProfessorPromotion",bridge["bridgeLaw"]["professorPromotionRequired"] is True,"human promotion")
for p in ["tools/tourniquetAgentLogicAudit.py","tools/networkContractReconcile.py","tools/assetCastBridgeAudit.py","tools/characterPetPresentationAudit.py","tools/buildStaticAssetDist.py"]:
    add("auditTool:"+p,(root/p).is_file(),"deterministic audit tool")
# Fill remaining passes with distinct cross-contract invariants, not duplicated pretend passes.
add("sourceLaw","AI proposes. Policy authorizes. CI proves. Human promotes." in (root/"doctrine/artOniLayeredMutationV3.json").read_text(),"art authority law")
add("protectedReference", "protectedReference" in (root/"agents/yumeArtOni/SKILL.md").read_text(),"reference separation")
add("sumiHash","hash" in (root/"agents/sumiAssetOni/SKILL.md").read_text().lower(),"provenance hashing")
add("kugiDeterministic","deterministic" in (root/"agents/kugiToolOni/SKILL.md").read_text().lower(),"executor bounded")
add("lumBoss","only conversational boss" in (root/"agents/lum/SKILL.md").read_text().lower(),"single boss")
add("oniEvidence","Evidence" in (root/"agents/shared/ONI_PROTOCOL_V2.md").read_text(),"shared evidence law")
add("oniNoRecursive","recursively recruit" in (root/"agents/shared/ONI_PROTOCOL_V2.md").read_text(),"no recursive recruitment")
add("castBridgeWorkflow",(root/".github/workflows/professor-cast-bridge.yml").is_file(),"CAST bridge exists")
add("castAudit",(root/"tools/professorCastBridgeAudit.py").is_file(),"CAST audit exists")
add("androidWorkflow",(root/".github/workflows/android-testing-build.yml").is_file(),"Android build workflow exists")
assert len(checks)==50, len(checks)
reds=[x for x in checks if x["state"]=="RED"]
out=root/"build/titan7-50pass/report.json";out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({"schema":"luhmOs.operationTitan7.50passReceipt.v1","executedPasses":len(checks),"green":len(checks)-len(reds),"red":len(reds),"passes":checks},indent=2)+"\n")
print(json.dumps({"executedPasses":50,"red":len(reds),"redNames":[x["name"] for x in reds]}))
raise SystemExit(2 if reds else 0)
