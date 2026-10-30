#!/usr/bin/env python3
"""DEV and npm staging plus read-only four-package source/dependency gate."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
POLICY = "doctrine/fourPackageTrainV1.json"
LANES = ("dev", "npm", "dmg", "apk")

def load(root=ROOT):
    return json.loads((root / POLICY).read_text(encoding="utf-8"))

def source_ref(root=ROOT):
    env = os.environ.get("LUHM_SOURCE_REF", "").strip()
    current = subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,text=True,check=False)
    actual=current.stdout.strip() if current.returncode == 0 else ""
    if not re.fullmatch(r"[0-9a-f]{40}",actual):
        raise ValueError("GIT_EXACT_HEAD_REQUIRED")
    if env and env != actual:
        raise ValueError("SOURCE_SHA_DRIFT")
    return actual

def export_sections(text):
    starts = list(re.finditer(r"^\[preset\.(\d+)\]\s*$",text,re.MULTILINE))
    if not starts:
        return {}
    return {int(m.group(1)):text[m.start():starts[i+1].start() if i+1 < len(starts) else len(text)]
            for i,m in enumerate(starts)}

def inspect(policy, files, root=ROOT):
    errors=[]
    def check(ok, why):
        if not ok: errors.append(why)
    check(policy.get("schema")=="luhmOs.fourPackageTrain.v1","SCHEMA")
    check(policy.get("order")==list(LANES) and set(policy.get("lanes",{}))==set(LANES),"EXACTLY_FOUR_LANES")
    check(all(policy.get("lanes",{}).get(k,{}).get("publish") is False for k in LANES),"NO_PUBLICATION")
    check(policy.get("publication",{}).get("crownStatus")=="STOP","CROWN_STOP")
    allow=policy.get("sourceAllowlist",[])
    check(len(allow)>=10 and len(allow)==len(set(allow)),"DEV_ALLOWLIST")
    for rel in allow:
        path=Path(rel)
        check(not path.is_absolute() and ".." not in path.parts and len(path.parts)>0,"DEV_PATH_TRAVERSAL")
        if path.is_absolute() or ".." in path.parts:
            continue
        p=root/path
        check(p.is_file() and not p.is_symlink(),"DEV_SOURCE_MISSING_OR_SYMLINK:"+rel)
        if p.is_file():
            check(p.stat().st_size<=policy["maxDevFileBytes"],"DEV_SOURCE_TOO_LARGE:"+rel)
    check(not any("private/" in x or "media/" in x or "assets/lum/" in x for x in allow),"PRIVATE_SOURCE_NOT_ALLOWLISTED")
    npm=policy["npm"]
    pkg=json.loads(files["glassPkg"])
    lock=json.loads(files["glassLock"])
    jqp=json.loads(files["frontPkg"])
    outer=json.loads(files["webPkg"])
    check(pkg.get("private") is True and outer.get("private") is True,"NPM_PRIVATE")
    check(outer.get("files")==npm["stagedFiles"],"NPM_PACK_ALLOWLIST")
    check(pkg.get("dependencies")=={"@babylonjs/core":npm["babylonVersion"],"jquery":npm["jqueryVersion"],"vue":npm["vueVersion"]},"GLASS_RUNTIME_DEPS_PINNED")
    check(pkg.get("devDependencies")=={"vite":npm["viteVersion"]},"VITE_BUILD_DEP_PINNED")
    check(jqp.get("dependencies")=={"jquery":npm["jqueryVersion"]},"JQUERY_SOURCE_PIN")
    check(lock.get("lockfileVersion")==3 and lock.get("packages",{}).get("",{}).get("dependencies")==pkg.get("dependencies"),"NPM_LOCKFILE")
    check(lock.get("packages",{}).get("",{}).get("devDependencies")==pkg.get("devDependencies"),"NPM_DEV_LOCK")
    check(outer.get("name")=="luhmos-k9000-web" and outer.get("version")=="0.1.0-candidate.0","NPM_ARTIFACT_ID")
    check(policy["lanes"]["npm"]["artifact"]=="luhmos-k9000-web-0.1.0-candidate.0.tgz","NPM_ARTIFACT_NAME")
    presets=export_sections(files["presets"])
    headers=re.findall(r"^\[preset\.(\d+)\.options\]\s*$",files["presets"],re.MULTILINE)
    check(len(presets)==4 and sorted(presets)==[0,1,2,3],"FOUR_GODOT_PRESETS")
    check(len(headers)==4 and sorted(headers)==["0","1","2","3"],"ONE_OPTIONS_SECTION_PER_PRESET")
    check('name="Android Proposed"' in presets.get(0,"") and 'package/unique_name="art.eggiebagelface.luhmos.testing"' in presets.get(0,""),"TESTING_ID_PRESERVED")
    check('name="macOS K9000 Candidate"' in presets.get(2,"") and 'export_path="build/k9000/K9000-development.dmg"' in presets.get(2,""),"DMG_GODOT_PRESET")
    check("codesign/codesign=1" in presets.get(2,"") and "notarization/notarization=0" in presets.get(2,""),"DMG_ADHOC_ONLY")
    check('name="Android Crown Cathedral Public Candidate"' in presets.get(3,"") and 'package/unique_name="art.eggiebagelface.luhmos.cathedral"' in presets.get(3,""),"PUBLIC_ANDROID_PRESET_ID")
    check("permissions/internet=false" in presets.get(0,"") and "permissions/internet=false" in presets.get(3,""),"ANDROID_OFFLINE_PERMISSION")
    gradle=files["gradle"]
    check('implementation("org.godotengine:godot:4.7.2.stable")' in gradle,"GODOT_ANDROID_DEP_PIN")
    check('implementation("androidx.webkit:webkit:1.17.1")' in gradle,"ANDROID_WEBKIT_PIN")
    check("compileSdk = 36" in gradle and "minSdk = 24" in gradle,"ANDROID_SDK_PINS")
    apk_workflow=files["apkWorkflow"]
    check("python3 tools/forgeCastGate.py" in apk_workflow and "CAST gate" in apk_workflow,"APK_OWNER_CAST_WORKFLOW")
    check(policy["lanes"]["apk"]["execution"]=="EXISTING_OWNER_CAST_WORKFLOW","APK_NO_DUPLICATE_BYPASS")
    workflow=files["trainWorkflow"]
    check("npm ci --ignore-scripts" in workflow and "npm pack" in workflow,"NPM_CI_AND_PACK")
    check("workflow_dispatch" in workflow and "build_dmg" in workflow,"DMG_EXPLICIT_DISPATCH")
    check("github.actor == 'eggie-admin'" in workflow,"DMG_OWNER_CHECK")
    check("npm publish" not in workflow and "gh release create" not in workflow,"NO_REGISTRY_OR_GH_PUBLICATION")
    return sorted(set(errors))

def audit(root=ROOT):
    policy=load(root)
    names={"glassPkg":"frontEnd/prototypes/glassWorld/package.json",
           "glassLock":"frontEnd/prototypes/glassWorld/package-lock.json",
           "frontPkg":"frontEnd/package.json",
           "webPkg":"packages/k9000-web/package.json",
           "presets":"export_presets.cfg",
           "gradle":"androidWeb3Plugin/plugin/build.gradle.kts",
           "apkWorkflow":".github/workflows/android-testing-build.yml",
           "trainWorkflow":".github/workflows/four-package-train.yml"}
    files={k:(root/p).read_text(encoding="utf-8") for k,p in names.items()}
    failed=inspect(policy,files,root)
    return {"schema":"luhmOs.fourPackageTrainReceipt.v1",
            "sourceRef":source_ref(root),"lanes":list(LANES),
            "checks":"SOURCE_AND_DEPENDENCY_CONTRACT",
            "failures":failed,"verdict":"GREEN_SOURCE_NOT_RELEASED" if not failed else "RED_SOURCE",
            "dmgBuilt":False,"apkBuilt":False,"npmPublished":False,"crownStatus":"STOP"}

def record(path,lane,ref):
    data=path.read_bytes()
    return {"lane":lane,"filename":path.name,"sourceRef":ref,
            "sha256":hashlib.sha256(data).hexdigest(),
            "bytes":len(data),"status":"PRIVATE_CI_CANDIDATE_NO_RELEASE"}

def build_dev(root=ROOT, destination=None):
    cfg=load(root)
    if inspect(cfg,{k:(root/p).read_text(encoding="utf-8") for k,p in {
       "glassPkg":"frontEnd/prototypes/glassWorld/package.json",
       "glassLock":"frontEnd/prototypes/glassWorld/package-lock.json",
       "frontPkg":"frontEnd/package.json",
       "webPkg":"packages/k9000-web/package.json",
       "presets":"export_presets.cfg",
       "gradle":"androidWeb3Plugin/plugin/build.gradle.kts",
       "apkWorkflow":".github/workflows/android-testing-build.yml",
       "trainWorkflow":".github/workflows/four-package-train.yml"}.items()},root):
        raise ValueError("SOURCE_CONTRACT_RED")
    ref=source_ref(root)
    output=destination or root/"build/fourPackage/dev"
    output.mkdir(parents=True,exist_ok=True)
    archive=output/cfg["lanes"]["dev"]["artifact"]
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for rel in sorted(cfg["sourceAllowlist"]):
            member=zipfile.ZipInfo("luhmos-dev/"+rel,date_time=(1980,1,1,0,0,0))
            member.compress_type=zipfile.ZIP_DEFLATED
            member.external_attr=(0o100644<<16)
            z.writestr(member,(root/rel).read_bytes())
    if archive.stat().st_size > cfg["maxDevArchiveBytes"]:
        archive.unlink()
        raise ValueError("DEV_ARCHIVE_TOO_LARGE")
    receipt=record(archive,"dev",ref)
    (output/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    return receipt

def stage_npm(root=ROOT,destination=None):
    policy=load(root)
    ref=source_ref(root)
    dist=root/"frontEnd/prototypes/glassWorld/dist"
    if not (dist/"index.html").is_file():
        raise ValueError("NPM_DIST_BUILD_REQUIRED")
    destination=destination or root/"build/fourPackage/npm/stage"
    if destination.exists(): shutil.rmtree(destination)
    destination.mkdir(parents=True)
    allowed={".html",".js",".css",".svg",".png",".webp",".wasm"}
    count=0
    for source in sorted(dist.rglob("*")):
        if source.is_symlink():raise ValueError("NPM_BUNDLE_SYMLINK")
        if source.is_file():
            if source.suffix.lower() not in allowed or source.stat().st_size>policy["maxNpmAssetBytes"]:
                raise ValueError("NPM_UNKNOWN_OR_LARGE_ASSET")
            target=destination/"dist"/source.relative_to(dist)
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
            count+=1
    if count>policy["maxNpmFiles"]: raise ValueError("NPM_TOO_MANY_FILES")
    for suffix in ("html","css","js"):
        source=root/("frontEnd/k9000."+suffix)
        target=destination/"k9000"/source.name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    for name in ("k9000-cathedral-mark.svg","k9000-main-192.png","k9000-adaptive-432.png"):
        source=root/"frontEnd/brand"/name
        target=destination/"k9000/brand"/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    for src,dst in (("packages/k9000-web/package.json","package.json"),("packages/k9000-web/README.md","README.md"),("LICENSE","LICENSE")):
        shutil.copyfile(root/src,destination/dst)
    return {"lane":"npm","sourceRef":ref,"status":"STAGED_FOR_NPM_PACK_NO_PUBLICATION","files":count}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action",choices=("audit","build-dev","stage-npm"))
    args=ap.parse_args()
    if args.action=="audit":
        result=audit()
        print(json.dumps(result,indent=2))
        return 1 if result["failures"] else 0
    result=build_dev() if args.action=="build-dev" else stage_npm()
    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
