"""Negative controls for source drift and managed certificate-path inspection."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from networkSpineAudit import audit
from certbotWorkspaceSymlinkAudit import inspectPaths

rootPath = Path(__file__).resolve().parents[1]


class NetworkSpineTests(unittest.TestCase):
    def setUp(self):
        self.tempValue = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempValue.cleanup)
        self.rootValue = Path(self.tempValue.name)
        for pathValue in ("doctrine/networkSpineV1.json", "doctrine/cloudflareAirTrafficControllerV1.json", "doctrine/belldandyPkiCorporateSecretaryV1.json", "doctrine/currentSourceTruthV3.json", "doctrine/activeRepositorySetV1.json", "agents/belldandyQualityOni/SKILL.md", "agents/urdMutationOni/SKILL.md"):
            targetValue = self.rootValue / pathValue
            targetValue.parent.mkdir(parents=True, exist_ok=True)
            targetValue.write_text((rootPath / pathValue).read_text())
        self.docValue = json.loads((self.rootValue / "doctrine/networkSpineV1.json").read_text())

    def saveDoc(self):
        (self.rootValue / "doctrine/networkSpineV1.json").write_text(json.dumps(self.docValue))

    def testCurrentSourcePassesOnlySourceScope(self):
        resultValue = audit(self.rootValue)
        self.assertEqual(resultValue["errors"], [])
        self.assertFalse(resultValue["runtimeProven"])
        self.assertFalse(resultValue["milestoneCompletion"])

    def testDangerousProxyFlagsRejected(self):
        for keyValue in ("allowForwardProxy", "trustClientForwardedHeaders", "serveRepositoryRoot", "exposeShellOrSqlAdmin", "symlinksGrantAccess"):
            with self.subTest(keyValue=keyValue):
                originalValue = copy.deepcopy(self.docValue)
                self.docValue["reverseProxy"][keyValue] = True
                self.saveDoc()
                self.assertTrue(audit(self.rootValue)["errors"])
                self.docValue = originalValue

    def testRuntimeAndTlsFalseClaimsRejected(self):
        for pathValue, value in ((("runtimeProofFromStaticCi",), True), (("runtimeState",), "GREEN"), (("tls", "noTlsVerify"), True), (("tls", "tunnelOriginValidation"), "edgeModeOnly"), (("hostIdentity", "runtimeReceiptRequired"), False)):
            with self.subTest(pathValue=pathValue):
                originalValue = copy.deepcopy(self.docValue)
                targetValue = self.docValue
                for keyValue in pathValue[:-1]:
                    targetValue = targetValue[keyValue]
                targetValue[pathValue[-1]] = value
                self.saveDoc()
                self.assertTrue(audit(self.rootValue)["errors"])
                self.docValue = originalValue

    def testLaneDirectionAndHostnameDriftRejected(self):
        self.docValue["lanes"]["systemPortal"]["requestPath"].reverse()
        self.docValue["lanes"]["systemPortal"]["fqdn"] = "wrong.example.com"
        self.saveDoc()
        self.assertTrue(audit(self.rootValue)["errors"])

    def testReverseFqdnNamespaceCannotBecomeDnsOrPtr(self):
        for keyValue in ("isDnsRecord", "isPtrRecord", "wildcardTldIsPublicDns", "mayGrantNetworkOrExecutionAuthority"):
            with self.subTest(keyValue=keyValue):
                originalValue = copy.deepcopy(self.docValue)
                self.docValue["identityChain"]["reverseFqdnNamespace"][keyValue] = True
                self.saveDoc()
                self.assertTrue(audit(self.rootValue)["errors"])
                self.docValue = originalValue

    def testRemoteSourceIdentitySeparatesForwardRouteAndReverseNamespace(self):
        resultValue = audit(self.rootValue)
        self.assertEqual(resultValue["errors"], [])
        identityValue = self.docValue["identityChain"]["canonicalRepository"]["remoteSourceIdentity"]
        self.assertEqual(identityValue["identity"], "art.eggiebagelface.mcp.LuHm-OS")
        self.assertEqual(identityValue["forwardHttpsFqdn"], "mcp.eggiebagelface.art")
        self.assertFalse(identityValue["wildcardSortingPatternIsLiteralDns"])
        self.assertFalse(identityValue["isDnsRecord"])
        self.assertFalse(identityValue["isPtrRecord"])
        self.assertEqual(identityValue["cloudflareProxy"], "disabledUntilSeparateStreamingProof")

    def testDirectoryPullAndForwardDnsContracts(self):
        identityValue = self.docValue["identityChain"]["canonicalRepository"]["remoteSourceIdentity"]
        pullValue = identityValue["directoryPullLocator"]
        self.assertEqual(pullValue["components"], ["repository", "ref", "path", "commitSha"])
        self.assertFalse(pullValue["maySubstituteForGitHubRefPathOrCommit"])
        dnsValue = identityValue["forwardDns"]
        self.assertEqual(dnsValue["recordType"], "CNAME")
        self.assertEqual(dnsValue["targetCandidate"], "luhm-os-harness-green.onrender.com")
        self.assertEqual(dnsValue["proxy"], "DNS_ONLY")
        self.assertEqual(dnsValue["aaaaRecord"], "mustBeAbsent")
        self.assertEqual(dnsValue["runtimeState"], "UNVERIFIED_UNTIL_RENDER_DOMAIN_DNS_TLS_AND_MCP_PROBES_PASS")
        self.assertTrue(audit(self.rootValue)["errors"] == [])

    def testDirectoryPullAndDnsDriftRejected(self):
        changes = (
            (("directoryPullLocator", "maySubstituteForGitHubRefPathOrCommit"), True),
            (("directoryPullLocator", "requiresExactRepositoryRefPathAndCommitSha"), False),
            (("forwardDns", "recordType"), "A"),
            (("forwardDns", "proxy"), "PROXIED"),
            (("forwardDns", "aaaaRecord"), "present"),
            (("forwardDns", "runtimeState"), "LIVE"),
        )
        for pathValue, wrongValue in changes:
            with self.subTest(pathValue=pathValue):
                originalValue = copy.deepcopy(self.docValue)
                targetValue = self.docValue["identityChain"]["canonicalRepository"]["remoteSourceIdentity"][pathValue[0]]
                targetValue[pathValue[1]] = wrongValue
                self.saveDoc()
                self.assertTrue(audit(self.rootValue)["errors"])
                self.docValue = originalValue

    def testRemoteSourceIdentityDriftRejected(self):
        for keyValue, wrongValue in (("identity", "mcp.eggiebagelface.art"), ("forwardHttpsFqdn", "art.eggiebagelface.mcp"), ("wildcardSortingPatternIsLiteralDns", True), ("isPtrRecord", True), ("cloudflareProxy", "enabled")):
            with self.subTest(keyValue=keyValue):
                originalValue = copy.deepcopy(self.docValue)
                self.docValue["identityChain"]["canonicalRepository"]["remoteSourceIdentity"][keyValue] = wrongValue
                self.saveDoc()
                self.assertTrue(audit(self.rootValue)["errors"])
                self.docValue = originalValue

    def testNameserverAndPtrClaimsRejected(self):
        changes = (
            ("authoritativeNameservers", "delegationState", "LIVE"),
            ("authoritativeNameservers", "mayChangeRegistrarDelegation", True),
            ("reverseDnsPtrWhenApplicable", "renderSharedIpIsOwnedByProject", True),
            ("reverseDnsPtrWhenApplicable", "mayMutatePtr", True),
            ("reverseDnsPtrWhenApplicable", "optionalForPublicMcpTlsReadiness", False),
        )
        for parentValue, keyValue, value in changes:
            with self.subTest(parentValue=parentValue, keyValue=keyValue):
                originalValue = copy.deepcopy(self.docValue)
                self.docValue["identityChain"][parentValue][keyValue] = value
                self.saveDoc()
                self.assertTrue(audit(self.rootValue)["errors"])
                self.docValue = originalValue

    def testRepositoryAndProxyCollisionRejected(self):
        changes = (
            ("canonicalRepository", "githubRepositoryIsDnsNameserver", True),
            ("canonicalRepository", "donorHistoryAutoMerge", True),
            ("proxyLane", "mayActivateFromSourceOnly", True),
            ("proxyLane", "trustUnverifiedForwardedHeaders", True),
        )
        for parentValue, keyValue, value in changes:
            with self.subTest(parentValue=parentValue, keyValue=keyValue):
                originalValue = copy.deepcopy(self.docValue)
                self.docValue["identityChain"][parentValue][keyValue] = value
                self.saveDoc()
                self.assertTrue(audit(self.rootValue)["errors"])
                self.docValue = originalValue

    def testRenderTunnelDriftRejected(self):
        pathValue = self.rootValue / "doctrine/cloudflareAirTrafficControllerV1.json"
        value = json.loads(pathValue.read_text())
        value["lanes"]["publicChatPluginMcp"]["tunnelForThisLane"] = True
        pathValue.write_text(json.dumps(value))
        self.assertTrue(audit(self.rootValue)["errors"])

    def testMalformedMissingAndWrongShapeFailClosed(self):
        pathValue = self.rootValue / "doctrine/networkSpineV1.json"
        for value in ("{", "[]", '{"reverseProxy": null}', "{}"):
            with self.subTest(value=value):
                pathValue.write_text(value)
                self.assertTrue(audit(self.rootValue)["errors"])
        pathValue.unlink()
        self.assertTrue(audit(self.rootValue)["errors"])

    def testCliFailureIsRedAndNonzero(self):
        (self.rootValue / "doctrine/networkSpineV1.json").write_text("{}")
        resultValue = subprocess.run([sys.executable, str(rootPath / "tools/networkSpineAudit.py"), "--root", str(self.rootValue)], capture_output=True, text=True)
        self.assertNotEqual(resultValue.returncode, 0)
        self.assertEqual(json.loads(resultValue.stdout)["status"], "RED_NETWORK_SPINE_SOURCE")

    def testAgentPointerDriftRejected(self):
        pathValue = self.rootValue / "agents/urdMutationOni/SKILL.md"
        pathValue.write_text("No spine contract")
        self.assertTrue(audit(self.rootValue)["errors"])

    def testMissingRuntimeCheckRejected(self):
        self.docValue["runtimeEvidenceRequired"].remove("authBoundary")
        self.saveDoc()
        self.assertTrue(audit(self.rootValue)["errors"])

    def testLiveMutationAndAlignmentDriftRejected(self):
        for parentValue, keyValue, value in (("liveMutation", "dns", True), ("repositoryAlignment", "unrelatedHistoryMerge", True), ("repositoryAlignment", "snapshotsBeforeStructuralChanges", False), ("reverseProxy", "cacheAuthenticatedOrMcpTraffic", True)):
            with self.subTest(keyValue=keyValue):
                originalValue = copy.deepcopy(self.docValue)
                self.docValue[parentValue][keyValue] = value
                self.saveDoc()
                self.assertTrue(audit(self.rootValue)["errors"])
                self.docValue = originalValue


class CertbotPathTests(unittest.TestCase):
    def setUp(self):
        self.tempValue = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempValue.cleanup)
        self.rootValue = Path(self.tempValue.name)
        self.certName = "system.eggiebagelface.art"
        self.liveValue = self.rootValue / "live" / self.certName
        self.archiveValue = self.rootValue / "archive" / self.certName
        for pathValue in (self.liveValue, self.archiveValue, self.rootValue / "renewal"):
            pathValue.mkdir(parents=True)
        for prefixValue in ("fullchain", "privkey"):
            targetValue = self.archiveValue / (prefixValue + "1.pem")
            targetValue.touch()
            (self.liveValue / (prefixValue + ".pem")).symlink_to(targetValue)
        (self.rootValue / "renewal" / (self.certName + ".conf")).touch()

    def checkFails(self):
        resultValue, codeValue = inspectPaths(self.certName, self.rootValue)
        self.assertNotEqual(codeValue, 0)
        self.assertNotEqual(resultValue["status"], "GREEN_CERTBOT_LIVE_PATH_PRESENT")

    def testValidLinksProveOnlyFilesystem(self):
        with patch.object(Path, "read_text", side_effect=AssertionError("contents must not be read")), patch.object(Path, "read_bytes", side_effect=AssertionError("contents must not be read")):
            resultValue, codeValue = inspectPaths(self.certName, self.rootValue)
        self.assertEqual(codeValue, 0)
        self.assertFalse(resultValue["certificateValidityProven"])
        self.assertFalse(resultValue["renewalProven"])
        self.assertFalse(resultValue["serviceReadinessProven"])

    def testInvalidNamesRejected(self):
        for value in ("", "../other", "/etc/passwd", ".", "..", "a/b", "bad\nname"):
            with self.subTest(value=value):
                self.assertNotEqual(inspectPaths(value, self.rootValue)[1], 0)

    def testCopiedFilesRejected(self):
        pathValue = self.liveValue / "privkey.pem"
        pathValue.unlink()
        pathValue.touch()
        self.checkFails()

    def testBrokenSymlinkRejected(self):
        (self.archiveValue / "privkey1.pem").unlink()
        self.checkFails()

    def testEscapedArchiveRejected(self):
        otherValue = self.rootValue / "privkey1.pem"
        otherValue.touch()
        pathValue = self.liveValue / "privkey.pem"
        pathValue.unlink()
        pathValue.symlink_to(otherValue)
        self.checkFails()

    def testMismatchedVersionsRejected(self):
        targetValue = self.archiveValue / "privkey2.pem"
        targetValue.touch()
        pathValue = self.liveValue / "privkey.pem"
        pathValue.unlink()
        pathValue.symlink_to(targetValue)
        self.checkFails()

    def testRenewalDirectoryAndSymlinkRejected(self):
        pathValue = self.rootValue / "renewal" / (self.certName + ".conf")
        pathValue.unlink()
        pathValue.mkdir()
        self.checkFails()
        pathValue.rmdir()
        pathValue.symlink_to(self.archiveValue / "fullchain1.pem")
        self.checkFails()

    def testSymlinkCycleRejected(self):
        pathValue = self.liveValue / "privkey.pem"
        pathValue.unlink()
        pathValue.symlink_to(pathValue)
        self.checkFails()

    def testFilesystemErrorFailsClosed(self):
        with patch.object(Path, "is_dir", side_effect=PermissionError):
            self.checkFails()


if __name__ == "__main__":
    unittest.main()

