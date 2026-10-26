"""Fail closed on Hydra closeout, exact Witching Hour names and vendor evidence."""
import unittest
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def read(path):
    value=yaml.safe_load((ROOT/path).read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise ValueError("RED_YAML_OBJECT")
    return value

class HydraVendorCloseoutTest(unittest.TestCase):
    def test_hydra_to_premonition_includes_required_gates(self):
        t=read("doctrine/hydraCloseoutPremonitionTasksV1.yaml")
        self.assertEqual(t["schema"],"luhmOs.hydraCloseoutToPremonition.v1")
        self.assertTrue(t["projectTransition"]["preserveProjectHydraPluginIdentity"])
        self.assertTrue(t["projectTransition"]["noPublicPremonitionPromotionBeforeHydraCloseout"])
        self.assertEqual(t["storage"]["liveOperationalState"],"existingApprovedSqlFirst")
        self.assertEqual(t["storage"]["portableConfigAndTasks"],"reviewedYaml")
        self.assertEqual(t["crownStatus"],"STOP")
        ids=[x["id"] for x in t["tasks"]]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual([x["priority"] for x in t["tasks"]],list(range(len(ids))))
        self.assertLess(ids.index("nativeSamsungLiteChatAcceptance"),ids.index("threeDHardening"))

    def test_namespace_forms_are_exact_not_renamed(self):
        t=read("doctrine/hydraCloseoutPremonitionTasksV1.yaml")
        self.assertEqual(t["namespace"]["exactAliases"],[
            "Witching Hour","witching hour","witching-hour","wh",
            "wtchngHr","witchingHour","WITCHING_HOUR"])
        self.assertTrue(t["namespace"]["aliasesNeverGrantExecution"])

    def test_vendor_docs_cover_current_stack_without_faking_entitlements(self):
        v=read("doctrine/vendorQuickstartLedgerV1.yaml")
        self.assertEqual(v["schema"],"luhmOs.vendorQuickstartLedger.v1")
        self.assertGreaterEqual(len(v["vendors"]),13)
        for n,record in v["vendors"].items():
            self.assertTrue(record.get("verifiedDocs"),n)
            self.assertTrue(all(url.startswith("https://") for url in record["verifiedDocs"]),n)
            self.assertTrue(record.get("observedRepo"),n)
            self.assertTrue(record.get("action"),n)
        self.assertTrue(v["libraryRules"]["preserveUpstreamVendoredDependencies"])
        self.assertTrue(v["libraryRules"]["npmIsDependencySourceNotProofOfCustomPluginPublication"])
        self.assertIn("Samsung Lite native ChatGPT UI mount or touch acceptance",v["unverified"])

    def test_jquery_triage_has_protected_legacy_path(self):
        r=read("doctrine/jqueryLegacyTriageV1.yaml")
        self.assertEqual(r["newCore"],"frontEnd/lib/luhmUiCore.js")
        states={x["feature"]:x["decision"] for x in r["inventory"]}
        self.assertEqual(states["vendorAliases"],"extract")
        self.assertEqual(states["normalizeMagicText"],"extract")
        self.assertEqual(states["backendOpenClose"],"retain")
        self.assertEqual(states["thirdPartyCdnScripts"],"retireAsDefault")
        self.assertEqual(states["godotBabylonBlenderRender"],"defer")
        self.assertFalse(r["sourcePromotionAuthorized"])

    def test_fingerprinted_cockpit_is_unchanged_and_candidate_is_isolated(self):
        import hashlib
        triage=read("doctrine/jqueryLegacyTriageV1.yaml")
        self.assertTrue(triage["acceptedLegacyUntouched"])
        self.assertFalse(triage["candidateRuntimeLoaded"])
        original=(ROOT/"frontEnd/jquery/luhm.cockpit.js").read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(original)).encode("ascii")+b"\\0"+original).hexdigest()
        self.assertEqual(blob,triage["acceptedLegacyBlob"])
        candidate=(ROOT/"frontEnd/jquery/luhm.cockpit.slimCandidate.js").read_text()
        self.assertIn("HISTORICAL COMPATIBILITY REFERENCE",candidate)
        self.assertIn("RED_LUHM_UI_CORE_NOT_LOADED",candidate)
        html=(ROOT/"frontEnd/index.html").read_text()
        self.assertNotIn("luhm.cockpit.slimCandidate.js",html)
        self.assertNotIn("lib/luhmUiCore.js",html)

    def test_openai_host_mount_remains_red_and_npm_private(self):
        t=read("doctrine/hydraCloseoutPremonitionTasksV1.yaml")
        self.assertEqual(t["observedAtStart"]["androidInChatHostMount"],"RED_OBSERVED_SCREENSHOT")
        self.assertTrue(t["observedAtStart"]["notAFullRepositoryCommitExhaustiveAudit"])
        v=read("doctrine/vendorQuickstartLedgerV1.yaml")
        self.assertEqual(v["vendors"]["jquery"]["publicationStatus"],"LOCAL_CUSTOM_PLUGIN_NOT_NPM_PUBLISHED")
        self.assertEqual(v["vendors"]["openAi"]["hostAcceptance"],"RED")

if __name__=="__main__":
    unittest.main()
