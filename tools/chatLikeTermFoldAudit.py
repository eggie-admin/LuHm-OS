#!/usr/bin/env python3
import json, pathlib, subprocess, sys, tempfile
root=pathlib.Path(__file__).resolve().parents[1]
errors=[]
contract=json.loads((root/"doctrine/chatLikeTermFoldV1.json").read_text())
progress=json.loads((root/"doctrine/chatProgressStreamV1.json").read_text())
economy=json.loads((root/"doctrine/providerEconomyV1.json").read_text())
canon=json.loads((root/"doctrine/projectChatCanonV1.json").read_text())

def need(ok,msg):
    if not ok: errors.append(msg)

need(contract.get("executionLaw",{}).get("collectionEndpointBeforeItemEndpoint") is True,"collection-first missing")
need(contract.get("executionLaw",{}).get("providerFanoutPerItem") is False,"provider per-item fanout must be false")
need(contract.get("executionLaw",{}).get("oneProviderEscalationPerSemanticClass") is True,"provider class budget drift")
need(contract.get("progressPresentation",{}).get("individualItemProgressByDefault") is False,"per-item progress must default off")
need(contract.get("progressPresentation",{}).get("oneVisibleLinePerSemanticClass") is True,"group progress missing")
need(contract.get("authorityBoundary",{}).get("foldingChangesAuthority") is False,"folding cannot change authority")
need(progress.get("aggregation",{}).get("contract")=="doctrine/chatLikeTermFoldV1.json","progress stream not bound")
need(economy.get("likeTermEconomy",{}).get("groupBeforeProviderRoute") is True,"provider economy grouping missing")
need(economy.get("likeTermEconomy",{}).get("perTargetProviderFanout") is False,"provider fanout drift")
need(canon.get("chatRuntime",{}).get("likeTermFold")=="doctrine/chatLikeTermFoldV1.json","chat canon not bound")

sample={
 "operations":[
  {"sourceRef":"abc","scopeId":"prs","operationFamily":"compareBranchAgainstMain","repository":"eggie-admin/LuHm-OS","baseRef":"main","toolClass":"githubCompare","proofKind":"ancestry","authorityClass":"READ_ONLY","targetId":"pr1"},
  {"sourceRef":"abc","scopeId":"prs","operationFamily":"compareBranchAgainstMain","repository":"eggie-admin/LuHm-OS","baseRef":"main","toolClass":"githubCompare","proofKind":"ancestry","authorityClass":"READ_ONLY","targetId":"pr2"},
  {"sourceRef":"abc","scopeId":"prs","operationFamily":"compareBranchAgainstMain","repository":"eggie-admin/LuHm-OS","baseRef":"main","toolClass":"githubCompare","proofKind":"ancestry","authorityClass":"READ_ONLY","targetId":"pr2"}
 ]}
with tempfile.NamedTemporaryFile("w",suffix=".json",delete=False) as f:
    json.dump(sample,f); name=f.name
run=subprocess.run([sys.executable,str(root/"tools/chatLikeTermFold.py"),name],capture_output=True,text=True)
need(run.returncode==0,"batcher failed")
if run.returncode==0:
    out=json.loads(run.stdout)
    need(out.get("inputCount")==3,"input count wrong")
    need(out.get("dedupedCount")==2,"exact dedupe failed")
    need(out.get("semanticClassCount")==1,"like terms failed to fold")
    need(out.get("groups",[{}])[0].get("memberCount")==2,"group member count wrong")
if errors:
    print(json.dumps({"status":"RED_CHAT_LIKE_TERM_FOLD","errors":errors},indent=2))
    raise SystemExit(1)
print(json.dumps({"status":"GREEN_CHAT_LIKE_TERM_FOLD_SOURCE_CANDIDATE","semanticGrouping":True,"providerFanoutPerItem":False,"individualProgressDefault":False,"crownStatus":"STOP"},indent=2))
