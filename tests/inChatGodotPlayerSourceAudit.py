#!/usr/bin/env python3
"""Source-only gate: in-chat Godot bridge is isolated from the old cockpit."""
from pathlib import Path
import ast

source = Path("host/mcp/luhmHarness.py").read_text(encoding="utf-8")
ui = Path("host/harness/godotPlayerWidget.html").read_text(encoding="utf-8")
ast.parse(source)
assert 'GODOT_PLAYER_RESOURCE_URI = "ui://luhm-os/godot-player-v1.html"' in source
assert 'name="luhm_open_godot_player"' in source
assert '"frameDomains": [public_origin] if public_origin else []' in source
assert 'godot_embed=html' in source
assert "https://*.web-sandbox.oaiusercontent.com" in source
assert '"godotEmbeddingInChat": False' in source  # default cockpit remains unchanged
assert "WEB_EXPORT_FILES_STAGED" in source
assert "runtimeVerifiedInChat" in source
assert "<!-- LUHM_GODOT_FRAME -->" in ui
assert "<script" not in ui.lower()
print("GREEN_IN_CHAT_GODOT_SOURCE_ONLY")
