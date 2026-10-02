#!/usr/bin/env python3
import json
from pathlib import Path
d=json.loads(Path("doctrine/fqdnReverseProxyBoundaryV1.json").read_text())
assert d["authority"]=="Professor"
assert d["local"]["canonicalFqdn"]=="hydra.localhost"
assert d["local"]["reverseProxy"]=="nginx"
assert d["local"]["originClass"]=="desktopOrServer"
assert d["local"]["backendBindPolicy"]=="loopbackOnly"
assert d["remote"]["tunnelOrigin"]=="localReverseProxy"
assert d["remote"]["directBackendExposure"] is False
assert d["remote"]["routerPortForwarding"] is False
m=d["mobile"]
for key in ("webOriginAllowed","reverseProxyAllowed","cloudflareTunnelOriginAllowed","cdnOriginAllowed","publicListenerAllowed"):
    assert m[key] is False, "RED_MOBILE_SERVER_BOUNDARY"
assert m["localDevUtilityPolicy"]=="loopbackOnlyNonAuthoritative"
print("FQDN REVERSE PROXY BOUNDARY GREEN")
