#!/usr/bin/env python3
"""Fail-closed static proof of Titan 7 local jQuery UI and mode boundaries."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
h=root/"host/harness"
html=(h/"index.html").read_text()
widget=(h/"widget.html").read_text()
js=(h/"titan7Cockpit.js").read_text()
server=(root/"host/mcp/luhmHarness.py").read_text()
assert html.index("jquery-3.7.1.min.js")<html.index("jquery-ui-1.14.2.min.js")<html.index("titan7Cockpit.js")
assert 'id="titan7Accordion"' in html and 'data-luhm-titan7' in html
assert all(f'data-luhm-mode="{m}"' in html and f'data-luhm-chat-mode="{m}"' in widget for m in ("default","ic","ooc","irl"))
assert 'aria-pressed' in html and 'aria-pressed' in widget
assert '.accordion({' in js and 'collapsible:true' in js and 'authorityEffect:"none"' in js
assert 'workerExecution:"QUARANTINED"' in js and 'hostSync:"UNVERIFIED"' in js
for name,tag in (("jquery-3.7.1.min.js","jQuery v3.7.1"),("jquery-ui-1.14.2.min.js","jQuery UI - v1.14.2")):
 content=(h/name).read_text()
 assert tag in content[:260] and len(content)>50000,name
 assert f'"{name}"' in server,name
for name in ("jquery-LICENSE.txt","jquery-ui-LICENSE.txt"):
 assert "Permission is hereby granted" in (h/name).read_text(),name
print("GREEN_TITAN7_JQUERY_MODE_SOURCE")
print("HOST_PUBLICATION_PROOF_NOT_ESTABLISHED")
