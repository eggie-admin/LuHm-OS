#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
example = json.loads((root / "assets/nexus/manifest.example.json").read_text(encoding="utf-8"))
assert example["policy"] == "LOCAL_PERMISSION_GATED_NO_AUTODOWNLOAD"
assert example["runtime_network"] is False
assert example["items"][0]["rights"]["allow_git"] is False
assert example["items"][0]["rights"]["allow_shared_apk"] is False

stager = (root / "tools/stageNexusAssets.py").read_text(encoding="utf-8")
assert "urllib" not in stager
assert "requests" not in stager
assert "nexusmods.com" not in stager.lower()
assert "runtime_network" in stager
assert "permission_evidence" in stager
assert "PRIVATE_PERSONAL_REFERENCE" in stager
assert "REDISTRIBUTABLE_WITH_EVIDENCE" in stager

runtime = root / "assets/nexus/runtime"
assert not runtime.exists(), "private Nexus runtime payloads must not be committed"

gitignore = (root / ".gitignore").read_text(encoding="utf-8")
assert "assets/nexus/runtime/" in gitignore
assert "assets/nexus/incoming/" in gitignore

print("NEXUS_PRIVATE_LANE=PASS")
