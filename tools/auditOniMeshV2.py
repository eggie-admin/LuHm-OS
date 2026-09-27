#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine" / "ONI_MESH_CONTROL_PLANE_V2.json"
PROTOCOL = ROOT / "agents" / "shared" / "ONI_PROTOCOL_V2.md"

SKILLS = {
    "Lum": ROOT / "agents" / "lum" / "SKILL.md",
    "Kiri": ROOT / "agents" / "kiriContextOni" / "SKILL.md",
    "TetsuKaji": ROOT / "agents" / "buildOnis" / "SKILL.md",
    "Momo": ROOT / "agents" / "momoResearchOni" / "SKILL.md",
    "Shiori": ROOT / "agents" / "shioriCriticOni" / "SKILL.md",
    "DrNao": ROOT / "agents" / "doctorOni" / "SKILL.md",
    "Kugi": ROOT / "agents" / "kugiToolExecutor" / "SKILL.md",
    "Fumi": ROOT / "agents" / "fumiSecretaryOni" / "SKILL.md",
    "Sumi": ROOT / "agents" / "sumiAssetOni" / "SKILL.md",
    "Koe": ROOT / "agents" / "koeDictationOni" / "SKILL.md",
    "Yume": ROOT / "agents" / "yumeArtOni" / "SKILL.md",
}

REQUIRED_ENVELOPE = {
    "taskId", "intent", "scope", "repository", "sourceRef",
    "authorityClass", "allowedCapabilities", "forbiddenCapabilities",
    "evidenceRefs", "requiredOutputs", "stopConditions", "budget",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load() -> dict:
    require(DOCTRINE.is_file(), "missing mesh doctrine")
    require(PROTOCOL.is_file(), "missing shared Oni protocol")
    data = json.loads(DOCTRINE.read_text(encoding="utf-8"))
    require(data["schema"] == "luhm-os.oni-mesh-control-plane.v2", "wrong doctrine schema")
    require(data["boss"] == "Lum", "Lum must remain sole boss")
    require(data["humanAuthority"] == "Professor", "human Crown authority changed")
    topo = data["topology"]
    require(topo["helperRecruitment"] is False, "helpers may not recruit helpers")
    require(topo["maxParallelSupportWorkers"] <= 3, "parallel support budget exceeded")
    require(topo["maxMutableSourceLanesPerCandidate"] == 1, "multiple mutable source lanes enabled")
    require(topo["directQuestionBypassesMesh"] is True, "simple direct questions must bypass mesh")
    require(set(data["requiredTaskEnvelope"]) == REQUIRED_ENVELOPE, "task envelope contract drift")
    require(data["statePrecedence"] == ["ERROR", "RED", "UNKNOWN", "AMBER", "GREEN"], "evidence precedence drift")
    require(data["retryPolicy"]["blindMutationRetry"] is False, "blind mutation retry enabled")
    require(data["retryPolicy"]["identicalTransientRetryMax"] <= 1, "retry budget too high")
    require(data["learning"]["hiddenRetraining"] is False, "hidden retraining enabled")
    require(data["learning"]["silentPolicyMutation"] is False, "silent policy mutation enabled")
    return data


def audit_skills(data: dict) -> None:
    protocol_ref = "agents/shared/ONI_PROTOCOL_V2.md"
    for role, path in SKILLS.items():
        require(path.is_file(), f"missing skill: {role}: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        require(protocol_ref in text, f"{role} is not bound to shared protocol")
        require("recruit helpers" not in text.lower() or "never" in text.lower() or "does not" in text.lower(), f"{role} may imply helper recruitment")

    roles = data["roles"]
    require(roles["Lum"]["kind"] == "boss-router-integrator", "Lum role drift")
    require(roles["Lum"]["mutationAuthority"] is False, "Lum gained direct mutation authority")
    require(roles["Kugi"]["kind"] == "deterministic-tool-executor", "Kugi executor role drift")
    require(roles["Fumi"]["defaultAuthority"] == "READ_ONLY", "Fumi authority creep")
    require(roles["DrNao"]["defaultAuthority"] == "READ_ONLY", "Dr Nao authority creep")

    lum = SKILLS["Lum"].read_text(encoding="utf-8")
    for state in ("INTAKE", "RESOLVE", "ROUTE", "OBSERVE", "VERIFY", "ADJUDICATE", "REPORT", "CROWN_STOP"):
        require(f"`{state}`" in lum, f"Lum state machine missing {state}")
    require("Kugi" in lum and "Dr. Nao" in lum and "Fumi" in lum, "Lum routing table incomplete")

    kugi = SKILLS["Kugi"].read_text(encoding="utf-8")
    require("UNKNOWN_MUTATION_STATE" in kugi, "Kugi ambiguous mutation stop missing")
    require("Never blindly repeat" in kugi, "Kugi blind retry guard missing")

    doctor = SKILLS["DrNao"].read_text(encoding="utf-8").lower()
    require("physical-device" in doctor, "Dr Nao device-proof boundary missing")
    require("policy drift" in doctor or "policy-drift" in doctor, "Dr Nao policy-drift adjudication missing")


def main() -> None:
    data = load()
    audit_skills(data)
    print("ONI MESH V2 CONTROL PLANE GREEN")
    print(json.dumps({
        "schema": data["schema"],
        "boss": data["boss"],
        "maxParallelSupportWorkers": data["topology"]["maxParallelSupportWorkers"],
        "helperRecruitment": data["topology"]["helperRecruitment"],
        "maxMutableSourceLanesPerCandidate": data["topology"]["maxMutableSourceLanesPerCandidate"],
        "skillCountAudited": len(SKILLS),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
