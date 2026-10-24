#!/usr/bin/env python3
"""Professor-approved Canary milestone and private-media boundary regression.

Tests source truth and sanitized receipts only; public CI never copies the video.
"""
from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def audit(truth, receipt, milestones):
    problems = []
    def require(ok, name):
        if not ok:
            problems.append(name)

    link = truth.get("chromeCanaryKioskCurrentMilestone", {})
    require(truth.get("schema") == "luhmOs.currentSourceTruth.v3", "sourceSchema")
    require(truth.get("status") == "AMBER_PROPOSED_SEAL_OF_TRUTH", "globalSourcePromotion")
    require(link.get("contract") == "doctrine/chromeCanaryKioskMilestonesV1.json", "missingMilestoneLink")
    require(link.get("deviceEvidence") == "doctrine/chromeCanaryDeviceProof20261024V1.json", "missingReceiptLink")
    require(link.get("professorApprovedContinuation") is True, "professorApproval")
    require(link.get("chatGptAndroidInlineMount") == "RED_OBSERVED", "falseHostGreen")
    require(link.get("finalProductCrown") == "NOT_GRANTED", "falseProductCrown")

    require(receipt.get("schema") == "luhmOs.chromeCanaryDeviceProof.v1", "receiptSchema")
    require(receipt.get("professorApproval") is True, "receiptApproval")
    require(receipt.get("crownStatus") == "CROWNED_SCOPED_CANARY_DEVICE_EVIDENCE", "receiptCrownScope")
    require(receipt.get("rawVideoPublished") is False and receipt.get("rawScreenshotPublished") is False,
            "privateMediaPublication")
    digest = receipt.get("privateVideo", {}).get("sha256", "")
    require(bool(re.fullmatch("[0-9a-f]{64}", digest)), "invalidVideoDigest")
    require(receipt.get("privateVideo", {}).get("sourceCommitVisiblyInVideo") is False,
            "inferredVideoCommit")
    require(receipt.get("canaryStandalone", {}).get("status") == "GREEN_SCOPED_DEVICE_TOUCH",
            "missingTouchEvidence")
    blocked = receipt.get("blocked", {})
    require(blocked.get("chatGptInlineWidget") == "RED_OBSERVED", "falseClientMount")
    require(blocked.get("musicPlayback") == "RED_INVALID_URL", "falseMusicPlayback")
    require(blocked.get("godotExportOnObservedOrigin") == "NOT_STAGED", "falseGodotGameplay")
    require(blocked.get("secureKioskLock") == "UNVERIFIED", "falseLockTaskProof")
    require(receipt.get("mcpServer", {}).get("clientIframeMount") == "RED_OBSERVED",
            "mcpTransportClaimedAsMount")
    require(receipt.get("fullProductCrown") == "NOT_GRANTED_BY_THIS_EVIDENCE",
            "falseFullProductCrown")

    require(milestones.get("schema") == "luhmOs.chromeCanaryKioskMilestones.v1", "milestonesSchema")
    require(milestones.get("professorApprovedContinuation") is True, "milestonesAuthority")
    require(milestones.get("status") == "ACTIVE_CONTINUOUS_AMBER_REPAIR", "amberStop")
    require(milestones.get("deviceReceipt") == link.get("deviceEvidence"), "milestonesReceiptDrift")
    require("AMBER_CONTINUES" in milestones.get("promotionRule", ""), "amberMustContinue")
    rows = {row.get("id"): row for row in milestones.get("stages", [])}
    require(len(rows) == len(milestones.get("stages", [])) and len(rows) == 10, "milestoneInventory")
    require(rows.get("physicalChromeCanaryStandalone", {}).get("state") == "GREEN_SCOPED", "standaloneRed")
    require(rows.get("chatGptAndroidInlineWidget", {}).get("state") == "RED_OBSERVED", "clientFalseGreen")
    require(rows.get("musicDeckPlayback", {}).get("state") == "RED_OBSERVED", "musicFalseGreen")
    require(rows.get("godotEmbeddedGameplay", {}).get("state") == "AMBER_NOT_STAGED", "godotFalseGreen")
    require(rows.get("managedDeviceKiosk", {}).get("state") == "UNVERIFIED", "lockFalseGreen")
    require(rows.get("publicAndStableDistribution", {}).get("state") == "NOT_APPROVED", "releaseFalseGreen")
    govern = milestones.get("governance", {})
    require(govern.get("noPublicUserRecording") is True and govern.get("noNewPaidServices") is True,
            "privacyOrSpend")
    require(govern.get("companyAgentQuarantine") == "QUARANTINED", "agentUnquarantine")
    require(milestones.get("productCrown") == "NOT_YET_PROVEN", "finalCrownFalsePositive")
    return problems


class CanaryDeviceMilestoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.truth = load("doctrine/currentSourceTruthV3.json")
        cls.receipt = load("doctrine/chromeCanaryDeviceProof20261024V1.json")
        cls.milestones = load("doctrine/chromeCanaryKioskMilestonesV1.json")

    def test_current_records_pass(self):
        self.assertEqual(audit(self.truth, self.receipt, self.milestones), [])

    def test_reject_false_inline_green(self):
        m = copy.deepcopy(self.milestones)
        for stage in m["stages"]:
            if stage["id"] == "chatGptAndroidInlineWidget":
                stage["state"] = "GREEN"
        self.assertIn("clientFalseGreen", audit(self.truth, self.receipt, m))

    def test_reject_private_video_publication(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["rawVideoPublished"] = True
        self.assertIn("privateMediaPublication", audit(self.truth, receipt, self.milestones))

    def test_reject_false_product_crown(self):
        truth = copy.deepcopy(self.truth)
        truth["chromeCanaryKioskCurrentMilestone"]["finalProductCrown"] = "GREEN"
        self.assertIn("falseProductCrown", audit(truth, self.receipt, self.milestones))

    def test_reject_unapproved_paid_resource(self):
        m = copy.deepcopy(self.milestones)
        m["governance"]["noNewPaidServices"] = False
        self.assertIn("privacyOrSpend", audit(self.truth, self.receipt, m))

    def test_reject_mismatched_video_digest(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["privateVideo"]["sha256"] = "bad"
        self.assertIn("invalidVideoDigest", audit(self.truth, receipt, self.milestones))


if __name__ == "__main__":
    unittest.main()
