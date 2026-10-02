#!/usr/bin/env python3
import json
from pathlib import Path
d=json.loads(Path("doctrine/assetCastBridgeV1.json").read_text())
m=json.loads(Path(d["sourceManifest"]).read_text())
assert d["authority"]=="Professor"
assert m["status"]=="sourceSlotsReady"
assert d["acceptedRuntimeStates"]==["runtimeImportProven"]
assert d["bridgeLaw"]["exactSourceRequired"] is True
assert d["bridgeLaw"]["hashRequired"] is True
assert d["bridgeLaw"]["licenseDispositionRequired"] is True
assert d["bridgeLaw"]["runtimeProofRequired"] is True
assert d["bridgeLaw"]["professorPromotionRequired"] is True
assert d["bridgeLaw"]["missingAssetMayBecomeGreen"] is False
assert "protectedReference" in d["forbiddenSourceClasses"]
assert d["fallbackPolicy"]["fallbackMayNotMasqueradeAsApprovedArt"] is True
required={"portrait","fullBody","spriteIdle","spriteWalk","spriteRun","expressionSheet","uiIcon"}
assert required==set(m["requiredFamilies"])
assert {"lum","urd","belldandy","skuld"}==set(m["characters"])
print("ASSET CAST BRIDGE CONTRACT GREEN")
