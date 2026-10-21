"""Source-only ten-pass guard. Never authenticates providers or changes infrastructure."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
read = lambda name: (root / name).read_text(encoding="utf-8")
doc = json.loads(read("doctrine/tenPassHardeningV1.json"))
passes = doc["passes"]
assert doc["schema"] == "luhmOs.tenPassHardening.v1"
assert doc["liveProviderChangesPerformed"] is False
assert doc["providerCostsAddedUsd"] == 0
assert len(passes) == 10 and [p["pass"] for p in passes] == list(range(1, 11))
assert all(p["state"] and p["gate"] and p["evidence"] for p in passes)
assert passes[1]["state"] == "UNKNOWN_LIVE_CONFIGURATION"
assert passes[6]["state"] == "PRIVATE_PLUGIN_NOT_INSTALLED"
assert "not installed" in passes[6]["evidence"]
assert "no active production DB" in doc["sqlLane"]
blueprint = read("render.yaml")
assert "healthCheckPath: /healthz" in blueprint and "autoDeployTrigger: off" in blueprint
copilot = read(".github/copilot-instructions.md")
assert "Ten-pass solo-studio security rules" in copilot
assert "do not apply it from Copilot or CI" in copilot
ignore = read(".gitignore")
assert all(pat in ignore for pat in (".env", ".secrets/", "*.sqlite3", "*.key", ".cloudflared/"))
localSql = read("host/api/typedLanesV1.sql")
pgSql = read("host/api/typedPostgresReviewV1.sql")
assert "STRICT;" in localSql and "PRAGMA foreign_keys = ON;" in localSql
assert "sourceRef NOT GLOB '*[^0-9a-f]*'" in localSql
assert "sha256 NOT GLOB '*[^0-9a-f]*'" in localSql
assert "REVIEW ONLY" in pgSql and "CREATE TABLE artifactPointer" in pgSql
plugin = json.loads(read("plugins/luhm-os/plugin.json"))
interface = plugin["extensions"]["com.openai"]["interface"]
assert interface.get("capabilities") == ["Read"]
assert "read-only" in plugin["description"]
print("TEN_PASS_SOURCE_AUDIT=GREEN; LIVE_PROVIDER_HARDENING=UNVERIFIED")
