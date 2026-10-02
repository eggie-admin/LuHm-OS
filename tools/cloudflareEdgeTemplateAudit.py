#!/usr/bin/env python3
import json
from pathlib import Path
p=Path("doctrine/cloudflareEdgeAssetTemplateV1.json")
d=json.loads(p.read_text())
lanes=d["lanes"]
assert d["status"]=="candidateNotDeployed"
assert lanes["privateHydra"]["cloudflareAccessRequired"] is True
assert lanes["privateHydra"]["cloudflareTunnelRequired"] is True
assert lanes["privateHydra"]["routerPortForwardRequired"] is False
assert lanes["privateHydra"]["newApiSpine"] is False
assert lanes["assetCdn"]["thirdPartyRuntimeDependencies"] is False
assert lanes["mcp"]["mergeIntoHydraTunnel"] is False
assert d["dns"]["noIpAddressesInSource"] is True
assert d["deployment"]["automatic"] is False
assert d["deployment"]["cloudflareAccountMutationPerformed"] is False
html=Path("frontEnd/index.html").read_text()
srv=Path("frontEnd/srv.txt").read_text()
resolver=Path("frontEnd/staticService.js").read_text()
assert '<script src="./staticService.js"></script>' in html
assert html.index("staticService.js") < html.index("jquery-3.7.1.min.js")
assert "mode=localFirst" in srv
assert "remoteAssetBase=" in srv
assert "remoteAuthority=none" in srv
assert "LuHmStaticService" in resolver
assert "candidates" in resolver
assert "remoteAssetBase" in resolver
assert 'fetch("./srv.txt"' in resolver
assert '{ cache: "no-store", credentials: "same-origin" }' in resolver
app=Path("frontEnd/app.js").read_text()
assert "LuHmStaticService.load()" in app
assert "LuHmAssets" in app
print("CLOUDFLARE EDGE TEMPLATE GREEN")
