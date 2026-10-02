#!/usr/bin/env python3
import hashlib,json,re,sys
from pathlib import Path
d=json.loads(Path("doctrine/runtimeStackV1.json").read_text())
b=d["browser"]; a=d["android"]; t=d["tooling"]
jq=Path(b["jquery"]["path"])
assert jq.is_file(), "RED_JQUERY_MISSING"
html=Path("frontEnd/index.html").read_text()
assert "./vendor/jquery-3.7.1.min.js" in html
assert "./jquery/luhm.cockpit.js" in html
assert html.index("jquery-3.7.1.min.js") < html.index("luhm.cockpit.js")
assert b["jqueryUi"]["state"]=="approvedCandidate"
assert b["bootstrap"]["state"]=="approvedCandidate"
assert b["jqueryUi"]["runtimeCdn"] is False and b["bootstrap"]["runtimeCdn"] is False
assert "jquery-ui" not in html.lower() and "bootstrap" not in html.lower(), "RED_UNPROVEN_UI_LIBRARY_ACTIVE"
gradle=Path("androidWeb3Plugin/plugin/build.gradle.kts").read_text()
assert "JavaVersion.VERSION_17" in gradle
assert "JvmTarget.JVM_17" in gradle
assert a["java"]["jvmTarget"]=="17" and a["kotlin"]["jvmTarget"]=="17"
assert t["python"]["major"]==3
print("RUNTIME STACK AUDIT GREEN")
print("jquerySha256="+hashlib.sha256(jq.read_bytes()).hexdigest())
print("python="+sys.version.split()[0])
