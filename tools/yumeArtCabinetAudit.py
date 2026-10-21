#!/usr/bin/env python3
"""Static Yume/Lum cabinet contract audit; never invokes creative providers."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda path: (ROOT / path).read_text(encoding="utf-8")
load = lambda path: json.loads(read(path))
cabinet = load("doctrine/yumeArtCabinetHandoffV1.json")
roles = load("doctrine/agentSystemDeploymentV1.json")
goddesses = load("doctrine/lumGoddessCabinetV1.json")
quarantine = load("doctrine/companyWideOperationalQuarantineV1.json")
godot = load("doctrine/yumeGodotArtToolboxV1.json")
lanes = load("doctrine/contentLaneDoctrineV1.json")
yume = read("agents/yumeArtOni/SKILL.md")
shared = read("agents/goddessSharedSystemsPractice/SKILL.md")
asset_prep = read("tools/yumeGodotAssetPrep.py")
test = read("tests/testYumeAssetPrepSecurity.py")

checks = []
def check(label, predicate): checks.append((label, bool(predicate)))

check("schema", cabinet["schema"] == "luhmOs.yumeArtCabinetHandoff.v1")
check("authority", cabinet["authority"] == "Professor")
check("LumBoss", cabinet["boss"] == "lum")
check("creativeOwner", cabinet["creativeOwner"] == "yume")
check("quarantineLinked", cabinet["quarantineRef"] == "doctrine/companyWideOperationalQuarantineV1.json")
check("quarantineActive", quarantine["state"] == "QUARANTINED")
check("zeroAgentExecution", quarantine["activeTaskWorkersAllowed"] is False)
check("noHiddenAsync", quarantine["hiddenAsyncAgents"] is False)
check("cabinetNoAgentClaims", cabinet["autonomousWorkerClaims"] is False)
check("lumInRegistry", "lum" in roles["requiredAgents"])
check("yumeInRegistry", "yume" in roles["requiredAgents"])
for name in ("lum","urdDoctorGoddess","belldandySecretary","skuldResearch"):
    check("goddessCabinet_" + name, name in [r["id"] for r in goddesses["members"]])
for name in ("lum","yume","urdDoctorGoddess","belldandySecretary","skuldResearch","sumi"):
    check("artCabinet_" + name, name in cabinet["cabinet"])
check("oneMutableLane", cabinet["singleMutableSourceLane"] is True)
check("maxThreeSupportWorkers", cabinet["maxSupportWorkerRoles"] == 3)
check("one3dForeground", "one foreground rigged high-detail 3D character" in cabinet["creativeProfile"]["primary"])
check("lightweight2dBackground", "2D sprites" in cabinet["creativeProfile"]["secondary"])
check("privateMasters", "private" in cabinet["creativeProfile"]["masters"])
check("mobileProofUnknown", "UNKNOWN" in cabinet["creativeProfile"]["mobile"])
check("noExternalProviderClaim", cabinet["registeredAgentExecution"] is False)
check("artLicenseUnknownBlocks", cabinet["publicationGuards"]["unknownLicenseMayShip"] is False)
check("privateReferenceCannotShip", cabinet["publicationGuards"]["privateSourceMayShip"] is False)
check("generatedPublicDenied", cabinet["publicationGuards"]["generatedPublicDefaultAllowed"] is False)
check("noAutoRelease", cabinet["publicationGuards"]["quarantineMayAutoRelease"] is False)
check("deviceProofSeparate", cabinet["publicationGuards"]["sourceGreenIsDeviceGreen"] is False)
check("noAutoPublish", cabinet["publicationGuards"]["aiExecutionMayAuthorizePublish"] is False)
check("YumeToolRef", cabinet["tools"]["assetPrep"] == godot["tools"]["assetPrep"])
check("YumeTestRef", cabinet["tools"]["assetPrepAdversarialTests"] == godot["tools"]["assetPrepAdversarialTests"])
check("GodotCabinetRef", godot["cabinetHandoff"] == "doctrine/yumeArtCabinetHandoffV1.json")
check("strictHashLaw", godot["assetSecurity"]["hash"] == "strictLowerHexSha256")
check("symlinkLaw", godot["assetSecurity"]["sourcePaths"] == "repoRelativeAndSymlinkBounded")
check("publicLane", "cathedralPublic" in lanes["lanes"])
check("privateLane", "privateMutation" in lanes["lanes"])
check("codeNoNetwork", "requests." not in asset_prep and "urllib." not in asset_prep)
check("codeNoSubprocess", "subprocess" not in asset_prep)
check("codeBoundsSource", "is_relative_to(root)" in asset_prep)
check("codeValidatesHash", "sourceHashMismatch" in asset_prep)
check("codeChecksMagic", "sourceFormatInvalid" in asset_prep)
check("codeDeniesPublicAi", "publicGeneratedAiArtDefaultDenied" in asset_prep)
check("codeNoUpload", "publicationAuthority" in asset_prep)
check("YumeSkillCabinet", "doctrine/yumeArtCabinetHandoffV1.json" in yume)
check("SharedSkillCabinet", "doctrine/yumeArtCabinetHandoffV1.json" in shared)
check("YumeUnknownRuntime", "not Blender export proof" in yume)
check("TestSymlinkEscape", "test_rejects_symlink_escape" in test)
check("TestPublicRights", "test_public_lane_requires_rights_and_approval" in test)
check("TestGLBLength", "test_rejects_glb_header_length_mismatch" in test)
check("TestNoWrites", "publicationAuthority" in test)
check("CrownStop", cabinet["crownStatus"] == "STOP")

for i, (name, passed) in enumerate(checks, 1):
    print(f"{'PASS' if passed else 'FAIL'} {i:02d}/{len(checks)} {name}")
failures = [name for name, good in checks if not good]
assert len(checks) >= 45
if failures:
    raise SystemExit("YUME_ART_CABINET_SOURCE_RED: " + ",".join(failures))
print(f"YUME_ART_CABINET_SOURCE_GREEN: {len(checks)}/{len(checks)}; RUNTIME_AND_AGENT_PROOF_UNVERIFIED")
