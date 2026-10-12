#!/usr/bin/env python3
"""Source-only Oni/wiring guard. No network, build or deploy."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
contract=json.loads((root/"doctrine/inChatOniRecoveryV1.json").read_text())
assert contract["schema"]=="luhmOs.inChatOniRecovery.v1"
assert contract["status"]=="SOURCE_CANDIDATE_ONLY"
assert contract["buildGate"]["requiredWord"]=="cast"
assert contract["buildGate"]["genericApprovalDoesNotReplaceCast"] is True
assert contract["authority"]["canSelfApprove"] is False
assert contract["workers"]["hiddenAsyncExecution"] is False
assert len(contract["evidenceGates"])==7
assert contract["currentClaims"]["inChatHost"]=="UNVERIFIED"
paths=[
 "agents/lum/SKILL.md","agents/kugiToolOni/SKILL.md",
 "agents/urdMutationOni/SKILL.md","agents/belldandyQualityOni/SKILL.md",
 "agents/skuldResearchOni/SKILL.md","agents/buildOnis/SKILL.md",
 "plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md"
]
for path in paths:
    source=(root/path).read_text()
    assert "doctrine/inChatOniRecoveryV1.json" in source, path
builders=(root/"agents/buildOnis/SKILL.md").read_text()
lum=(root/"agents/lum/SKILL.md").read_text()
assert "Only when an exact CAST packet" in builders
assert "No CAST means source-only tests" in lum
assert "Run Tetsu and Kaji in parallel when dual-build evidence is required." not in builders
print("GREEN_IN_CHAT_ONI_RECOVERY_SOURCE_ONLY")
