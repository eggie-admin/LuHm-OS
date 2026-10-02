#!/usr/bin/env python3
import json,re
from pathlib import Path
p=json.loads(Path("host/reverseProxy/serviceMap.json").read_text())
assert p["authority"]=="Professor"
assert p["originClass"]=="desktopOrServer"
assert p["localFqdn"]=="hydra.localhost"
assert p["remoteFqdn"]=="hydra.eggiebagelface.art"
assert p["edge"]["accessRequired"] is True
assert p["edge"]["tunnelTarget"]=="localReverseProxy"
assert p["edge"]["originAddressInSource"] is False
assert p["edge"]["routerPortForward"] is False
assert {r["publicPath"] for r in p["routes"]}=={"/","/api/"}
for service in p["privateServices"]:
    assert service["bind"]=="loopback"
    assert service["directRemote"] is False
blob=Path("host/reverseProxy/serviceMap.json").read_text()
assert not re.search(r'(?<![A-Za-z0-9])(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.',blob)
print("REVERSE PROXY SERVICE MAP GREEN")
