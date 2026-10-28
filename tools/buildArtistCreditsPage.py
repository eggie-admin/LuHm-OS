#!/usr/bin/env python3
"""Render a safe, searchable, offline-first LuHm Credits page from curated source data.

The reference gallery is study material ONLY. Actual game-usage credits require
a separately approved per-asset receipt. No SaaS, scraping, runtime API, or embeddings.
"""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
APPROVED = ROOT / "media" / "artistCreditsApprovedV1.json"
REFERENCE = ROOT / "media" / "yumeReferenceGalleryV1.json"
DOCTRINE = ROOT / "doctrine" / "artistCreditLedgerV1.json"
SHA = re.compile(r"^[0-9a-f]{64}$")
SAFE_REF_HOSTS = {"www.nexusmods.com", "sketchfab.com", "github.com"}
SAFE_STATES = {"approvedArt", "runtimeImportProven"}


def safeUrl(value, knownHosts=None):
    if not isinstance(value, str) or not value or len(value) > 2048:
        return None
    try:
        parsed = urlsplit(value)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username
                or parsed.password or parsed.port is not None):
            return None
        if knownHosts and parsed.hostname not in knownHosts:
            return None
        return value
    except ValueError:
        return None


def buildIndex(approved, references, doctrine):
    if approved.get("schema") != "luhmOs.artistCreditsApproved.v1":
        raise ValueError("wrong approved artist credit schema")
    if references.get("scope") != "referenceCatalogOnly":
        raise ValueError("reference gallery has been relabeled as used art")
    if doctrine.get("schema") != "luhmOs.artistCreditLedger.v1":
        raise ValueError("artist credit doctrine missing")
    used = []
    seen = set()
    for item in approved.get("approvedAssets", []):
        if not isinstance(item, dict):
            raise ValueError("malformed approved asset record")
        if (item.get("publicAllowed") is not True
                or item.get("rightsReviewed") is not True
                or item.get("professorArtApproval") is not True
                or item.get("reviewState") not in SAFE_STATES
                or item.get("contentLane") != "cathedralPublic"):
            raise ValueError("uncleared asset must not enter public runtime credits")
        for field in ("assetId", "assetTitle", "creatorDisplayName", "requestedCreditString",
                      "license", "licenseUrlOrFile", "sourceUrl", "sourceHash"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError("missing required public credit field: " + field)
        if item["assetId"] in seen:
            raise ValueError("duplicate used asset id")
        seen.add(item["assetId"])
        if not SHA.fullmatch(item["sourceHash"]):
            raise ValueError("source file SHA-256 is missing")
        if item["license"].upper() in ("UNKNOWN", "UNLICENSED", "PENDING"):
            raise ValueError("unreviewed asset license")
        if not safeUrl(item["sourceUrl"]):
            raise ValueError("invalid used asset source URL")
        if not (safeUrl(item["licenseUrlOrFile"]) or item["licenseUrlOrFile"].startswith("LICENSES/")):
            raise ValueError("invalid license proof pointer")
        if item.get("creatorUrlWhenPublic") and not safeUrl(item["creatorUrlWhenPublic"]):
            raise ValueError("invalid creator link")
        used.append({
            "id": item["assetId"],
            "title": item["assetTitle"],
            "creator": item["creatorDisplayName"],
            "creatorUrl": item.get("creatorUrlWhenPublic") or None,
            "credit": item["requestedCreditString"],
            "license": item["license"],
            "licenseProof": item["licenseUrlOrFile"],
            "url": item["sourceUrl"],
            "role": item.get("assetRole") or "Game asset",
            "scope": "usedAndReviewed",
        })
    research = []
    researchIds = set()
    for entry in references.get("cards", []):
        if not isinstance(entry, dict):
            raise ValueError("invalid reference card")
        key = entry.get("id")
        url = safeUrl(entry.get("url"), SAFE_REF_HOSTS)
        if not isinstance(key, str) or not key or key in researchIds or not url:
            raise ValueError("invalid reference URL or duplicate reference id")
        researchIds.add(key)
        creatorUrl = entry.get("creatorUrl")
        if creatorUrl is not None and not safeUrl(creatorUrl, SAFE_REF_HOSTS):
            raise ValueError("invalid creator reference URL")
        research.append({
            "id": key, "title": str(entry.get("title") or "Study"),
            "creator": str(entry.get("creator") or "Creator not yet verified"),
            "creatorUrl": creatorUrl,
            "url": url,
            "role": str(entry.get("kind") or "Creative reference"),
            "lesson": str(entry.get("lesson") or ""),
            "scope": "researchReferenceNotUsed",
        })
    return {
        "schema": "luhmOs.artistCreditsSearchIndex.v1",
        "source": ["media/artistCreditsApprovedV1.json",
                   "media/yumeReferenceGalleryV1.json"],
        "used": sorted(used, key=lambda x: x["title"].casefold()),
        "references": sorted(research, key=lambda x: x["title"].casefold()),
        "unreviewedNotPromoted": True,
        "noExternalInference": True,
        "noTracking": True,
        "noRuntimeDownloads": True,
        "creditsAreNotAssetLicenseGrants": True,
    }


PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer">
<meta name="color-scheme" content="dark light">
<title>About the Art · LuHm OS</title>
<style>
:root{font-family:system-ui,sans-serif;color-scheme:dark;--bg:#090c16;--ink:#f3edf8;--dim:#c3bfd4;--card:#151a2b;--line:#37405b;--blue:#80bdfd}
@media(prefers-color-scheme:light){:root{color-scheme:light;--bg:#fafaff;--ink:#161b2f;--dim:#454e68;--card:#f0f2ff;--line:#bfc9e7;--blue:#124b9d}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);line-height:1.5}main{max-width:900px;padding:clamp(16px,4vw,42px);margin:auto}
h1{font:normal clamp(35px,7vw,63px)/1.1 Georgia,serif;margin:14px 0}h2{font-size:20px}a{color:var(--blue);overflow-wrap:anywhere}
input,button{color:inherit;font:inherit;border:1px solid var(--line);background:var(--card);border-radius:8px;padding:11px;min-height:44px}
input{width:100%;margin:14px 0}button{cursor:pointer}button[aria-pressed="true"]{border-color:var(--blue);box-shadow:0 0 0 1px var(--blue)}button:focus-visible,input:focus-visible,a:focus-visible{outline:3px solid var(--blue);outline-offset:3px}
.buttons{display:flex;gap:10px;flex-wrap:wrap}.intro,.hint,footer{color:var(--dim)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:22px}
article{padding:18px;background:var(--card);border:1px solid var(--line);border-radius:12px;min-width:0}article h2{margin:0 0 8px;font-size:20px}.credit{color:var(--dim);margin:6px 0}.kind{color:var(--blue);font-size:12px;text-transform:uppercase;letter-spacing:.08em}
.empty{padding:20px;border:1px dashed var(--line);border-radius:10px}footer{border-top:1px solid var(--line);margin-top:32px;padding-top:22px;font-size:13px}
</style>
</head>
<body>
<main>
<a href="./index.html">← Back to Witching Hour</a>
<p class="kind">LuHm OS · The artists behind the magic</p>
<h1>About the Art.</h1>
<p class="intro">Creative people deserve to be seen. See credited artwork in the game and the separate research references that inspired our investigations. A reference is not an imported game asset.</p>
<div class="buttons" role="group" aria-label="Credit category">
<button id="usedButton" type="button" aria-pressed="true">Used in the game</button>
<button id="refButton" type="button" aria-pressed="false">Creative references</button>
</div>
<label for="search">Search artists, assets, and sources</label>
<input id="search" type="search" autocomplete="off" placeholder="Search the credit spellbook">
<p class="hint" id="summary" aria-live="polite"></p>
<div id="results" class="grid" aria-live="polite"></div>
<footer>GitHub-authored static credits · No cookies, tracking, paid vectors, or third-party media downloads. Each source retains its own license; credit is not a grant of reuse rights.</footer>
</main>
<script type="application/json" id="creditsData">__SAFE_JSON_PAYLOAD__</script>
<script>
(() => {
  "use strict";
  const doc = document;
  const data = JSON.parse(doc.getElementById("creditsData").textContent);
  const buttons = [doc.getElementById("usedButton"),doc.getElementById("refButton")];
  const search = doc.getElementById("search");
  const results = doc.getElementById("results");
  const summary = doc.getElementById("summary");
  let tab = "used";
  const e = (tag,text) => { const node = doc.createElement(tag); if(text !== undefined)node.textContent=text; return node; };
  const link = (label,url) => { const a=e("a",label); a.href=url; a.target="_blank"; a.rel="noopener noreferrer nofollow"; return a; };
  function render(){
    buttons.forEach((b,i)=>b.setAttribute("aria-pressed",String((i===0)===(tab==="used"))));
    const source=tab==="used" ? data.used : data.references;
    const terms=search.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    const filtered=source.filter(item=>terms.every(term=>
      [item.title,item.creator,item.credit,item.license,item.role,item.lesson].filter(Boolean).join(" ").toLocaleLowerCase().includes(term)));
    results.replaceChildren();
    summary.textContent=filtered.length+" of "+source.length+" "+(tab==="used"?"verified game asset credits":"source-linked study references");
    if(!source.length){
      results.append(e("p","No third-party assets have been verified as used in this public candidate yet. Credits appear here when an exact asset receipt is approved."));
      return;
    }
    if(!filtered.length){results.append(e("p","No matching entries. Try another word."));return;}
    for(const item of filtered){
      const card=e("article");
      card.append(e("p",tab==="used"?"USED · "+item.role:"STUDIED · NOT IMPORTED"));
      card.append(e("h2",item.title),e("p",item.credit||"Artist/source: "+item.creator));
      if(item.creatorUrl)card.append(link("Artist profile",item.creatorUrl),e("span"," · "));
      card.append(link("Original source",item.url));
      if(item.license)card.append(e("p","License: "+item.license));
      if(item.lesson)card.append(e("p",item.lesson));
      results.append(card);
    }
  }
  buttons[0].addEventListener("click",()=>{tab="used";render();});
  buttons[1].addEventListener("click",()=>{tab="references";render();});
  search.addEventListener("input",render);
  render();
})();
</script>
</body>
</html>
'''


def renderPage(data):
    # prevent untrusted JSON values from prematurely closing the JSON script
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return PAGE.replace("__SAFE_JSON_PAYLOAD__", payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "host/harness/witchingHourBeta/credits.html")
    parser.add_argument("--json-output", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    def load(path):
        return json.loads(path.read_text(encoding="utf-8"))
    index = buildIndex(load(APPROVED),load(REFERENCE),load(DOCTRINE))
    content = renderPage(index)
    indexed = json.dumps(index, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != content:
            raise SystemExit("ARTIST_CREDITS_PAGE_STALE")
        if args.json_output and (not args.json_output.is_file() or args.json_output.read_text(encoding="utf-8") != indexed):
            raise SystemExit("ARTIST_CREDITS_JSON_STALE")
        print("GREEN_ARTIST_CREDIT_PAGE_SOURCE_MATCH")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(indexed, encoding="utf-8")
    print(json.dumps({"status":"CANDIDATE_GENERATED_NO_PUBLISH","used":len(index["used"]),
                      "studyReferences":len(index["references"]),"page":str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
