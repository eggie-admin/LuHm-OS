"""Negative controls for Unreal destination, licenses, modding and release boundaries."""
import copy,json,unittest
from tools.unrealFinalFormAudit import POLICY,evaluate
class UnrealFinalFormBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads(POLICY.read_text(encoding="utf-8"))
    def failcase(self,mutate,expected):
        p=copy.deepcopy(self.p);mutate(p);self.assertIn(expected,evaluate(p))
    def test_baseline(self):self.assertEqual(evaluate(self.p),[])
    def test_no_fake_unreal(self):self.failcase(lambda p:p["engineDirection"].update(unrealRuntimeVerified=True),"FALSE_ENGINE_PROOF_unrealRuntimeVerified")
    def test_godot_preserved(self):self.failcase(lambda p:p["engineDirection"].update(godotDeletionAllowed=True),"FALSE_ENGINE_PROOF_godotDeletionAllowed")
    def test_no_private_master_upload(self):self.failcase(lambda p:p["studioPipeline"].update(autoUploadPrivateMasters=True),"ASSET_EXPOSURE_autoUploadPrivateMasters")
    def test_original_rights(self):self.failcase(lambda p:p["studioPipeline"].update(assetsRequireKnownRights=False),"ASSET_GATE_assetsRequireKnownRights")
    def test_no_asset_script(self):self.failcase(lambda p:p["studioPipeline"].update(executeUntrustedAssetScripts=True),"ASSET_EXPOSURE_executeUntrustedAssetScripts")
    def test_optional_oracle(self):self.failcase(lambda p:p["adapters"][4].update(enabledByDefault=True),"AUTO_VENDOR_EXECUTION_oracleOciAi")
    def test_optional_nvidia(self):self.failcase(lambda p:p["adapters"][0].update(networkAllowedByDefault=True),"AUTO_VENDOR_EXECUTION_nvidiaAce")
    def test_no_mod_redistribution(self):self.failcase(lambda p:p["moddingLaw"].update(autoRedistributeThirdPartyMods=True),"NEXUS_POLICY_autoRedistributeThirdPartyMods")
    def test_no_fake_app_registration(self):self.failcase(lambda p:p["moddingLaw"].update(publicAppRegistrationVerified=True),"NEXUS_POLICY_publicAppRegistrationVerified")
    def test_no_bulk_merge(self):self.failcase(lambda p:p["repositoryInventory"].update(bulkMerge=True),"GIT_HISTORY_SAFETY_bulkMerge")
    def test_no_unverified_runtime(self):self.failcase(lambda p:p["safety"].update(acceptUnverifiedRuntime=True),"UNAUTHORIZED_ACTION_acceptUnverifiedRuntime")
    def test_no_spend(self):self.failcase(lambda p:p["safety"].update(autoSpendUsd=1),"UNAUTHORIZED_SPENDING")
    def test_no_deploy(self):self.failcase(lambda p:p["safety"].update(autoDeploy=True),"UNAUTHORIZED_ACTION_autoDeploy")
    def test_crown_stays_stop(self):self.failcase(lambda p:p["safety"].update(crown="GREEN"),"FALSE_CROWN")
if __name__=="__main__":unittest.main()
