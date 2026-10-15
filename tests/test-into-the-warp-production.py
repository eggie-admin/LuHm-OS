#!/usr/bin/env python3
"""Into the Warp preproduction contract; no media generation or external writes."""
import json
from pathlib import Path
path = Path(__file__).resolve().parents[1] / "media/pirate-daddy-film/into-the-warp-project-template-v3.json"
v = json.loads(path.read_text())
assert v["schema"] == "luhm.into-the-warp.project-draft.v3"
assert v["publication"] == "crown-stop"
script = v["script"]
assert script["status"] == "sealed" and script["modify"] is False
assert script["sha256"] == "6f6054e86f6f6dd74ffc9355a34f86d2ff4c3822f1c8c4f2d20b8a701b38f9ef"
assert script["movements"] == ["transmission", "old-guard", "witching-hour"]
assert [s["id"] for s in v["sections"]] == ["100", "200", "300", "400", "500"]
assert v["counts"] == {"sections": 5, "storyboardPanels": 23, "renderBlocks": 7}
panels = [p for s in v["sections"] for p in s["panels"]]
blocks = [p for s in v["sections"] for p in s["renderBlocks"]]
assert len(set(panels)) == len(panels) == 23
assert blocks == ["100", "200", "300", "401", "402", "403", "500"]
assert v["locks"]["approvedScriptUntouched"]
assert v["locks"]["audioDeferred"]
assert v["locks"]["belldandyReadsCodexLoreAt401"]
assert v["locks"]["noCodexOpeningAt500"]
assert v["locks"]["outroIsExistingCodexCallback"]
assert v["sections"][4]["name"] == "root-access-outro-stinger"
assert "no new codex lookup" in v["sections"][4]["direction"].lower()
assert v["codex"]["owner"] == "belldandy"
assert v["codex"]["primaryAppearance"]["shot"] == "401"
assert v["codex"]["primaryAppearance"]["movement"] == "old-guard"
assert v["codex"]["finalCallback"]["newLookup"] is False
assert v["locks"]["lumPhysicallyFollows"] and v["locks"]["fourMonitorsFixed"]
assert v["locks"]["autoPublish"] is False
assert v["storage"]["sourceAuthority"] == "github"
assert v["storage"]["durableBinaryAuthority"] == "google-drive"
assert v["runtime"]["gpu"] == "unverified"
assert v["authority"]["publication"] == "professor-only"
print("INTO_THE_WARP_SOURCE_CANDIDATE_GREEN_NOT_ARTWORK_OR_RUNTIME_GREEN")
