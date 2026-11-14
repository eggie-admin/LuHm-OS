"""Read-only regression controls for LuHm Samsung field kit."""
from __future__ import annotations
from io import BytesIO
from unittest import TestCase, main, mock

from tools import samsungFieldKit as kit


class FakeHttpResponse:
    def __init__(self, body: bytes):
        self.body = BytesIO(body)
    def __enter__(self):
        return self
    def __exit__(self, *_):
        self.body.close()
    def read(self, size=-1):
        return self.body.read(size)


class FieldKitTests(TestCase):
    def test_help_has_no_mutation_language(self):
        self.assertEqual(kit.main(["help"]), 0)

    def test_git_pull_only_clean_main(self):
        good = {"sourceRef": "a"*40, "branch": "main",
                "trackedChangesPresent": False}
        self.assertEqual(kit.safe_pull_instruction(good), "git pull --ff-only origin main")
        self.assertEqual(kit.safe_pull_instruction({**good, "branch": "develop"}),
                         "STOP_NOT_ON_MAIN")
        self.assertEqual(kit.safe_pull_instruction({**good, "trackedChangesPresent": True}),
                         "STOP_LOCAL_CHANGES_OR_STATUS_UNKNOWN")
        self.assertEqual(kit.safe_pull_instruction({**good, "trackedChangesPresent": None}),
                         "STOP_LOCAL_CHANGES_OR_STATUS_UNKNOWN")
        self.assertEqual(kit.safe_pull_instruction({**good, "sourceRef": "UNVERIFIED"}),
                         "STOP_NOT_A_GIT_CHECKOUT")

    def test_edge_requires_physical_setup(self):
        edge = kit.edge_profile()
        self.assertEqual(edge["providerId"], "edgeGallery")
        self.assertEqual(edge["sourceReadiness"], "UNCONFIGURED_EVIDENCE_PENDING")
        self.assertEqual(edge["appInstalled"], "UNVERIFIED")
        self.assertEqual(edge["luHmBridgeOperational"], "UNVERIFIED")
        self.assertEqual(edge["networkCalls"], 0)

    def test_ollama_reads_only_fixed_local_paths_and_redacts_model_details(self):
        requests = []
        def fake(url, *, timeout):
            requests.append((url, timeout))
            if url.endswith("/api/version"):
                return FakeHttpResponse(b'{"version":"1.0"}')
            return FakeHttpResponse(b'{"models":[{"name":"gemma:test","digest":"not-shared"}]}')
        result = kit.ollama_probe(fetch=fake)
        self.assertEqual([x[0] for x in requests],
                         ["http://127.0.0.1:11434/api/version",
                          "http://127.0.0.1:11434/api/tags"])
        self.assertEqual(result["modelCount"], 1)
        self.assertEqual(result["modelNames"], ["gemma:test"])
        self.assertTrue(result["localServiceProven"])
        self.assertEqual(result["luHmBridgeOperational"], "UNVERIFIED")
        self.assertNotIn("digest", result)

    def test_ollama_offline_does_not_claim_proof(self):
        def offline(*_, **__):
            raise OSError("offline")
        result = kit.ollama_probe(fetch=offline)
        self.assertFalse(result["localServiceProven"])
        self.assertFalse(result["modelInference"])
        self.assertFalse(result["modelDownloaded"])

    def test_ollama_rejects_large_local_response(self):
        def oversize(*_, **__):
            return FakeHttpResponse(b"x"*65537)
        result = kit.ollama_probe(fetch=oversize)
        self.assertFalse(result["localServiceProven"])
        self.assertEqual(result["version"], "UNVERIFIED_RESPONSE_TOO_LARGE")

    def test_budget_does_not_trigger_audit(self):
        code, result = kit.doctor(passes=40)
        self.assertEqual(code, 2)
        self.assertEqual(result["verdict"], "RED_INVALID_PASS_BUDGET")

    def test_doctor_fail_closed_on_bad_source_identity(self):
        with mock.patch.object(kit, "git_identity",
                               return_value={"sourceRef":"UNVERIFIED"}):
            code, result = kit.doctor(passes=1)
        self.assertEqual(code, 2)
        self.assertEqual(result["verdict"], "RED_SOURCE_NOT_BOUND")

    def test_canon_source_remains_proposed(self):
        source = kit.source_profile()
        self.assertEqual(source["status"], "AMBER_PROPOSED_SEAL_OF_TRUTH")
        self.assertEqual(source["crownStatus"], "STOP")

    def test_status_is_read_only_without_device(self):
        with mock.patch.object(kit, "git_identity", return_value={"sourceRef":"a"*40}):
            with mock.patch.object(kit, "device_hints", return_value={"model":"UNVERIFIED"}):
                self.assertEqual(kit.main(["status"]), 0)


if __name__ == "__main__":
    main()
