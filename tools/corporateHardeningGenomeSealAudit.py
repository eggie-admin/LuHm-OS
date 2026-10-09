#!/usr/bin/env python3
import json
from pathlib import Path

rootPath = Path(__file__).resolve().parents[1]
errors = []

def need(conditionValue, messageValue):
    if not conditionValue:
        errors.append(messageValue)

receipt = json.loads((rootPath / "doctrine/corporateHardeningCrownReceiptV1.json").read_text(encoding="utf-8"))
semantic = json.loads((rootPath / "doctrine/semanticDomainHardeningV1.json").read_text(encoding="utf-8"))
pki = json.loads((rootPath / "doctrine/belldandyPkiCorporateSecretaryV1.json").read_text(encoding="utf-8"))
corporate = json.loads((rootPath / "doctrine/corporateEscalationProfileV1.json").read_text(encoding="utf-8"))
sourceTruth = json.loads((rootPath / "doctrine/currentSourceTruthV3.json").read_text(encoding="utf-8"))

approvedHead = "9a00fd4ecac1e1af3302ff8c3e05524bf6b55020"
approvedTree = "7d4d0cfbe01831c83446ff390cddc564f1fa7dbd"
mergedMain = "3471f78188410761c84a892101ba163a3052be13"

approval = receipt.get("approvalBasis", {})
need(receipt.get("authority") == "Professor", "Crown receipt authority drift")
need(receipt.get("scopeId") == "corporateSemanticPkiHardeningMilestone", "Crown receipt scope drift")
need(approval.get("professorCrownApproval") is True, "Professor Crown approval missing")
need(approval.get("approvedCandidateSourceRef") == approvedHead, "approved candidate ref drift")
need(approval.get("approvedTreeRef") == approvedTree, "approved tree drift")
need(approval.get("mergedMainRef") == mergedMain, "merged main ref drift")
need(approval.get("mergedMainTreeRef") == approvedTree, "merged main tree drift")
need(approval.get("mergedTreeMatchesApprovedCandidate") is True, "tree equivalence receipt missing")
need(approval.get("exactHeadWorkflowsGreen") is True, "exact-head GREEN receipt missing")
need(approval.get("mainPushWorkflowsGreen") is True, "main-push GREEN receipt missing")
need(receipt.get("automaticFuturePromotion") is False, "future promotion became automatic")

for docName, docValue, expectedStatus in (
    ("semantic", semantic, "CANONICAL_SEMANTIC_SOURCE"),
    ("pki", pki, "CANONICAL_PKI_SECRETARY_SOURCE"),
):
    need(docValue.get("status") == expectedStatus, f"{docName} canonical status drift")
    need(docValue.get("promotion") is True, f"{docName} promotion flag missing")
    need(docValue.get("professorApproval") is True, f"{docName} Professor approval missing")
    need(docValue.get("crownReceipt") == "doctrine/corporateHardeningCrownReceiptV1.json", f"{docName} Crown receipt pointer drift")
    need(docValue.get("approvedCandidateSourceRef") == approvedHead, f"{docName} approved source drift")
    need(docValue.get("mergedMainRef") == mergedMain, f"{docName} merged-main ref drift")
    need(docValue.get("crownStatus") == "CROWNED_SOURCE_MILESTONE", f"{docName} Crown status drift")

route = ["lum", "urdDoctorGoddess", "belldandySecretary", "skuldResearch", "lum"]
caseEscalation = corporate.get("cabinetCaseEscalation", {})
need(caseEscalation.get("route") == route, "cabinet route drift")
need(caseEscalation.get("authorityHierarchy") is False, "cabinet route became authority hierarchy")
casePromotion = caseEscalation.get("promotion", {})
need(casePromotion.get("status") == "CROWNED_SOURCE_MILESTONE", "cabinet route promotion missing")
need(casePromotion.get("crownReceipt") == "doctrine/corporateHardeningCrownReceiptV1.json", "cabinet route receipt pointer drift")

hardening = sourceTruth.get("corporateHardening", {})
need(hardening.get("status") == "CROWNED_SOURCE_MILESTONE", "current source truth hardening status drift")
need(hardening.get("semanticBoundary") == "doctrine/semanticDomainHardeningV1.json", "semantic pointer missing")
need(hardening.get("pkiSecretary") == "doctrine/belldandyPkiCorporateSecretaryV1.json", "PKI pointer missing")
need(hardening.get("corporateEscalation") == "doctrine/corporateEscalationProfileV1.json#cabinetCaseEscalation", "corporate escalation pointer missing")
need(hardening.get("crownReceipt") == "doctrine/corporateHardeningCrownReceiptV1.json", "source truth Crown receipt pointer missing")
need(hardening.get("cabinetRoute") == route, "source truth cabinet route drift")
need(hardening.get("liveInfrastructureMutationIncluded") is False, "source truth incorrectly includes live infrastructure mutation")
need(hardening.get("futurePromotionAutomatic") is False, "source truth incorrectly allows future automatic promotion")

need(sourceTruth.get("agentLayer", {}).get("semanticDomainHardening") == "doctrine/semanticDomainHardeningV1.json", "agentLayer semantic pointer missing")
need(sourceTruth.get("agentLayer", {}).get("belldandyPkiCorporateSecretary") == "doctrine/belldandyPkiCorporateSecretaryV1.json", "agentLayer PKI pointer missing")

for forbiddenPromotion in (
    "live DNS mutation",
    "certificate issuance",
    "certificate revocation",
    "secret rotation",
    "token rotation",
    "public deployment",
    "production signing",
):
    need(forbiddenPromotion in receipt.get("notPromoted", []), f"receipt missing non-promotion boundary: {forbiddenPromotion}")

need(pki.get("liveMutation", {}).get("certificateIssuance") is False, "PKI doctrine grants certificate issuance")
need(pki.get("liveMutation", {}).get("dnsChange") is False, "PKI doctrine grants DNS mutation")
need(pki.get("liveMutation", {}).get("secretRotation") is False, "PKI doctrine grants secret rotation")
need(pki.get("pkiMaterial", {}).get("privateKeyContentsMayBeReadByAudit") is not True, "private-key audit read unexpectedly enabled")

print(json.dumps({
    "schema": "luhmOs.corporateHardeningGenomeSealAudit.v1",
    "status": "GREEN_CORPORATE_HARDENING_GENOME_SEAL" if not errors else "RED_CORPORATE_HARDENING_GENOME_SEAL",
    "errors": errors,
    "authorityExpansion": False,
    "liveInfrastructureMutation": False,
    "futureAutomaticPromotion": False,
    "crownStatus": "STOP"
}, indent=2))
raise SystemExit(1 if errors else 0)
