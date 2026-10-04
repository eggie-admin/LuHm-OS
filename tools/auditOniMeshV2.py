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
    "idempotencyKey", "writerLease", "evidencePolicy",
}

REQUIRED_EVIDENCE = {
    "kind", "locator", "sourceRef", "observedAt", "freshnessClass", "status",
}

REQUIRED_LEASE = {
    "leaseId", "taskId", "repository", "sourceRef", "candidateRef", "holder", "scope",
}

REQUIRED_OUTPUT = {
    "taskId", "worker", "sourceRef", "scope", "status", "facts",
    "evidenceRefs", "uncertainties", "proposedNextActions", "authorityNeeded",
    "budgetUsed", "capabilitiesUsed", "deniedCapabilityAttempts", "errors",
    "evidenceFreshness", "idempotencyKey", "writerLeaseId", "mutationResultIdentity",
}

MUTATION_AUTHORITIES = {"MUTATE_REVERSIBLE", "MUTATE_BUILD_AFFECTING", "RELEASE_SIGNING", "PUBLIC_EXPOSURE"}


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
    require(topo["oneWriterLeaseRequired"] is True, "one-writer lease disabled")

    require(set(data["requiredTaskEnvelope"]) == REQUIRED_ENVELOPE, "task envelope contract drift")
    require(set(data["writerLeaseRequiredFields"]) == REQUIRED_LEASE, "writer lease contract drift")
    require(set(data["evidencePolicy"]["requiredEvidenceFields"]) == REQUIRED_EVIDENCE, "evidence record contract drift")
    require(set(data["requiredOutputPacket"]) == REQUIRED_OUTPUT, "output packet contract drift")
    require(data["statePrecedence"] == ["ERROR", "RED", "UNKNOWN", "AMBER", "GREEN"], "evidence precedence drift")

    firewall = data["capabilityFirewall"]
    require(firewall["defaultDeny"] is True, "capability firewall is not default-deny")
    require(firewall["noTaskInheritance"] is True, "capabilities may leak across tasks")
    require(firewall["noHistoryInheritance"] is True, "chat/history may grant capabilities")
    require(firewall["noRoleplayInheritance"] is True, "roleplay may grant capabilities")
    for forbidden in ("secret.read", "shell.arbitrary", "network.publicBind", "release.productionSign", "release.publish", "git.forceUpdate", "git.branchDelete", "git.historyRewrite", "policy.selfMutate", "crown.selfApprove"):
        require(forbidden in firewall["hardDeny"], f"missing hard deny: {forbidden}")

    ceilings = data["budgetCeilings"]
    require(ceilings["maxToolCalls"] <= 20, "tool-call ceiling too high")
    require(ceilings["maxMutations"] == 1, "ordinary mutation ceiling must remain one")
    require(ceilings["maxRetries"] <= 1, "retry ceiling too high")
    require(ceilings["maxRuntimeSeconds"] <= 900, "runtime budget too high")
    require(ceilings["maxDelegationDepth"] == 0, "helper delegation depth must remain zero")

    mutation = data["mutationPolicy"]
    require(mutation["exactSourceRefRequired"] is True, "mutation source identity not required")
    require(mutation["unknownSourceMayMutate"] is False, "UNKNOWN source may mutate")
    require(mutation["idempotencyKeyRequired"] is True, "mutation idempotency disabled")
    require(mutation["writerLeaseRequired"] is True, "mutation writer lease disabled")
    require(mutation["ambiguousMutationState"] == "STOP", "ambiguous mutation state does not stop")
    require(mutation["ordinaryTaskMutationMax"] == 1, "ordinary mutation batch widened")
    require(mutation["postconditionReceiptRequired"] is True, "mutation postcondition receipt disabled")

    evidence = data["evidencePolicy"]
    require(evidence["exactSourceBinding"] is True, "evidence source binding disabled")
    require(evidence["contradictionBlocksGreen"] is True, "contradiction may pass GREEN")
    require(evidence["staleLiveEvidenceCanPromote"] is False, "stale live evidence may promote")
    require(evidence["defaultMaxLiveEvidenceAgeHours"] <= 24, "live evidence freshness window too broad")

    require(data["retryPolicy"]["blindMutationRetry"] is False, "blind mutation retry enabled")
    require(data["retryPolicy"]["identicalTransientRetryMax"] <= 1, "retry budget too high")
    require(data["retryPolicy"]["retryRequiresSameIdempotencyKey"] is True, "retry may change idempotency key")
    require(data["retryPolicy"]["retryRequiresKnownNoPartialMutation"] is True, "retry may ignore partial mutation")

    require(data["contradictionPolicy"]["stopMutation"] is True, "contradiction does not stop mutation")
    require(set(data["contradictionPolicy"]["routeTo"]) == {"Shiori", "DrNao"}, "contradiction routing drift")

    require(data["learning"]["hiddenRetraining"] is False, "hidden retraining enabled")
    require(data["learning"]["silentPolicyMutation"] is False, "silent policy mutation enabled")
    require(data["learning"]["lessonMayGrantCapability"] is False, "lessons may grant capability")
    require(data["learning"]["lessonMayIncreaseBudget"] is False, "lessons may increase budget")
    require(data["learning"]["lessonMayOverrideStop"] is False, "lessons may override stop rules")
    return data


def resolve_capabilities(data: dict, role: str, allowed: list[str], forbidden: list[str]) -> set[str]:
    role_ceiling = set(data["roleCapabilityCeilings"].get(role, []))
    hard_deny = set(data["capabilityFirewall"]["hardDeny"])
    return (set(allowed) & role_ceiling) - set(forbidden) - hard_deny


def validate_task_envelope(data: dict, envelope: dict, role: str) -> None:
    missing = REQUIRED_ENVELOPE - set(envelope)
    require(not missing, f"task envelope missing fields: {sorted(missing)}")
    require(envelope["authorityClass"] in data["authorityClasses"], "unknown authority class")
    require(isinstance(envelope["allowedCapabilities"], list), "allowedCapabilities must be list")
    require(isinstance(envelope["forbiddenCapabilities"], list), "forbiddenCapabilities must be list")
    hard_deny = set(data["capabilityFirewall"]["hardDeny"])
    require(not (set(envelope["allowedCapabilities"]) & hard_deny), "hard-denied capability requested as allowed")

    budget = envelope["budget"]
    for key, ceiling in data["budgetCeilings"].items():
        require(key in budget, f"budget missing {key}")
        require(isinstance(budget[key], int) and budget[key] >= 0, f"invalid budget {key}")
        require(budget[key] <= ceiling, f"budget exceeds ceiling: {key}")

    if envelope["authorityClass"] in MUTATION_AUTHORITIES:
        require(envelope["sourceRef"] not in (None, "", "UNKNOWN"), "mutation requires exact sourceRef")
        require(bool(envelope["idempotencyKey"]), "mutation requires idempotency key")
        require(isinstance(envelope["writerLease"], dict), "mutation requires writer lease")
        require(REQUIRED_LEASE <= set(envelope["writerLease"]), "writer lease missing fields")
        lease = envelope["writerLease"]
        require(lease["taskId"] == envelope["taskId"], "writer lease task mismatch")
        require(lease["repository"] == envelope["repository"], "writer lease repository mismatch")
        require(lease["sourceRef"] == envelope["sourceRef"], "writer lease source mismatch")
        require(lease["holder"] == role, "writer lease holder mismatch")
        require(budget["maxMutations"] == 1, "mutation task must be one atomic mutation")
    else:
        require(budget["maxMutations"] == 0, "read/plan task may not reserve mutations")


def evidence_eligible(data: dict, evidence: dict, source_ref: str, live_age_hours: int | None = None) -> bool:
    if not REQUIRED_EVIDENCE <= set(evidence):
        return False
    if evidence["sourceRef"] != source_ref:
        return False
    if evidence["status"] in ("ERROR", "RED", "UNKNOWN"):
        return False
    freshness = evidence["freshnessClass"]
    if freshness not in data["evidencePolicy"]["freshnessClasses"]:
        return False
    if freshness == "LIVE":
        if live_age_hours is None:
            return False
        if live_age_hours > data["evidencePolicy"]["defaultMaxLiveEvidenceAgeHours"]:
            return False
    return True


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

    protocol = PROTOCOL.read_text(encoding="utf-8")
    for phrase in (
        "Capabilities are **deny by default**",
        "UNKNOWN_MUTATION_STATE",
        "one active writer lease",
        "Conflicting evidence blocks GREEN",
        "No agent may choose the more convenient receipt",
    ):
        require(phrase in protocol, f"protocol hardening missing: {phrase}")


def main() -> None:
    data = load()
    audit_skills(data)
    print("ONI MESH V2 HARDENED CONTROL PLANE GREEN")
    print(json.dumps({
        "schema": data["schema"],
        "boss": data["boss"],
        "defaultDeny": data["capabilityFirewall"]["defaultDeny"],
        "maxParallelSupportWorkers": data["topology"]["maxParallelSupportWorkers"],
        "maxMutableSourceLanesPerCandidate": data["topology"]["maxMutableSourceLanesPerCandidate"],
        "maxMutationsPerTask": data["budgetCeilings"]["maxMutations"],
        "maxRetries": data["budgetCeilings"]["maxRetries"],
        "skillCountAudited": len(SKILLS),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
