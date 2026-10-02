#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(".")
d=json.loads((root/"doctrine/tourniquetWorkflowV1.json").read_text())
required=[
 "agents/tourniquetWorkflow/SKILL.md","agents/witchingHourCoding/SKILL.md",
 "agents/goddessSharedSystemsPractice/SKILL.md","agents/lum/SKILL.md",
 "agents/kugiToolOni/SKILL.md","agents/urdMutationOni/SKILL.md",
 "agents/shioriCriticOni/SKILL.md","agents/belldandyQualityOni/SKILL.md"
]
for p in required: assert (root/p).is_file(), "RED_AGENT_SKILL_MISSING:"+p
assert d["authority"]=="Professor"
assert d["purpose"]=="failClosedMutationClamp"
assert d["limits"]["maxParallelism"]<=3
for k in ("recursiveRecruitment","selfApproval","implicitCrown","unknownToGreen","weakenEvidenceToPass","broadenScopeDuringRepair"):
    assert d["limits"][k] is False, "RED_TOURNIQUET_AUTHORITY_LEAK:"+k
assert d["greenAction"]=="reingestCurrentTruthAndContinue"
assert d["redAction"]=="rollbackOrNearestEvidenceBackedKnownGood"
assert d["consequentialPromotion"]=="ProfessorCrownOnly"
tour=(root/"agents/tourniquetWorkflow/SKILL.md").read_text()
for term in ("exact sourceRef","Witching Hour","Kugi","Urd","Belldandy","Shiori","Professor Crown"):
    assert term in tour, "RED_TOURNIQUET_SKILL_DRIFT:"+term
witch=(root/"agents/witchingHourCoding/SKILL.md").read_text()
for term in ("exact sourceRef","Urd","Belldandy","Shiori","Kugi","nearest evidence-backed known-good"):
    assert term in witch, "RED_WITCHING_HOUR_DRIFT:"+term
protocol=root/"agents/shared/ONI_PROTOCOL_V2.md"
assert protocol.is_file(), "RED_ONI_PROTOCOL_MISSING"
proto=protocol.read_text()
for term in ("authority","evidence"):
    assert term.lower() in proto.lower(), "RED_ONI_PROTOCOL_DRIFT:"+term
kugi=(root/"agents/kugiToolOni/SKILL.md").read_text()
for term in ("deterministic","authorized","does not reinterpret","GREEN"):
    assert term in kugi, "RED_KUGI_AUTHORITY_DRIFT:"+term
lum=(root/"agents/lum/SKILL.md").read_text()
assert "Consequential boundary" in lum, "RED_LUM_CROWN_BOUNDARY"
print("TOURNIQUET AGENT LOGIC GREEN")
