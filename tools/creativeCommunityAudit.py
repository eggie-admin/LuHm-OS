#!/usr/bin/env python3
"""LuHm original RPG community research: offline RSS/Atom and rights admission.

No network, Git clone, Nexus API call, emulator, Live2D model import, Daz add-on
execution, browser, subprocess or file writes. Parses explicitly provided bytes.
"""
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"doctrine/creativeModuleForge4x4V1.json"
QUARANTINE=ROOT/"doctrine/companyWideOperationalQuarantineV1.json"
LANES=("rulesRoleplay","worldModules","artAvatars","communitySignals")
PHASES=("R1","R2","R3","R4")
SHA40=re.compile(r"[0-9a-f]{40}\Z")
IDENT=re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
MAX_FEED=65536


def _read(path:Path)->dict[str,Any]:
    obj=json.loads(path.read_text(encoding="utf8"))
    if not isinstance(obj,dict):
        raise ValueError("RED_CREATIVE_JSON")
    return obj


def audit()->dict[str,Any]:
    data=_read(CONTRACT)
    issues=[]
    if data.get("schema")!="luhmOs.creativeModuleForge4x4.v1" or data.get("repo")!="eggie-admin/LuHm-OS":
        issues.append("RED_CREATIVE_CANON")
    if [x.get("id") for x in data.get("lanes",[])]!=list(LANES):
        issues.append("RED_CREATIVE_LANES")
    if [x.get("id") for x in data.get("phases",[])]!=list(PHASES):
        issues.append("RED_CREATIVE_PHASES")
    cells=data.get("matrix4x4",[])
    if len(cells)!=4:
        issues.append("RED_CREATIVE_MATRIX")
    else:
        for i,row in enumerate(cells):
            if row.get("lane")!=LANES[i] or len(row.get("cells",[]))!=4:
                issues.append("RED_CREATIVE_MATRIX")
                continue
            for j,cell in enumerate(row["cells"]):
                if (cell.get("cell")!=LANES[i]+"."+PHASES[j]
                    or any(cell.get(k) is not False for k in
                        ("rightsApproved","liveRuntimeVerified","releaseAuthorized"))):
                    issues.append("RED_CREATIVE_FAKE_EVIDENCE")
    roots=data.get("roots",[])
    if not isinstance(roots,list) or len(roots)!=10 or any(
        type(p) is not str or Path(p).is_absolute() or ".." in Path(p).parts
        or not (ROOT/p).is_file() or not (ROOT/p).resolve().is_relative_to(ROOT.resolve())
        for p in roots):
        issues.append("RED_CREATIVE_ROOTS")
    language=data.get("scriptLanguage",{})
    if (language.get("representation")!="JSON_ONLY_NO_EVAL"
        or language.get("commands")!=["say","check","grant","goto"]
        or language.get("noUntrustedCode") is not True
        or language.get("noNetworkOps") is not True):
        issues.append("RED_CREATIVE_DSL_AUTHORITY")
    rss=data.get("rss",{})
    if (rss.get("maxBytes")!=MAX_FEED or rss.get("maxEntries")!=32
        or rss.get("secureNoDtd") is not True
        or rss.get("secureNoEntity") is not True
        or rss.get("secureNoNetwork") is not True
        or rss.get("manualUserProvidedXmlOnly") is not True):
        issues.append("RED_CREATIVE_RSS")
    mods=data.get("mods",{})
    if any(mods.get(k) is not True for k in
        ("noBundledBiosRomOrGameAsset",)):
        issues.append("RED_CREATIVE_MOD_LAW")
    if (data.get("avatars",{}).get("autoConvertLive2dTo3d") is not False
        or data.get("licensing",{}).get("rootActual")!="GPL-3.0"
        or data.get("licensing",{}).get("noBlanketApacheRelicense") is not True):
        issues.append("RED_CREATIVE_RIGHTS")
    refs=data.get("communityReferences",[])
    if len(refs)!=9 or any(
        not x.get("url","").startswith("https://") or x.get("noImport") is not True
        for x in refs):
        issues.append("RED_CREATIVE_UPSTREAM")
    automation=data.get("automation",{})
    for key in ("ingestNetwork","rssPolling","githubAutoFork","nexusApiCalls",
                "emulatorLaunch","thirdPartyPluginExecution","sqlWrites",
                "gamePublicRelease"):
        if automation.get(key) is not False:
            issues.append("RED_CREATIVE_UNAPPROVED_AUTOMATION")
            break
    q=_read(QUARANTINE)
    if (q.get("state")!="QUARANTINED" or
        q.get("activeTaskWorkersAllowed") is not False
        or data.get("crownStatus")!="STOP"):
        issues.append("RED_CREATIVE_QUARANTINE")
    return {
      "schema":"luhmOs.creativeModuleForgeAudit.v1",
      "state":"SOURCE_CANDIDATE_ONLY" if not issues else "RED_SOURCE_DRIFT",
      "issues":sorted(set(issues)),"cells":16,"referenceSources":len(refs),
      "liveWorkers":0,"rssNetworkRequests":0,"nexusRequests":0,
      "githubForks":0,"romsProcessed":0,"live2dConversions":0,
      "productionGame":False,"greenAuthority":False,"crownAuthority":False,
    }


def _safe_url(value:str)->str:
    if type(value) is not str or not 8<len(value)<=400 or any(
        ord(c)<32 for c in value):
        raise ValueError("RED_FEED_URL")
    p=urlsplit(value)
    if (p.scheme!="https" or not p.hostname or p.username or p.password
        or p.port not in (None,443)
        or p.hostname.lower()=="localhost" or p.hostname.endswith(".local")
        or p.hostname.startswith("127.") or p.hostname.startswith("10.")
        or p.hostname.startswith("192.168.") or p.hostname.startswith("169.254.")
        or p.hostname.startswith("[") or p.hostname.isdigit()):
        raise ValueError("RED_FEED_URL")
    return value


def parse_feed(xml_bytes:bytes)->dict[str,Any]:
    """Strict bounded user-provided RSS 2/Atom XML; never dereferences links."""
    if type(xml_bytes) is not bytes or not 10<=len(xml_bytes)<=MAX_FEED:
        raise ValueError("RED_FEED_SIZE")
    lower=xml_bytes.lower()
    if (b"<!doctype" in lower or b"<!entity" in lower
        or b"<![" in lower or b"<?xml-stylesheet" in lower
        or b"<!--" in lower):
        raise ValueError("RED_FEED_DTD_OR_ACTIVE_MARKUP")
    try:
        root=ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError("RED_FEED_PARSE") from exc
    if root.tag=="rss":
        items=root.findall("./channel/item")
        title=lambda x:x.findtext("title")
        link=lambda x:x.findtext("link")
        kind="rss2"
    elif root.tag=="{http://www.w3.org/2005/Atom}feed":
        ns="{http://www.w3.org/2005/Atom}"
        items=root.findall(ns+"entry")
        title=lambda x:x.findtext(ns+"title")
        link=lambda x:next(
            (a.attrib.get("href") for a in x.findall(ns+"link")
             if a.attrib.get("rel","alternate")=="alternate"),None)
        kind="atom"
    else:
        raise ValueError("RED_FEED_TYPE")
    if len(items)>32:
        raise ValueError("RED_FEED_TOO_MANY_ITEMS")
    entries=[]
    for i,item in enumerate(items):
        t=title(item)
        url=link(item)
        if (type(t) is not str or not 1<=len(t.strip())<=160
            or any(ord(ch)<32 and ch not in "\n\t" for ch in t)):
            raise ValueError("RED_FEED_TITLE")
        normalized_url=_safe_url(url)
        entries.append({
           "index":i,"title":t.strip(),
           "link":normalized_url,
           "recordDigest":hashlib.sha256(
              (t.strip()+"\x00"+normalized_url).encode("utf8")).hexdigest(),
           "contentDownloaded":False,"rightsVerified":False,
        })
    return {"schema":"luhmOs.offlineFeedReceipt.v1","format":kind,
        "feedDigest":hashlib.sha256(xml_bytes).hexdigest(),
        "entries":entries,"networkRequests":0,
        "publisherIdentityVerified":False,"downloadAuthorized":False,
        "publicationAuthorized":False}


def candidate(*,task_id:str,source_ref:str,scope_id:str,
              reference_id:str,asset_license:str)->dict[str,Any]:
    if any(type(x) is not str or IDENT.fullmatch(x) is None
           for x in (task_id,scope_id)):
        raise ValueError("RED_COMMUNITY_SCOPE")
    if type(source_ref) is not str or SHA40.fullmatch(source_ref) is None:
        raise ValueError("RED_COMMUNITY_SOURCE")
    registered={x["id"]:x for x in _read(CONTRACT)["communityReferences"]}
    if type(reference_id) is not str or reference_id not in registered:
        raise ValueError("RED_COMMUNITY_REFERENCE")
    if type(asset_license) is not str or not 1<=len(asset_license)<=60 or not re.fullmatch(
        r"[A-Za-z0-9+._-]+",asset_license):
        raise ValueError("RED_COMMUNITY_LICENSE_CLAIM")
    obj=registered[reference_id]
    return {
      "taskId":task_id,"sourceRef":source_ref,"scopeId":scope_id,
      "referenceId":reference_id,"url":obj["url"],
      "claimedLicense":asset_license,"upstreamLicenseHint":obj["license"],
      "status":"HOLD_PER_FILE_RIGHTS_AND_CURRENT_RELEASE_PROOF",
      "permissionVerified":False,"binaryImported":False,
      "pluginInstalled":False,"gitForkCreated":False,"agentStarted":False,
      "possibleManualSourceReview":True,"greenAuthority":False,
    }


def avatar_retarget_plan(*,source_format:str,target_format:str,rights:str)->dict[str,Any]:
    if (source_format not in ("PSD_LAYERS","ORIGINAL_SVG","OWNED_DAZ_REFERENCE")
        or target_format not in ("BLENDER_RIG_PLAN","GODOT_GLTF_PLAN")
        or rights not in ("homebrewOwned","licensedForTransform")):
        raise ValueError("RED_AVATAR_RIGHTS_OR_FORMAT")
    return {
      "sourceFormat":source_format,"targetFormat":target_format,
      "state":"HOLD_MANUAL_RIG_MAPPING_AND_LICENSE_REVIEW",
      "sourceRepresentation":"2D_LAYERED" if source_format!="OWNED_DAZ_REFERENCE" else "EXTERNAL_3D_REFERENCE",
      "auto3dMeshGenerated":False,"live2dCoreLoaded":False,
      "blenderExecuted":False,"commercialRedistributionGranted":False,
      "commandTemplate":"blender --background <owned.blend> --python <reviewed_export.py>",
      "commandExecuted":False,"greenAuthority":False,
    }


if __name__=="__main__":
    print(json.dumps(audit(),indent=2))
