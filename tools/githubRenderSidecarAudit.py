#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
errors=[]
def need(ok,msg):
    if not ok: errors.append(msg)
side=json.loads((root/"doctrine/githubRenderSidecarV1.json").read_text())
api=json.loads((root/"doctrine/apiSpineV1.json").read_text())
truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text())
render=(root/"render.yaml").read_text()
server=(root/"host/mcp/luhmMcpServer.py").read_text()
lum=(root/"agents/lum/SKILL.md").read_text()
need(side.get("status")=="CANONICAL_LAW","sidecar canon status drift")
need(side.get("professorApproval") is True,"Professor approval missing")
need("ci" in side.get("githubPrimary",{}).get("owns",[]),"GitHub CI ownership missing")
need(side.get("renderSidecar",{}).get("autoDeployCanonical") is False,"Render auto-deploy must stay off")
free=side.get("strictFreeTier",{})
need(free.get("required") is True,"strict free tier not required")
for key in ("paidPlanUpgrade","paidManagedDatabase","paidKeyValue","paidCron","paidBackgroundWorker","paidPersistentDisk","createAdditionalRenderServicesByDefault"):
    need(free.get(key) is False,f"paid/free-tier drift: {key}")
need(api.get("renderSidecar",{}).get("sourceAndCiAuthority")=="github","API spine lost GitHub authority")
need(api.get("renderSidecar",{}).get("entitlementLane")=="STRICT_FREE_TIER","API spine cost lane drift")
layer=truth.get("renderSidecarLayer",{})
need(layer.get("contract")=="doctrine/githubRenderSidecarV1.json","source truth pointer missing")
need(layer.get("githubRole")=="compatibilitySourceCiAndReceiptSpine","source truth GitHub role drift")
for phrase in ("plan: free","autoDeployTrigger: off","LUHM_RENDER_ROLE","strict-free-tier","LUHM_GITHUB_PRIMARY","github-green-only"):
    need(phrase in render,f"render.yaml missing {phrase}")
need('"renderSidecar": spine.get("renderSidecar", {})' in server,"MCP API spine does not expose sidecar")
need('"role": os.environ.get("LUHM_RENDER_ROLE"' in server,"health sidecar role missing")
need("## GitHub primary / Render sidecar canon" in lum,"Lum sidecar practice missing")
print(json.dumps({
  "schema":"luhmOs.githubRenderSidecarAudit.v1",
  "status":"GREEN_GITHUB_RENDER_SIDECAR_CANON" if not errors else "RED_GITHUB_RENDER_SIDECAR_CANON",
  "scope":"source contract only",
  "liveRenderPlanProof":False,
  "liveDeploymentProof":False,
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)
