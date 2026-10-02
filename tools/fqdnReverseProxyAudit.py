#!/usr/bin/env python3
import json,re
from pathlib import Path
d=json.loads(Path("doctrine/fqdnReverseProxyV1.json").read_text())
assert d["names"]["localCockpit"]=="hydra.localhost"
assert d["localProxy"]["implementation"]=="nginx"
assert d["localProxy"]["apiPrefix"]=="/api/"
assert d["localProxy"]["upstreamPolicy"]=="loopbackOnly"
assert d["localProxy"]["browserDirectServicePorts"] is False
r=d["remotePrivate"]
assert r["accessRequired"] and r["tunnelRequired"]
assert r["tunnelTarget"]=="localReverseProxy"
assert r["directServiceTarget"] is False
assert r["routerPortForward"] is False
assert r["originIpPublished"] is False
assert d["serviceBoundaries"]["browserMayAddressDirectly"] is False
law=d["dnsLaw"]
assert law["applicationConfigUsesFqdn"] is True
assert law["rawLanIpInBrowserConfig"] is False
tls=d["tlsLaw"]
assert tls["localAndRemoteCertificatesAreSeparateTrustDomains"] is True
assert tls["localMkcertDoesNotProvePublicTls"] is True
edge=json.loads(Path("doctrine/cloudflareEdgeAssetTemplateV1.json").read_text())
assert edge["lanes"]["privateHydra"]["apiPath"]=="/api/"
assert edge["lanes"]["privateHydra"]["newApiSpine"] is False
print("FQDN REVERSE PROXY GREEN")
