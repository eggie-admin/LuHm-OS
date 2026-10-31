#!/usr/bin/env python3
"""One-procedure helper: bounded, read-only local source spider and human-need routing.

Never execute imported code, clone donor repositories, access the network, or
promote release authority. Use through tools.r1UnifiedFlow --spider.
"""
from __future__ import annotations

import ast
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/sinisterAutonomySpiderV1.json"
HEX = ("0x00","0x02","0x04","0x08","0x10","0x20","0x40","0x80","0x100")
EXT = (".py",".js",".mjs",".html",".css",".json",".webmanifest",".svg",".gd",".ts",".yml",".yaml")
JS_IMPORT = re.compile(r"""(?:\bfrom\s*|\bimport\s*)["'](\.[^"']+)["']""")
WORKFLOW_MODULE = re.compile(r"\bpython3?\s+-m\s+((?:tools|tests)\.[A-Za-z][A-Za-z0-9_.]*)")
WORKFLOW_PATH = re.compile(r"\bpython3?\s+((?:tools|tests)/[A-Za-z0-9_./-]+\.py)")
NODE_PATH = re.compile(r"\bnode\s+--test\s+([A-Za-z0-9_./-]+\.(?:js|mjs))")


def validate(doc):
    errors=[]
    def require(test,code):
        if not test:errors.append(code)
    require(doc.get("schema")=="luhmOs.sinisterAutonomySpider.v1" and
            doc.get("state")=="PROPOSED_SOURCE_ONLY" and doc.get("crown")=="STOP","SCHEMA")
    require(doc.get("authority")=="Professor" and doc.get("entry")=="tools/r1UnifiedFlow.py" and
            doc.get("helper")=="tools/sinisterSpider.py" and
            doc.get("spiderMode")=="LOCAL_SOURCE_ONLY_NO_EXECUTION","ONE_ENTRY")
    roots=doc.get("roots",[])
    require(roots==["tools/r1UnifiedFlow.py","frontEnd/rootlessCockpit/index.html",
                    "frontEnd/prototypes/glassWorld/src/main.js",
                    ".github/workflows/free-first-workspace-daily.yml"],"BOUNDED_ROOTS")
    limits=doc.get("limits",{})
    require(limits=={"maxNodes":160,"maxEdges":512,"maxDepth":3,
                     "maxFileBytes":200000,"maxPathLength":200},"BOUNDED_LIMITS")
    mat=doc.get("matrices",{})
    for key,count,rows,cols in (
        ("twoByTwo",4,2,2),("fourByFour",16,4,4),("eightByEight",64,8,8)):
        v=mat.get(key,{})
        require(v.get("count")==count and len(v.get("rows",[]))==rows and
                len(v.get("columns",[]))==cols and
                len(set(v.get("rows",[])))==rows and len(set(v.get("columns",[])))==cols
                and v.get("status") in ("DECISION_PLAN_NOT_RUNTIME","ROUTING_PLAN_NOT_RUNTIME",
                                        "EVIDENCE_PLAN_NOT_RUNTIME"),"MATRIX_"+key)
    require(mat.get("hexAudits")==list(HEX) and
            mat.get("fullAudit64Executed")==0 and mat.get("physicalDeviceAuditsExecuted")==0,
            "FALSE_DEPTH_PROOF")
    human=doc.get("intervention",{})
    require(human.get("humanNeedIsNotEscalationTier") is True and
            human.get("sourcePolicyCannotGrantRuntimeAuthority") is True and
            human.get("unattendedDraftCandidateWritesAuthorizedByThisHelper") is False and
            human.get("automaticDeescalationOnNewEvidence") is True,"HUMAN_SCOPE")
    require(doc.get("risk")=={"low":0,"medium":1,"high":2,"privileged":3,
                               "minimumConfidenceForAutomation":2},"RISK_MAP")
    existing=doc.get("existing",{})
    require(existing.get("escalation")=="doctrine/escalationKernelV1.json" and
            existing.get("r1")=="doctrine/r1UnifiedFlowV1.json" and
            existing.get("crownReceiptSlots")==336,"CANON_REUSE")
    permissions=doc.get("permissions",{})
    for key in ("autoMerge","autoDeploy","autoSign","autoPublish","autoFirmware",
                "autoKernel","autoGrub","autoNetworkCrawl","autoUnquarantine","autoCallAI"):
        require(permissions.get(key) is False,"AUTHORITY_"+key)
    require(type(permissions.get("autoCostUsd")) is int and permissions.get("autoCostUsd")==0 and
            permissions.get("ownerPromotionRequired") is True,"COST_CROWN")
    release=doc.get("release",{})
    require(release.get("automaticPromotion") is False and
            release.get("beta")=="OWNER_SIGNED_SAMSUNG_REQUIRED" and
            release.get("public")=="OWNER_PUBLICATION_GATES_UNSATISFIED","RELEASE_HOLD")
    return sorted(set(errors))


def route(impact, confidence, *, privileged=False, repeatable=False,
          independent_proof=False):
    """0 means no human action for safe work; risk+uncertainty increase attention.
    Lowering risk or obtaining evidence automatically lowers human need again.
    Never grant a capability, even at zero.
    """
    if type(impact) is not int or impact not in range(4) or type(confidence) is not int or confidence not in range(4):
        raise ValueError("INVALID_AUTONOMY_INPUT")
    if type(privileged) is not bool or type(repeatable) is not bool or type(independent_proof) is not bool:
        raise ValueError("INVALID_AUTONOMY_FLAGS")
    if privileged or impact==3:
        need,decision=3,"OWNER_REQUIRED_PRIVILEGED_BOUNDARY"
    elif impact==2:
        need,decision=(2 if not independent_proof else 1),"DEVICE_OR_RIGHTS_EVIDENCE_REQUIRED"
    elif confidence<2:
        need,decision=1,"FOCUSED_REVIEW_AFTER_MACHINE_RETRY"
    elif impact==1 and repeatable:
        need,decision=0,"DRAFT_FIX_PROPOSAL_ELIGIBLE"
    elif impact==1:
        need,decision=1,"REVIEW_NONREPEATABLE_SOURCE"
    else:
        need,decision=0,"ZERO_TOUCH_READONLY_CLOSE"
    return {
        "humanNeed":need,"humanNeedHex":f"0x{need:02x}",
        "decision":decision,
        "machineMayRunSourceAudit":True,
        "machineMayPrepareDraftFix":decision=="DRAFT_FIX_PROPOSAL_ELIGIBLE",
        "machineMayWriteProtectedMain":False,
        "machineMayDeployOrSign":False,"crown":"STOP"
    }


def _canonical(root,rel,max_length):
    """The exact relative path must stay within root and never pass through symlinks."""
    if (not isinstance(rel,str) or not rel or len(rel)>max_length or
            "\\" in rel or any(ord(char)<32 for char in rel) or rel.startswith("/")):
        raise ValueError("UNSAFE_PATH")
    parts=PurePosixPath(rel).parts
    if any(part in ("..",".") for part in parts) or not parts:
        raise ValueError("UNSAFE_PATH")
    path=root.joinpath(*parts)
    if any(p.is_symlink() for p in [root.joinpath(*parts[:i]) for i in range(1,len(parts)+1)]):
        raise ValueError("SYMLINK_PATH")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("PATH_ESCAPE")
    return path


class _HtmlRefs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="script" and "src" in a:self.refs.append(a["src"])
        if tag=="link" and "href" in a:
            rels=set(a.get("rel","").lower().split())
            if (rels.intersection(("stylesheet","icon","manifest","modulepreload")) or
                ("preload" in rels and a.get("as","").lower() in ("script","style"))):
                self.refs.append(a["href"])


def _resolve_relative(origin,target):
    if not target.startswith(".") or target.startswith("..\\"):
        return None
    # PurePosixPath does not collapse '..'; normalize only when the file remains inside repo.
    parts=list(PurePosixPath(origin).parent.parts)
    for piece in target.replace("\\\\","/").split("/"):
        if piece in ("","."):continue
        if piece=="..":
            if not parts:return None
            parts.pop()
        else:parts.append(piece)
    return "/".join(parts)


def references(path,raw):
    suffix=PurePosixPath(path).suffix.lower()
    if suffix==".py":
        try:tree=ast.parse(raw.decode("utf-8"),filename=path)
        except (SyntaxError,UnicodeDecodeError) as exc:raise ValueError("PARSE_PY:"+path) from exc
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for item in node.names:
                    if item.name.startswith(("tools.","tests.")):
                        yield item.name.replace(".","/")+".py"
            elif isinstance(node,ast.ImportFrom):
                module=node.module or ""
                if node.level==0 and module in ("tools","tests"):
                    # Python permits "from tools import helper" for a module.
                    # Track each explicit module alias, not only dotted imports.
                    for alias in node.names:
                        if alias.name != "*" and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", alias.name):
                            yield module+"/"+alias.name+".py"
                elif node.level==0 and module.startswith(("tools.","tests.")):
                    yield module.replace(".","/")+".py"
                elif node.level and module:
                    base=PurePosixPath(path).parent
                    for i in range(node.level-1):base=base.parent
                    yield str(base.joinpath(*module.split(".")))+".py"
    elif suffix in (".js",".mjs",".ts"):
        content=raw.decode("utf-8")
        for m in JS_IMPORT.finditer(content):
            ref=_resolve_relative(path,m.group(1))
            if ref is not None:yield ref
    elif suffix==".html":
        parser=_HtmlRefs();parser.feed(raw.decode("utf-8"))
        for src in parser.refs:
            url=urlsplit(src)
            if url.scheme or url.netloc:raise ValueError("EXTERNAL_HTML_ASSET:"+path)
            if src.startswith("/"):
                if path=="frontEnd/rootlessCockpit/index.html":
                    yield "frontEnd/rootlessCockpit/"+url.path.lstrip("/")
            else:
                ref=_resolve_relative(path,"./"+url.path)
                if ref is not None:yield ref
    elif suffix in (".yml",".yaml") and path.startswith(".github/workflows/"):
        content=raw.decode("utf-8")
        for module in WORKFLOW_MODULE.findall(content):
            yield module.replace(".","/")+".py"
        for rel in WORKFLOW_PATH.findall(content):yield rel
        for rel in NODE_PATH.findall(content):yield rel


def spider(root,doc,*,roots=None):
    """Reads only local regular files. No filesystem-wide walk or shell/URL operations."""
    errors=validate(doc)
    if errors:return {"status":"RED_POLICY","errors":errors,"nodesVisited":0,
                      "edgesChecked":0,"crown":"STOP"}
    root=Path(root).resolve()
    bounds=doc["limits"]
    queue=[(0,p) for p in (doc["roots"] if roots is None else roots)]
    if len(queue)>bounds["maxNodes"]:return {"status":"RED_SOURCE","errors":["ROOT_BUDGET"],"nodesVisited":0,"edgesChecked":0,"crown":"STOP"}
    seen=set();edges=set();errors=[];size=0;observed=[]
    while queue:
        queue.sort(key=lambda x:(x[0],x[1]))
        depth,rel=queue.pop(0)
        if rel in seen:continue
        if len(seen)>=bounds["maxNodes"]:
            errors.append("NODE_BUDGET_EXCEEDED");break
        try:path=_canonical(root,rel,bounds["maxPathLength"])
        except ValueError as exc:errors.append(str(exc)+":"+rel);continue
        if not path.is_file():
            errors.append("MISSING_LOCAL_SOURCE:"+rel);continue
        if path.stat().st_size>bounds["maxFileBytes"]:
            errors.append("FILE_BUDGET:"+rel);continue
        raw=path.read_bytes();size+=len(raw)
        seen.add(rel);observed.append((rel,hashlib.sha256(raw).hexdigest()))
        if depth>=bounds["maxDepth"]:continue
        try:refs=sorted(set(references(rel,raw)))
        except (UnicodeDecodeError,ValueError) as exc:
            errors.append(str(exc));continue
        for target in refs:
            if target is None:continue
            if len(edges)>=bounds["maxEdges"]:
                errors.append("EDGE_BUDGET_EXCEEDED");break
            edges.add((rel,target))
            if target not in seen:queue.append((depth+1,target))
        if "EDGE_BUDGET_EXCEEDED" in errors:break
    digest=hashlib.sha256(json.dumps({"nodes":sorted(observed),"edges":sorted(edges)},
       separators=(",",":"),ensure_ascii=True).encode("utf-8")).hexdigest()
    return {
      "schema":"luhmOs.sinisterSpiderReceipt.v1",
      "status":"PASS_LOCAL_SOURCE_ONLY" if not errors else "RED_SOURCE",
      "errors":sorted(set(errors)),"nodesVisited":len(seen),"edgesChecked":len(edges),
      "bytesRead":size,"maxDepth":bounds["maxDepth"],
      "digestSha256":digest,
      "matrix2x2Planned":4,"matrix4x4Planned":16,"matrix8x8Planned":64,
      "matrixEvidenceCellsExecuted":0,
      "sourceGraphNodesActuallyRead":len(seen),
      "networkRequests":0,"codeImportsExecuted":0,"protectedFilesChanged":0,
      "ownerApproval":False,"crown":"STOP"
    }
