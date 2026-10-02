#!/usr/bin/env python3
import json
from pathlib import Path
b=json.loads(Path("doctrine/fqdnReverseProxyBoundaryV1.json").read_text())
m=json.loads(Path("host/reverseProxy/serviceMap.json").read_text())
assert b["local"]["canonicalFqdn"]==m["localFqdn"]
assert b["remote"]["canonicalFqdnTemplate"]==m["remoteFqdn"]
assert b["remote"]["tunnelOrigin"]=="localReverseProxy"
assert m["edge"]["tunnelTarget"]=="localReverseProxy"
assert b["mobile"]["webOriginAllowed"] is False
assert b["mobile"]["cloudflareTunnelOriginAllowed"] is False
for s in m["privateServices"]: assert s["directRemote"] is False
print("NETWORK CONTRACT RECONCILIATION GREEN")
