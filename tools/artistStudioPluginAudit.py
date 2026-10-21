#!/usr/bin/env python3
"""Strict source audit of the in-chat LuHm artist studio, not browser/runtime proof."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re
import subprocess

root = Path(__file__).resolve().parents[1]
contract = json.loads((root / "doctrine/artistStudioPluginV1.json").read_text())
experience = json.loads((root / "doctrine/inChatExperienceV1.json").read_text())
truth = json.loads((root / "doctrine/currentSourceTruthV3.json").read_text())
plugin = json.loads((root / "plugins/luhm-os/plugin.json").read_text())
html = (root / "host/harness/widget.html").read_text()
harness = (root / "host/mcp/luhmHarness.py").read_text()
assert contract["schema"] == "luhmOs.artistStudioPlugin.v1"
assert contract["pluginTool"] == "luhm_open_cockpit"
assert contract["resourceUri"] == "ui://luhm-os/cockpit-v2.html"
assert contract["project"]["scriptSealed"] is True
assert contract["project"]["scriptNeverIncludedInWidget"] is True
assert contract["project"]["codexOwner"] == "belldandy"
assert contract["project"]["codexLoreShot"] == "401"
assert contract["project"]["codexCallbackShot"] == "500"
assert contract["project"]["audioDeferred"] is True
ids = [s["id"] for s in contract["project"]["shots"]]
assert ids == ["100","200","300","401","402","403","500"]
for flag in ("serverWrites","providerWrites","driveUpload","githubMutations","renderExecution","publication"):
    assert contract["stateBoundary"][flag] is False
assert experience["runtime"]["artistStudio"]["contract"] == "doctrine/artistStudioPluginV1.json"
assert experience["runtime"]["artistStudio"]["writesToServer"] is False
assert truth["experienceLayer"]["artistStudio"] == "doctrine/artistStudioPluginV1.json"
assert truth["crownStatus"] == "STOP"
assert "artist-first" in plugin["description"].lower()
assert plugin["extensions"]["com.openai"]["interface"]["capabilities"] == ["Read"]
assert '"artistStudio": artist_studio' in harness
assert "artist_studio_path" in harness
assert "RED_ARTIST_STUDIO_PRIVILEGE" in harness
assert html.count("<style>") == html.count("</style>") == 1
assert html.count("<script>") == html.count("</script>") == 1
class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
    def handle_starttag(self, tag, attrs):
        for k,v in attrs:
            if k == "id": self.ids.append(v)
p = Inspector()
p.feed(html)
assert len(p.ids) == len(set(p.ids)), "duplicate DOM ids"
required = ("studioTimeline","studioVisual","studioSeconds","studioUndo","studioRedo",
            "studioDownload","studioCopy","studioReset","studioJson","studioPreview",
            "studioStatus","studioLock")
assert all(item in p.ids for item in required)
assert "function studioSet(" in html and "function studioUndo(" in html and "function studioRedo(" in html
assert "studioState.undo.push" in html and "studioState.redo.push" in html
assert "function studioPortable(" in html and "publicationApproved:false" in html
assert "studioInitialize(payload?.artistStudio)" in html
assert "function studioWire()" in html
assert "studioWire();render(window.openai?.toolOutput)" in html
assert "wireStudio();" not in html
# Artist-entered text must go through textContent or value, not an injection sink.
studio = html[html.index("/* In-chat artist studio:"):html.index("let rpcId=0;")]
assert ".innerHTML" not in studio and ".outerHTML" not in studio
assert ".fetch(" not in studio and "localStorage" not in studio and "sessionStorage" not in studio
assert "URL.createObjectURL" in studio and "URL.revokeObjectURL" in studio
js = html.split("<script>",1)[1].split("</script>",1)[0]
check = subprocess.run(["node", "--check", "-"], input=js, text=True, capture_output=True)
if check.returncode:
    raise SystemExit("RED_WIDGET_JS_SYNTAX: " + check.stderr[:900])
print("ARTIST_STUDIO_PLUGIN_SOURCE_GREEN_LOCAL_DRAFT_ONLY_NOT_HOST_RUNTIME_GREEN")
