#!/usr/bin/env python3
"""Four cumulative 512-case checkpoints around the existing HEX64 source model.

Source-only policy decisions, not 2048 independent host or runtime tests.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

try:
    from tools import hex64Insanus2048Audit as core
except ImportError:
    import hex64Insanus2048Audit as core

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "doctrine/crownCathedral512EscalationV1.json"
SHA = re.compile(r"^[0-9a-f]{40}$")
TARGETS = (512, 1024, 1536, 2048)
SOURCES = (
    "doctrine/crownCathedral512EscalationV1.json",
    "tools/hex64Insanus2048Audit.py",
    "doctrine/currentSourceTruthV3.json",
    "doctrine/everlastingCovenantV1.json",
    "doctrine/escalationKernelV1.json",
    "doctrine/companyWideOperationalQuarantineV1.json",
    "doctrine/crownCathedralWebglCastV1.json",
)


def validate_manifest(doc):
    if not isinstance(doc, dict) or doc.get("schema") != "luhmOs.crownCathedral512Escalation.v1":
        raise ValueError("invalid schema")
    if doc.get("status") != "PROPOSED_SOURCE_ONLY" or doc.get("crownStatus") != "STOP" or doc.get("promotion") is not False:
        raise ValueError("invalid promotion boundary")
    if doc.get("authority") != "Professor" or doc.get("boss") != "lum":
        raise ValueError("authority drift")
    if doc.get("taskId") != "crownCathedral512Escalation20261104" or doc.get("scopeId") != "hex64ScenarioCumulativeMilestones":
        raise ValueError("source task identity drift")
    if doc.get("sourceLaw") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        raise ValueError("source law drift")
    parent = doc.get("parent", {})
    if parent.get("repository") != "eggie-admin/LuHm-OS" or parent.get("pr") != 512 or parent.get("engine") != "tools/hex64Insanus2048Audit.py" or not SHA.fullmatch(str(parent.get("baseHead", ""))):
        raise ValueError("parent source drift")
    if doc.get("checkpointSize") != 512 or doc.get("scenarioTotal") != 2048 or doc.get("recordBytes") != 64:
        raise ValueError("checkpoint geometry drift")
    if any(doc.get(k) is not True for k in ("cumulativeReverification", "stopAtFirstFailedChunk", "sourceDriftResets", "exactSourceRequired", "noAuthorityEscalation")):
        raise ValueError("unsafe escalation doctrine")
    if doc.get("hardAuditBindings") != ["tools/hardSystemAudit200.py", "tools/machineCanonFourLoop.py", "tools/premonitionTitan500Audit.py", "tools/agentSystemDeploymentAudit.py"]:
        raise ValueError("hard audit references drift")
    if doc.get("denied") != ["providerApiCalls", "providerSpending", "productionSqlWrites", "hostRootChanges", "cloudflareChanges", "agentUnquarantine", "productionDeploy", "sourceMerge", "publicPublication", "releaseSigning", "selfCrown"]:
        raise ValueError("missing forbidden authority")
    chunks=doc.get("checkpoints")
    if not isinstance(chunks, list) or len(chunks)!=4:
        raise ValueError("missing four chunks")
    for i, chunk in enumerate(chunks):
        if chunk != {"target":TARGETS[i],"start":i*512,"endExclusive":TARGETS[i],"families":list(core.STAGES[i*4:i*4+4])}:
            raise ValueError("chunk identity/order drift")
    return chunks


def fingerprints(root=ROOT):
    result={}
    for rel in SOURCES:
        path=root / rel
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing or aliased Canon file")
        result[rel]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def valid_case(index, item, source_ref):
    row,raw=item
    stage,case=divmod(index,128)
    evidence=case & 7
    tier=(case>>3) & 3
    authority=(case>>5) & 3
    if not isinstance(row,dict) or not isinstance(raw,bytes) or len(raw)!=64:
        return False
    if row.get("id")!=f"0x{index:03X}" or row.get("stage")!=core.STAGES[stage] or row.get("tier")!=tier:
        return False
    if row.get("evidence")!=core.EVIDENCE[evidence] or row.get("authority")!=core.AUTHORITY[authority] or row.get("pass") is not True:
        return False
    expected=core.expected_decision(stage,evidence,authority)
    if row.get("decision")!=expected:
        return False
    try:
        magic,version,st,emitted_tier,decision,cid,flags,seq,passed,digest,reserved=core.RECORD.unpack(raw)
    except (ValueError,TypeError):
        return False
    calculated=hashlib.sha256(json.dumps({"sourceRef":source_ref,**row},sort_keys=True,separators=(",",":")).encode("utf-8")).digest()
    return (magic==b"LH64" and version==1 and st==stage and emitted_tier==tier and decision==core.DECISIONS[expected]
            and cid==case and flags==(evidence | (authority<<3)) and seq==index and passed==1
            and digest==calculated and reserved==bytes(12))


def audit(manifest, source_ref, actual_head, target, cases, anchors, digests):
    chunks=validate_manifest(manifest)
    if not isinstance(source_ref,str) or not SHA.fullmatch(source_ref) or actual_head!=source_ref:
        raise ValueError("exact checkout/source mismatch")
    if type(target) is not int or target not in TARGETS:
        raise ValueError("target not a 512-case checkpoint")
    if not isinstance(cases,list) or len(cases)!=2048:
        raise ValueError("incomplete scenario generation")
    if not isinstance(anchors,dict) or set(anchors)!=set(core.source_requirements(ROOT)):
        raise ValueError("source anchor inventory drift")
    if set(digests)!=set(SOURCES) or not all(isinstance(x,str) and re.fullmatch(r"[0-9a-f]{64}",x) for x in digests.values()):
        raise ValueError("invalid source digests")
    chain=bytes(32)
    completed=[]
    for chunk in chunks[:target//512]:
        start,end=chunk["start"],chunk["endExclusive"]
        entries=cases[start:end]
        invalid=[i for i,item in enumerate(entries,start) if not valid_case(i,item,source_ref)]
        binary=b"".join(raw for _,raw in entries if isinstance(raw,bytes))
        digest=hashlib.sha256(binary).digest()
        chain=hashlib.sha256(chain+digest+source_ref.encode("ascii")).digest()
        passed=len(entries)-len(invalid)
        ok=passed==512 and len(binary)==32768
        completed.append({
            "target":chunk["target"],"start":start,"endExclusive":end,
            "families":chunk["families"],"checked":len(entries),
            "passed":passed,"binaryBytes":len(binary),"sha256":digest.hex(),
            "cumulativeChainSha256":chain.hex(),"firstFailed":f"0x{invalid[0]:03X}" if invalid else None,
            "status":"SOURCE_MODEL_PASS" if ok else "RED_MODEL"
        })
        if not ok:
            break
    anchors_pass=all(v is True for v in anchors.values())
    accepted=(len(completed)==target//512 and all(c["status"]=="SOURCE_MODEL_PASS" for c in completed) and anchors_pass)
    return {
        "schema":"luhmOs.crownCathedral512EscalationReceipt.v1",
        "taskId":manifest["taskId"],"scopeId":manifest["scopeId"],
        "sourceRef":source_ref,"milestoneTarget":target,
        "checked":sum(c["checked"] for c in completed),
        "passed":sum(c["passed"] for c in completed),
        "remaining":2048-sum(c["checked"] for c in completed),
        "checkpoints":completed,"sourceAnchors":anchors,
        "sourceSha256":digests,"chainSha256":chain.hex(),
        "verdict":"AMBER_SOURCE_ONLY" if accepted else "RED_SOURCE_GATE",
        "sourceModelOnly":True,"cloudflareBuildProven":False,"googleEntitlementProven":False,
        "physicalDeviceProven":False,"artRightsProven":False,"runtimeGreen":False,
        "merged":False,"deployed":False,"paidCalls":False,"agentsReleased":False,
        "crownStatus":"STOP",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-ref",required=True)
    p.add_argument("--target",type=int,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True,timeout=8).strip()
        m=json.loads(MANIFEST.read_text())
        report=audit(m,args.source_ref,actual,args.target,list(core.matrix(args.source_ref)),
                     core.source_requirements(ROOT),fingerprints())
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError,json.JSONDecodeError) as err:
        report={"schema":"luhmOs.crownCathedral512EscalationReceipt.v1",
                "verdict":"RED_INVALID_SOURCE_OR_CONTRACT","failure":type(err).__name__,
                "runtimeGreen":False,"crownStatus":"STOP"}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:report.get(k) for k in ("sourceRef","milestoneTarget","checked","passed","remaining","verdict","crownStatus")}))
    return 0 if report["verdict"]=="AMBER_SOURCE_ONLY" else 2


if __name__=="__main__":
    raise SystemExit(main())
