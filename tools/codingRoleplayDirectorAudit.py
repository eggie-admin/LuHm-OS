#!/usr/bin/env python3
import json
from pathlib import Path
d=json.loads(Path("doctrine/codingRoleplayDirectorV1.json").read_text())
js=Path("frontEnd/jquery/luhm.codingRoleplay.js").read_text()
assert d["authority"]=="Professor"
assert d["bubbleLaw"]["bubbleCannotEstablishGreen"] is True
assert d["bubbleLaw"]["vendorCannotCrown"] is True
assert d["bubbleLaw"]["roleplayCannotRewriteEvidence"] is True
assert d["deepDungeonPresentation"]["rooms"][0]=="surface"
assert d["deepDungeonPresentation"]["rooms"][-1]=="dungeonMap"
assert d["layers"]["layerCast"]=="oniVendorPortraitPose"
assert "$.codingRoleplay" in js
assert "evidenceRefs" in js and "machineState" in js
assert 'authority:String(data.authority || "presentationOnly")' in js
assert 'luhm:boss:capabilityRequest' in js
assert 'luhm:boss:capabilityResult' in js
print("CODING ROLEPLAY DIRECTOR GREEN")
