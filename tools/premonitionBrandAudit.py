#!/usr/bin/env python3
"""Case-sensitive brand and honest Samsung/F-Droid distribution name gate."""
from __future__ import annotations
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def evaluate(policy,registry,chat,fdroid,readme,onePager):
    failures=[]
    def require(p,kind):
        if not p: failures.append(kind)
    require(policy["displayIdentity"]=="LuHm-OS: Project Premonition","BRAND_IDENTITY")
    require(policy["product"]=="LuHm-OS" and policy["productNameCaseSensitive"],"CASE_SENSITIVE_BRAND")
    require(registry["publicBrands"]["luhmOs"]["displayName"]=="LuHm-OS","REGISTRY_PRODUCT")
    require(registry["publicBrands"]["luhmOs"]["publisher"]==policy["publisher"],"REGISTRY_PUBLISHER")
    require(chat["developmentIdentity"]["productName"]=="LuHm-OS","CHAT_PRODUCT")
    require(chat["developmentIdentity"]["formerName"]=="Project Hydra","LEGACY_HYDRA")
    require("LuHm OS" in chat["bootstrapTrigger"]["projectNames"],"LEGACY_ALIAS")
    require("LuHm-OS" in chat["bootstrapTrigger"]["projectNames"],"NEW_ALIAS")
    require('NAME="LuHm-OS: Project Premonition Beta"' in fdroid,"FDROID_METADATA_BRAND")
    require('APP="art.eggiebagelface.luhmos.beta"' in fdroid,"PACKAGE_ID_UNCHANGED")
    require(readme.startswith("# LuHm-OS: Project Premonition\n"),"README_IDENTITY")
    for marker in ("NOT a public campaign","not** been verified","unverified","No sponsor"):
        require(marker.lower() in onePager.lower(),"FUNDING_NO_FALSE_CLAIM_"+marker.replace(" ","_"))
    for kind in ("publicMarketing","publicRepositoryPublication","productionSigning","sponsorClaims"):
        require(policy["authorizations"][kind] is False,"NO_AUTOMATIC_RELEASE_"+kind)
    for kind in ("androidApkSigner","fdroidIndexSigner","macosDeveloperID"):
        require("PROVEN" not in policy["platformTrust"][kind] or "NOT_PROVEN" in policy["platformTrust"][kind],"TRUST_BOUNDARY_"+kind)
    require(policy["crownStatus"]=="STOP","CROWN_STOP")
    return sorted(set(failures))
def main():
    policy=load("doctrine/premonitionEnterpriseBrandV1.json")
    errors=evaluate(policy,load("doctrine/organizationBrandRegistryV1.json"),
      load("doctrine/projectChatCanonV1.json"),
      (ROOT/"tools/prepareFdroidRepoCandidate.py").read_text(encoding="utf-8"),
      (ROOT/"README.md").read_text(encoding="utf-8"),
      (ROOT/"manual/premonition-funding-one-pager.md").read_text(encoding="utf-8"))
    if errors:raise SystemExit("RED_BRAND:"+",".join(errors))
    print("AMBER_ENTERPRISE_BRAND_SOURCE_CONTRACT; PUBLIC_RELEASE_AND_FDROID_INDEX_UNVERIFIED")
if __name__=="__main__":main()
