#!/usr/bin/env python3
"""Static guard for Pirate Daddy's Film prior to locked screenplay ingestion."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
text = (root / "media/pirate-daddy-film/production-workflow-template.md").read_text()
assert "Belldandy is the reader/owner" in text
assert "**Movement II, shot 401**" in text
assert "Her historical reading is interrupted" in text
assert "no new wiki lookup" in text
assert "Return to the **same** Anti-Daddy record" in text
assert "not a command terminal" in text.lower()
assert "source-script" in text
assert "PROPOSED_ONLY" in text
print("PIRATE_DADDY_CODEX_LORE_PLACEMENT_SOURCE_GREEN")
