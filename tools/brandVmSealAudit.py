#!/usr/bin/env python3
"""LuHm-OS source-only brand/vector/hex/VM seal.

P3 bitmap to vectorized pixel-run rectangles only, not semantic/smooth contour
tracing. No files from user, external XML/CSS, kernel access, network, VM boot,
firmware flashing, source promotion or plugin deployment.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"doctrine/brandVmArchitectureSealV1.json"
BRAND=ROOT/"doctrine/organizationBrandRegistryV1.json"
QUARANTINE=ROOT/"doctrine/companyWideOperationalQuarantineV1.json"
HEX_POLICY=ROOT/"doctrine/machineFourArchitectureForgeV1.json"
VEC=ROOT/"publicationSite/brandSealCandidate.svg"
PREVIEW=ROOT/"publicationSite/vmBootPreview.html"
AXES=("hexCodec","bitmapToVector","brandIdentity","vmCockpit")
GATES=("sourceIdentity","adversarialValidation","hostProof","ownerRelease")
COLORS=("#17131f","#9f7aea","#7ce8ec","#f7f4ff","#ff8aca","#2c213d")
HEX_WIDTHS={"usbVendorId":4,"pciVendorId":4,"cpuidLeaf":8,"ipsOffset":6,
            "uefiGuid":32,"sourceRef":40,"artifactSha256":64}
HEX=re.compile(r"[0-9a-f]+\Z")
SAFE_XML_TAGS={"svg","title","desc","defs","linearGradient","radialGradient",
               "stop","rect","path","circle","g","text","line"}
SAFE_XML_ATTRIBUTES={"viewBox","role","aria-labelledby","id","width","height","rx",
                     "fill","stroke","stroke-width","stroke-linecap","cx","cy","r",
                     "x1","x2","y1","y2","x","y","d","opacity","font-family",
                     "font-size","font-weight","letter-spacing","offset","stop-color",
                     "stop-opacity","transform"}
SVGNS="{http://www.w3.org/2000/svg}"


def _json(path:Path)->dict[str,Any]:
    data=json.loads(path.read_text(encoding="utf8"))
    if type(data) is not dict:
        raise ValueError("RED_SEAL_JSON_SHAPE")
    return data


def fixed_hex(kind:Any,value:Any)->dict[str,Any]:
    """Numeric input is normalized in a single registered bus/identity domain."""
    if type(kind) is not str or kind not in HEX_WIDTHS:
        raise ValueError("RED_SEAL_HEX_KIND")
    digits=HEX_WIDTHS[kind]
    if type(value) is int:
        if kind in ("sourceRef","artifactSha256") or not 0<=value<16**digits:
            raise ValueError("RED_SEAL_HEX_INTEGER")
        numeric=value
    elif type(value) is str and bool(value) and len(value)<=digits and HEX.fullmatch(value):
        if kind in ("sourceRef","artifactSha256") and len(value)!=digits:
            raise ValueError("RED_SEAL_HEX_DIGEST_WIDTH")
        numeric=int(value,16)
    else:
        raise ValueError("RED_SEAL_HEX_SHAPE")
    h=f"{numeric:0{digits}x}"
    return {"namespace":kind,"hex":h,"sortKey":kind+":"+h,"bits":digits*4,
            "deviceIdentityVerified":False,"securityAuthority":False}


def _flat_p3_ppm(raw:bytes)->tuple[int,int,list[int]]:
    """Plain P3 ASCII, max 16x16, six exact RGB brand colors, no comments."""
    if type(raw) is not bytes or len(raw)>8192 or len(raw)<16:
        raise ValueError("RED_BITMAP_SIZE")
    try:
        s=raw.decode("ascii")
    except UnicodeError as exc:
        raise ValueError("RED_BITMAP_ASCII") from exc
    if not re.fullmatch(r"[A-Za-z0-9\s]+",s) or "#" in s:
        raise ValueError("RED_BITMAP_TOKENS")
    tokens=s.split()
    if len(tokens)<4 or tokens[0]!="P3":
        raise ValueError("RED_BITMAP_FORMAT")
    try:
        w,h,maxchannel=[int(t) for t in tokens[1:4]]
    except (TypeError,ValueError) as exc:
        raise ValueError("RED_BITMAP_DIMENSIONS") from exc
    if not 1<=w<=16 or not 1<=h<=16 or maxchannel!=255 or len(tokens)!=4+w*h*3:
        raise ValueError("RED_BITMAP_DIMENSIONS")
    if any(not t.isdigit() or len(t)>3 for t in tokens[4:]):
        raise ValueError("RED_BITMAP_CHANNEL")
    rgb=[int(t) for t in tokens[4:]]
    if any(not 0<=v<=255 for v in rgb):
        raise ValueError("RED_BITMAP_RANGE")
    palette={tuple(bytes.fromhex(c[1:])):i for i,c in enumerate(COLORS)}
    try:
        indexed=[palette[tuple(rgb[i:i+3])] for i in range(0,len(rgb),3)]
    except KeyError as exc:
        raise ValueError("RED_BITMAP_UNREGISTERED_COLOR") from exc
    return w,h,indexed


def bitmap_to_vector(raw:bytes,*,rights:str="originalOwned")->dict[str,Any]:
    if type(rights) is not str or rights!="originalOwned":
        raise ValueError("RED_BITMAP_RIGHTS")
    w,h,indices=_flat_p3_ppm(raw)
    rectangles=[]
    for row in range(h):
        x=0
        while x<w:
            col=indices[row*w+x]
            run=1
            while x+run<w and indices[row*w+x+run]==col:
                run+=1
            rectangles.append((x,row,run,COLORS[col]))
            x+=run
    parts=[
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+str(w)+' '+str(h)+'" role="img" aria-label="Original indexed bitmap vector pixel runs">'
    ]
    for x,y,run,color in rectangles:
        parts.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{color}"/>')
    parts.append("</svg>")
    svg="".join(parts)
    ET.fromstring(svg)
    return {"schema":"luhmOs.bitmapToVectorCandidate.v1","width":w,"height":h,
            "pixelCount":w*h,"rectangleCount":len(rectangles),
            "originalBitmapSha256":hashlib.sha256(raw).hexdigest(),
            "vectorSha256":hashlib.sha256(svg.encode()).hexdigest(),
            "svg":svg,"representation":"PIXEL_EXACT_RECTANGLE_RUNS_NOT_SMOOTH_TRACE",
            "bitmapOriginalPreservedByCaller":True,"rightsClaimVerified":False,
            "outputPublicApproved":False,"externalFilesRead":False,
            "networkUsed":False}


def _check_svg(path:Path)->bool:
    text=path.read_text(encoding="utf8")
    if len(text)>16000 or "<!DOCTYPE" in text or "<!ENTITY" in text:
        return False
    try:
        root=ET.fromstring(text)
    except ET.ParseError:
        return False
    if root.tag!=SVGNS+"svg":
        return False
    for node in root.iter():
        if node.tag.removeprefix(SVGNS) not in SAFE_XML_TAGS:
            return False
        for key,value in node.attrib.items():
            if key not in SAFE_XML_ATTRIBUTES:
                return False
            if ("url(" in value.lower() and not re.fullmatch(r"url\(#[A-Za-z][A-Za-z0-9]*\)",value)
                or "javascript:" in value.lower() or "<" in value):
                return False
    return True


def audit()->dict[str,Any]:
    p=_json(POLICY);brand=_json(BRAND);q=_json(QUARANTINE)
    err=[]
    if p.get("schema")!="luhmOs.brandVmArchitectureSeal.v1" or p.get("repo")!="eggie-admin/LuHm-OS":
        err.append("RED_SEAL_SCHEMA")
    rows=p.get("matrix4x4",[])
    if len(rows)!=4 or [x.get("axis") for x in rows]!=list(AXES) or p.get("gates")!=list(GATES):
        err.append("RED_SEAL_4X4")
    else:
        for i,row in enumerate(rows):
            if len(row.get("cells",[]))!=4:
                err.append("RED_SEAL_MATRIX")
                continue
            for j,cell in enumerate(row["cells"]):
                if (cell.get("id")!=AXES[i]+"."+GATES[j] or
                    any(cell.get(k) is not False for k in
                        ("executed","hostVerified","productionAuthorized"))):
                    err.append("RED_SEAL_IMPLIED_GREEN")
    anchors=p.get("canon",[])
    if (len(anchors)!=10 or any(type(v) is not str or Path(v).is_absolute()
       or ".." in Path(v).parts or not (ROOT/v).is_file()
       for v in anchors)):
        err.append("RED_SEAL_ANCHOR")
    if (p.get("visual",{}).get("existingLogo")!="publicationSite/logo.svg"
        or p.get("visual",{}).get("candidateSeal")!="publicationSite/brandSealCandidate.svg"
        or brand["publicBrands"]["luhmOs"]["displayName"]!="LuHm-OS"
        or p.get("visual",{}).get("approval") is not False):
        err.append("RED_SEAL_BRAND")
    if not VEC.is_file() or not _check_svg(VEC):
        err.append("RED_SEAL_VECTOR_SECURITY")
    if not PREVIEW.is_file():
        err.append("RED_SEAL_PREVIEW_MISSING")
    elif "SIMULATED BOOT" not in PREVIEW.read_text(encoding="utf8"):
        err.append("RED_SEAL_FAKE_VM")
    widths=_json(HEX_POLICY)["sort"]["fixedHexNormalization"]
    if any(widths.get(k,{}).get("digits")!=v for k,v in HEX_WIDTHS.items()):
        err.append("RED_SEAL_HEX_DRIFT")
    host=p.get("host",{});release=p.get("release",{})
    for k in ("runtimeVMProven","gameRuntimeInChatProven","androidTouchAccepted",
              "mayStartVirtualMachine","autoLoadRemoteGame"):
        if host.get(k) is not False:
            err.append("RED_SEAL_HOST_CLAIM")
    if (host.get("remoteSourceMatchesDraft") is not False or
        host.get("remoteServiceType")!="RenderWebServiceNotHypervisor"):
        err.append("RED_SEAL_VM_IDENTITY")
    if (any(release.get(k) is not True for k in
            ("noAutoMerge","noAutoDeploy","noVmProvision","noPaidCompute",
             "companyAgentQuarantinePreserved"))
        or release.get("productionKernelAccepted") is not False
        or p.get("crownStatus")!="STOP"):
        err.append("RED_SEAL_RELEASE")
    if q.get("state")!="QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False:
        err.append("RED_SEAL_QUARANTINE")
    return {"schema":"luhmOs.brandVmArchitectureSourceAudit.v1",
        "status":"SOURCE_SEALED_CANDIDATE_ONLY" if not err else "RED_SOURCE_DRIFT",
        "issues":sorted(set(err)),"cells":16,"hexNamespaces":len(HEX_WIDTHS),
        "brandVectorSafe":VEC.is_file() and _check_svg(VEC),
        "existingLogoPreserved":True,"vmBooted":False,
        "historicalGodotWebServiceReportedLive":True,
        "historicalWebServiceEqualsVM":False,
        "installedPluginUpdatedToThisSource":False,
        "agentWorkersActive":0,"sourceProductionGreen":False,
        "crownAuthority":False}


if __name__=="__main__":
    print(json.dumps(audit(),indent=2))
