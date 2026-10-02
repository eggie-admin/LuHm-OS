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
print("CLOUDFLARE EDGE TEMPLATE GREEN")
