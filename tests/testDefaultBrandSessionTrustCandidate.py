"""Source-only baseline checks. No login sessions, Cloudflare changes or deploys."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "doctrine/defaultBrandSessionTrustCandidateV1.json").read_text(encoding="utf-8"))

def problems(policy):
    errors = []
    def need(condition, code):
        if not condition:
            errors.append(code)
    need(policy.get("schema") == "luhmOs.defaultBrandSessionTrustCandidate.v1", "schema")
    need(policy.get("status") == "PROPOSED_SOURCE_ONLY_UNSEALED", "unsealed")
    visual = policy.get("visualLaw", {})
    need(visual.get("defaultBrandedFromFirstPaint") is True, "firstPaint")
    need(visual.get("ownerControlledOnly") is True, "hostBoundary")
    need(visual.get("petPresentation", "").startswith("Reuse existing pet dock"), "petReuse")
    need(visual.get("noUnapprovedReferenceTransplants") is True, "copyright")
    need(visual.get("boundaries", {}).get("cannotStyleChatGptNativeThinking") is True, "hostThinking")
    need(visual.get("boundaries", {}).get("cannotReplaceRenderManagedColdStartPage") is True, "renderColdStart")
    need([s.get("id") for s in visual.get("surfaces", [])] ==
         ["firstPaint", "serverLoading", "godotBoot", "inChat"], "fourVisualSurfaces")
    sessions = policy.get("sessionLaw", {})
    tiers = sessions.get("fourRemoteTiers", [])
    need([t.get("tier") for t in tiers] == [0, 1, 2, 3], "fourOrderedRemoteTiers")
    need([t.get("rememberDeviceDays") for t in tiers] == [30, 7, 1, 0], "decreasingRememberTrust")
    need([t.get("absoluteSessionHours") for t in tiers] == [720, 24, 12, 1], "decreasingAbsolute")
    need([t.get("idleMinutes") for t in tiers] == [10080, 60, 30, 15], "decreasingIdle")
    need(sessions.get("requireServerSideExpiry") is True, "serverExpiry")
    need(sessions.get("requireRevocationOnLogoutOrCompromise") is True, "revocable")
    need(sessions.get("requireMfaForSensitiveRemote") is True, "remoteMfa")
    need(sessions.get("noArbitraryPeriodicPasswordChanges") is True, "passwordPolicy")
    local = sessions.get("indefiniteLocalDeviceTrust", {})
    need(local.get("deviceRegistrationTtl") == "UNTIL_USER_REVOKES_OR_DEVICE_LOST", "deviceTrust")
    need(local.get("authenticationSessionTtl") == "BOUNDED_RENEWABLE" and
         local.get("noForeverBearerTokens") is True, "noForeverSession")
    need(local.get("remoteGateAppliesToLocalDeviceOnRemoteNetwork") is True, "remoteStepUp")
    live = policy.get("liveChanges", {})
    need(live.get("none") is True and
         all(live.get(name) is False for name in
             ("sessionCookieWrites", "cloudflareAccessChanges", "renderDeploy", "githubMerge", "pluginInstall")),
         "noLiveMutation")
    need(policy.get("crownStatus") == "STOP", "crown")
    return errors

class BrandSessionProposalTest(unittest.TestCase):
    def test_canonical_source(self):
        self.assertEqual(problems(POLICY), [])
    def test_cannot_make_home_forever_bearer(self):
        mutation = copy.deepcopy(POLICY)
        mutation["sessionLaw"]["indefiniteLocalDeviceTrust"]["noForeverBearerTokens"] = False
        self.assertIn("noForeverSession", problems(mutation))
    def test_cannot_promote_sensitive_30day(self):
        mutation = copy.deepcopy(POLICY)
        mutation["sessionLaw"]["fourRemoteTiers"][3]["rememberDeviceDays"] = 30
        self.assertIn("decreasingRememberTrust", problems(mutation))
    def test_cannot_treat_native_chatgpt_thinking_as_themed(self):
        mutation = copy.deepcopy(POLICY)
        mutation["visualLaw"]["boundaries"]["cannotStyleChatGptNativeThinking"] = False
        self.assertIn("hostThinking", problems(mutation))
    def test_cannot_enable_unreviewed_platform_changes(self):
        mutation = copy.deepcopy(POLICY)
        mutation["liveChanges"]["cloudflareAccessChanges"] = True
        self.assertIn("noLiveMutation", problems(mutation))

if __name__ == "__main__":
    unittest.main()
