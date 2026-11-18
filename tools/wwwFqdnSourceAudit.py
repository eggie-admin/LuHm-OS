#!/usr/bin/env python3
"""Fail-closed source audit for WWW public site routing, never live DNS or release proof."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/"doctrine/wwwPublicFqdnActivationV1.json").read_text())
edge=json.loads((ROOT/"doctrine/staticPublicEdgeV1.json").read_text())
cloud=json.loads((ROOT/"doctrine/cloudflareEdgeHardeningV1.json").read_text())
brand=json.loads((ROOT/"doctrine/organizationBrandRegistryV1.json").read_text())
doc=(ROOT/"manual/wwwEggieBagelfaceDomainCutover20261118.md").read_text()
render=(ROOT/"render.yaml").read_text()
public=(ROOT/"publicationSite/index.html").read_text()
assert m["schema"]=="luhmOs.wwwPublicFqdnActivation.v1"
assert m["zoneApex"]=="eggiebagelface.art"
assert m["requestedHost"]=="www."+m["zoneApex"]
assert edge["fqdnCandidates"]["publicSite"]["alternate"]==m["requestedHost"]
assert edge["fqdnCandidates"]["publicSite"]["origin"]==m["targetPublicationOrigin"]["currentUrl"].removeprefix("https://").rstrip("/")
assert cloud["canonicalZone"]==m["zoneApex"]
assert brand["publicBrands"]["luhmOs"]["displayName"]=="LuHm-OS"
assert "LuHm-OS" in public and "Project Premonition" in public
assert "name: luhm-os-publication-site" in render
assert "branch: publication/plugin-full-green-20260930" in render
assert "staticPublishPath: publicationSite" in render
assert m["targetPublicationOrigin"]["currentlyDeployedBranch"]=="publication/plugin-full-green-20260930"
assert m["targetPublicationOrigin"]["autoDeploy"]=="off"
assert m["proposedHosting"]["cloudflareDnsAfterRenderDomain"]=={
    "name":"www","type":"CNAME","target":"luhm-os-publication-site.onrender.com",
    "proxyStatus":"DNS_ONLY_FOR_INITIAL_DOMAIN_AND_TLS_VERIFICATION",
    "onlyCreateIfAbsent":True,"overwriteExistingRecord":False,
    "manualOperatorAuthenticatedCloudflareRequired":True
}
assert m["protectedSeparation"]["doNotAttachWwwToProtectedWorker"] is True
assert m["protectedSeparation"]["doNotDisableExistingAccess"] is True
assert m["protectedSeparation"]["dnsMxTxtDsCaaUntouched"] is True
assert len(m["protectedSeparation"]["reservedFqdns"])==4
assert m["tls"]["noSelfSigned"] and m["tls"]["noForceHstsPreload"]
assert m["crownStatus"]=="STOP"
assert m["providerChangesApplied"] is False
assert m["publicReleasePromotion"] is False
assert all(value is False for value in m["verification"].values())
assert "https://www.eggiebagelface.art/" in doc
assert "https://eggiebagelface.art/" in doc
assert "Project Hydra" in doc and "Project Premonition" in doc
assert "do not" in doc.lower() and "cloudflare access" in doc.lower()
print("GREEN_WWW_PUBLIC_SITE_FQDN_CANON_SOURCE_ONLY")
print("NOT_LIVE: no Render domain, DNS, TLS, redirect or public site cutover evidenced")
