"""Fast Studio Mesh: source contract and quarantine-preserving route behavior."""
import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import studioFastMesh
from lumTaskRouter import ROUTES


class StudioFastMeshTests(unittest.TestCase):
    def test_canonical_contract(self):
        self.assertEqual([], studioFastMesh.audit())

    def test_every_route_is_read_only(self):
        for kind in ROUTES:
            with self.subTest(kind=kind):
                route = studioFastMesh.plan(kind)
                self.assertEqual(route["activeWorkers"], [])
                self.assertFalse(route["mayExecuteWorkers"])
                self.assertFalse(route["mayMutateSource"])
                self.assertFalse(route["mayDeploy"])
                self.assertFalse(route["maySpend"])
                self.assertFalse(route["mayInvokeProvider"])

    def test_google_is_workhorse_not_authority(self):
        route = studioFastMesh.plan("research", heavy=True)
        self.assertEqual(route["providerCandidate"], "googleAi")
        self.assertEqual(route["entitlementGate"], "UNKNOWN_ACCOUNT_BOUND_RECEIPT_REQUIRED")
        self.assertEqual(route["companyOperationalHold"], "QUARANTINED")

    def test_hugging_face_remains_specialist(self):
        route = studioFastMesh.plan("research", specialist=True)
        self.assertEqual(route["providerCandidate"], "huggingFace")
        self.assertFalse(route["mayInvokeProvider"])

    def test_repository_remains_source(self):
        route = studioFastMesh.plan("patch")
        self.assertEqual(route["sourceRepository"], "eggie-admin/LuHm-OS")
        self.assertEqual(route["compatibilityLayers"], ["chatGptOpenAi", "github"])

    def test_no_unknown_route(self):
        with self.assertRaises(ValueError):
            studioFastMesh.plan("inventedAgent")


if __name__ == "__main__":
    unittest.main()
