#!/usr/bin/env python3
"""Verify the live-in-chat Goddess release without falsifying runtime clearance."""
from __future__ import annotations
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf8"))

def audit(p):
    errors = []
    def need(ok, key):
        if not ok: errors.append(key)
    legacy = load("doctrine/supervisedChatCastReleaseV1.json")
    company = load("doctrine/companyWideOperationalQuarantineV1.json")
    belldandy = load("doctrine/belldandyOperationalQuarantineV1.json")
    roster = load("doctrine/agentSystemDeploymentV1.json")
    need(p.get("schema") == "luhmOs.goddessCabinetLiveChat.v1", "schema")
    need(p.get("scope") == "interactiveChatCollaborationOnly", "scope")
    need(p.get("status") == "PROFESSOR_AUTHORIZED_SUPERVISED_CHAT_CAST", "approval")
    need(p.get("authority") == "Professor", "authority")
    need(legacy.get("state") == "RELEASED", "legacyCast")
    need(company.get("state") == "QUARANTINED" and not company.get("activeTaskWorkersAllowed"), "companyHold")
    need(belldandy.get("state") == "QUARANTINED", "belldandyHold")
    need(company.get("registeredAgents") == roster.get("requiredAgents"), "sourceRoster")
    ids = [x["id"] for x in p.get("alwaysReadyCabinet", [])]
    need(ids == ["lum", "urdDoctorGoddess", "belldandySecretary", "skuldResearch", "yume"], "alwaysReady")
    complete = ids + p.get("specialistRosterIds", [])
    need(len(complete) == 15 and len(set(complete)) == 15 and
         set(complete) == set(roster["requiredAgents"]), "fullCast")
    a = p.get("activation", {})
    for k in ("all15NamesUsableInChat", "perRequestMinimalSpecialists",
              "noHiddenAsync", "mayUseActuallyConnectedToolsAsChatGPTAssistant",
              "toolResultsProvenOnlyIfObserved", "doNotClaimNamedIndependentServiceCalled"):
        need(a.get(k) is True, "chat:" + k)
    for k in ("actualIndependentWorkersStarted", "autoRunExternalActions"):
        need(a.get(k) is False, "runtime:" + k)
    h = p.get("persistedQuarantine", {})
    need(h.get("backendCompany") == "QUARANTINED", "backendHold")
    need(h.get("belldandyWorker") == "QUARANTINED", "belldandyExecutionHold")
    need(h.get("previousMissingHostProofCannotBeInvented") is True, "hostEvidence")
    need(len(h.get("requiredToChangeBackend", [])) == 5, "receiptGates")
    for k in ("privateRebelOriginalsStayInRestrictedDrive", "sourceAndSanitizedReceiptsStayInGithub",
              "noUnapprovedDonorPublicExposure", "noCloudflareChange", "noApiOrBillingAutoSpend",
              "noProductionSigningOrAutomaticPublication", "noPermissionsBroadening"):
        need(p.get("assetAndRelease", {}).get(k) is True, "asset:" + k)
    need(p.get("crown", {}).get("supervisedChatCast") == "AUTHORIZED", "cast")
    need(p.get("crown", {}).get("autonomousWorkers") == "STOP_UNTIL_INDEPENDENT_RECEIPTS", "workers")
    need(p.get("crown", {}).get("publicRelease") == "STOP_UNTIL_RELEASE_GATES", "public")
    for name in p.get("sourceContracts", []):
        need((ROOT / name).is_file(), "missing:" + name)
    return errors

def main():
    p = load("doctrine/goddessCabinetLiveChatV1.json")
    assert not audit(p), audit(p)
    controls = [
        ("fakeWorker", lambda x: x["activation"].update(actualIndependentWorkersStarted=True)),
        ("falseUnquarantine", lambda x: x["persistedQuarantine"].update(backendCompany="RELEASED")),
        ("falseBelldandy", lambda x: x["persistedQuarantine"].update(belldandyWorker="RELEASED")),
        ("falseCrown", lambda x: x["crown"].update(autonomousWorkers="GREEN")),
        ("missingUrd", lambda x: x["alwaysReadyCabinet"].pop(1)),
        ("unsecuredArt", lambda x: x["assetAndRelease"].update(noUnapprovedDonorPublicExposure=False)),
        ("hiddenWorker", lambda x: x["activation"].update(noHiddenAsync=False)),
    ]
    for label, mutate in controls:
        changed = copy.deepcopy(p)
        mutate(changed)
        assert audit(changed), "FALSE_GREEN:" + label
    print("GREEN_FULL_GODDESS_CHAT_CAST_15_IDENTITIES_7_NEGATIVE_CONTROLS")
    print("BACKEND_EXECUTION_HELD_PENDING_CHATGPT_HOST_AND_URD_PROOF")

if __name__ == "__main__":
    main()
