"""Bounded 500³ design / mod provenance / original-avatar / web HDR source controls."""
import copy,json,unittest
from tools.hydraModAvatarAudit import POLICY,audit,inspect_mod,inspect_avatar,inspect_skybox,sample_matrix
class HydraModAvatarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads(POLICY.read_text(encoding="utf-8"))
    def altered(self,section,key,value,error):
        p=copy.deepcopy(self.p);p[section][key]=value
        self.assertIn(error,audit(p))
    def test_policy_source_only(self):self.assertEqual(audit(self.p),[])
    def test_500_by_500_by_500_no_fake_green(self):
        cases=sample_matrix();self.assertEqual(len(cases),500)
        self.assertEqual(len(set(cases)),500)
        for dimension in range(3):self.assertEqual(len({case[dimension] for case in cases}),500)
        self.assertEqual(500**3,125000000)
        self.altered("coverage","sampleExecutedAsHardwareTests",True,"FAKE_TEST_PASS")
    def test_no_auto_adult_browsing(self):self.altered("nexus","autoBrowseAdult",True,"NEXUS_BOUNDARY_autoBrowseAdult")
    def test_no_nexus_asset_republication(self):self.altered("nexus","repurposeGameAssets",True,"NEXUS_BOUNDARY_repurposeGameAssets")
    def test_no_nexus_download(self):self.altered("nexus","autoDownloadMods",True,"NEXUS_BOUNDARY_autoDownloadMods")
    def test_legacy_vortex_api_blocked(self):self.altered("nexus","archivedVortexApiRepoUse",True,"NEXUS_BOUNDARY_archivedVortexApiRepoUse")
    def test_untrusted_mod_execution_blocked(self):self.altered("nexus","runThirdPartyInstallers",True,"NEXUS_BOUNDARY_runThirdPartyInstallers")
    def test_mod_requires_rights_and_adult_gate(self):
        m={"schema":"luhmOs.externalModReference.v1","source":"nexus","audience":"adult","adultVerified":False,"game":"fallout4"}
        self.assertEqual(inspect_mod(m),"HOLD_ADULT_AGE_GATE")
        m["adultVerified"]=True;self.assertEqual(inspect_mod(m),"HOLD_REUSE_RIGHTS")
        m["authorPermissionForHydraReuse"]=True;m["gamePublisherRightsCleared"]=True
        self.assertEqual(inspect_mod(m),"HOLD_UNVERIFIED_HASH")
        m["sha256"]="a"*64;self.assertEqual(inspect_mod(m),"REVIEW_ORIGINAL_AND_LICENSES_MANUALLY")
    def test_no_rated_mod_remote_execution(self):
        m={"schema":"luhmOs.externalModReference.v1","audience":"general","source":"nexus","game":"residentEvil","downloadRequested":True}
        self.assertEqual(inspect_mod(m),"REJECT_AUTOMATIC_EXECUTION")
    def test_avatar_no_source_no_proof(self):self.assertEqual(inspect_avatar({}),"NO_MEASURED_AVATAR_REPORT")
    def test_avatar_requires_measured_bone_faces(self):
        a={"schema":"luhmOs.measuredAvatarReport.v1","adultOriginalCharacter":True,"assetRightsCleared":True,
           "sha256":"f"*64,"measuredInBlender":True,"uvAndNormalsInspected":True,"weightsNormalized":True,
           "triangles":70000,"edgeLoopPasses":{"eyes":True,"mouth":True,"shoulder":True,"elbow":True,"hip":True,"knee":False},
           "morphTargets":["blinkLeft","blinkRight","smile","jawOpen","visemeAa","visemeOh"],"artistReviewed":True}
        self.assertEqual(inspect_avatar(a),"HOLD_DEFORMING_EDGE_LOOPS")
        a["edgeLoopPasses"]["knee"]=True;self.assertEqual(inspect_avatar(a),"REVIEW_CANDIDATE_SOURCE_ONLY")
        a["triangles"]=140000;self.assertEqual(inspect_avatar(a),"HOLD_TRIANGLE_BUDGET")
    def test_avatar_not_pretend_inspected(self):self.altered("avatar","actualBlenderMeshInspected",True,"FALSE_AVATAR_PROOF_actualBlenderMeshInspected")
    def test_hdr_requires_local_rights(self):
        s={"schema":"luhmOs.localSkyboxReference.v1","path":"https://cdn/sky.hdr","licenseClear":True,"artistApproved":True,"sha256":"d"*64,"sizeBytes":1000}
        self.assertEqual(inspect_skybox(s),"HOLD_SKYBOX_LOCAL_PATH")
        s["path"]="assets/skyboxes/studio-night.hdr"
        self.assertEqual(inspect_skybox(s),"REVIEW_CANDIDATE_NOT_RENDERED")
        s["licenseClear"]=False;self.assertEqual(inspect_skybox(s),"HOLD_SKYBOX_RIGHTS")
    def test_web_no_new_renderer(self):self.altered("web","additionalRendererAllowed",True,"WEB_UNSAFE_additionalRendererAllowed")
    def test_web_no_fake_hdr(self):self.altered("web","hdrAssetReady",True,"WEB_UNSAFE_hdrAssetReady")
    def test_no_cloud_ai_spend(self):self.altered("security","autoSpendUsd",10,"SPEND_GATE")
    def test_no_automatic_merge(self):self.altered("security","autoMerge",True,"UNSAFE_PRIVILEGE_autoMerge")
    def test_no_unreal_installed(self):self.altered("stack","unreal","BUILT","ENGINE_DRIFT")
if __name__=="__main__":unittest.main()
