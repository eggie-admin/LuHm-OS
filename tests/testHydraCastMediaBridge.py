"""Source-only negative controls for camera + matte + dating sim CAST."""
import copy,unittest
from tools.hydraCastMediaBridge import verify_policy,verify_story,plan_shot
from tools.hydraCastMediaBridge import POLICY,STORY
import json
class HydraCastMediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(POLICY.read_text(encoding="utf-8"))
        cls.s=json.loads(STORY.read_text(encoding="utf-8"))
        cls.shot={"schema":"luhmOs.captureShot.v1","shotId":"rebel001","fps":"30/1","mode":"luminanceMatte","sourceRightsCleared":True,"captureConsent":True,"audioClapFrame":30,"threshold":176,"cameras":[{"cameraId":"camFront","file":"front.mp4","sha256":"a"*64,"frameOffset":0},{"cameraId":"camSide","file":"side.mov","sha256":"b"*64,"frameOffset":1}]}
    def policy_fault(self,key,value,code):
        p=copy.deepcopy(self.p);section,field=key;p[section][field]=value
        self.assertIn(code,verify_policy(p))
    def shot_fault(self,mutate,code):
        s=copy.deepcopy(self.shot);mutate(s)
        with self.assertRaisesRegex(ValueError,code):plan_shot(s)
    def test_policy_and_story(self):self.assertEqual(verify_policy(self.p),[]);self.assertEqual(verify_story(self.s),[])
    def test_default_luma_preview(self):
        result=plan_shot(self.shot);self.assertEqual(result["status"],"PLAN_ONLY_PRIVATE")
        self.assertIn("lutyuv=",result["command"][-5]);self.assertEqual(result["execution"],False)
        self.assertFalse(result["sourceHashVerified"]);self.assertFalse(result["inputFilesExistVerified"])
    def test_chroma_distinct(self):
        s=copy.deepcopy(self.shot);s["mode"]="colorChromaKey";s["keyColor"]="green"
        self.assertIn("colorkey=green",plan_shot(s)["command"][-5])
    def test_vector_requires_artist(self):
        s=copy.deepcopy(self.shot);s["mode"]="vectorRoto"
        self.assertEqual(plan_shot(s)["status"],"ARTIST_EDIT_REQUIRED")
    def test_no_raw_path_escape(self):self.shot_fault(lambda s:s["cameras"][0].update(file="../secret.mp4"),"UNSAFE_FILE")
    def test_no_shell_metacharacter(self):self.shot_fault(lambda s:s["cameras"][0].update(file="x;touch.mp4"),"UNSAFE_FILE")
    def test_duplicate_cameras(self):self.shot_fault(lambda s:s["cameras"][1].update(cameraId="camFront"),"DUPLICATE_CAMERA")
    def test_requires_clap(self):self.shot_fault(lambda s:s.update(audioClapFrame=None),"SYNC_CLAP")
    def test_requires_rights(self):self.shot_fault(lambda s:s.update(sourceRightsCleared=False),"RIGHTS_OR_CONSENT")
    def test_six_camera_limit(self):
        s=copy.deepcopy(self.shot);s["cameras"]=s["cameras"]*4
        self.assertRaisesRegex(ValueError,"CAMERA_COUNT",plan_shot,s)
    def test_no_bad_threshold(self):self.shot_fault(lambda s:s.update(threshold=999),"THRESHOLD")
    def test_no_invalid_hash(self):self.shot_fault(lambda s:s["cameras"][0].update(sha256="0"),"SOURCE_SHA")
    def test_no_auto_video_upload(self):self.policy_fault(("ai","automaticVideoUpload"),True,"AI_AUTONOMY_automaticVideoUpload")
    def test_no_paid_model(self):self.policy_fault(("ai","autoSpendUsd"),1,"AI_SPEND")
    def test_no_fake_six_cam_proof(self):self.policy_fault(("capture","multiCameraHardwareSyncVerified"),True,"FAKE_CAMERA_PROOF_multiCameraHardwareSyncVerified")
    def test_no_gpl_unreal_link(self):self.policy_fault(("unrealLicensing","automaticallyLinkGplCodeIntoUnreal"),True,"UNREAL_LICENSE_BLOCK_automaticallyLinkGplCodeIntoUnreal")
    def test_no_epic_source_committed(self):self.policy_fault(("unrealLicensing","commitEpicEngineSourceToPublicRepo"),True,"UNREAL_LICENSE_BLOCK_commitEpicEngineSourceToPublicRepo")
    def test_no_meta_ai_training(self):self.policy_fault(("unrealLicensing","metahumanAssetsForAiTrainingAllowed"),True,"UNREAL_LICENSE_BLOCK_metahumanAssetsForAiTrainingAllowed")
    def test_no_unproven_legal_clearance(self):self.policy_fault(("unrealLicensing","legalClearanceObtained"),True,"UNREAL_LICENSE_BLOCK_legalClearanceObtained")
    def test_keep_unreal_unproven(self):self.policy_fault(("existingSpine","unrealStatus"),"BUILT","ENGINE_PROOF")
    def test_no_auto_release(self):self.policy_fault(("promotion","automaticDeploy"),True,"UNAUTHORIZED_RELEASE_automaticDeploy")
    def test_story_all_adults(self):
        s=copy.deepcopy(self.s);s["characters"][0]["adult"]=False
        self.assertIn("STORY_AGE_OR_CANON",verify_story(s))
    def test_story_dangling_node(self):
        s=copy.deepcopy(self.s);s["nodes"][0]["choices"][0]["next"]="missing"
        self.assertIn("INVALID_CHOICE",verify_story(s))
    def test_unreachable_story(self):
        s=copy.deepcopy(self.s);s["nodes"][0]["choices"][1]["next"]="practice"
        self.assertIn("UNREACHABLE_STORY_NODE",verify_story(s))
if __name__=="__main__":unittest.main()
