#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))

workstation=load("doctrine/yumeArtistWorkstationV1.json")
art=load("doctrine/yumeBigBrotherArtDeskV1.json")
godot=load("doctrine/yumeGodotArtToolboxV1.json")
campaign=load("doctrine/unifiedCampaignWorkbenchV1.json")
truth=load("doctrine/SOURCE_OF_TRUTH.json")
control=load("doctrine/luhmAiControlPlaneV1.json")
yume=load("doctrine/yumeCreativePipelineV1.json")

checks=[
 ("workstation.schema",workstation.get("schema")=="luhmOs.yumeArtistWorkstation.v1"),
 ("workstation.professor",workstation.get("authority")=="Professor"),
 ("workstation.yume",workstation.get("owner")=="yume"),
 ("workstation.lumBoss",workstation.get("boss")=="lum"),
 ("workstation.blender",any(x.get("toolId")=="blender" for x in workstation["capabilityClasses"]["modeling3d"])),
 ("workstation.meshy",any(x.get("toolId")=="meshyAi" for x in workstation["capabilityClasses"]["modeling3d"])),
 ("workstation.remotePool",any(x.get("toolId")=="remoteQuick3dVendorPool" and x.get("providerNamesMayNotBeGuessed") is True for x in workstation["capabilityClasses"]["modeling3d"])),
 ("workstation.godot",workstation["capabilityClasses"]["runtimeAndLayout"][0].get("toolId")=="godot4"),
 ("workstation.gimp",workstation["capabilityClasses"]["imageAndTexture"][0].get("toolId")=="gimp"),
 ("workstation.ffmpeg",workstation["capabilityClasses"]["videoAndAudio"][0].get("toolId")=="ffmpeg"),
 ("workstation.vram",workstation["capabilityClasses"]["compute"][0].get("toolId")=="localGpuVram"),
 ("workstation.noVendorCanon", "remote_provider_may_not_seal_canon_or_widen_content_lane" in workstation.get("remoteVendorLaw",[])),
 ("workstation.publicGenAiDefault",workstation.get("publicAuthorshipLaw",{}).get("publicGenerativeAiDefault")=="FORBIDDEN_UNLESS_PROFESSOR_CHANGES_POLICY"),
 ("art.bigBrother",art.get("provider",{}).get("providerNickname")=="bigBrother"),
 ("art.yumeNotReplaced",art.get("siblingLaw",{}).get("bigBrotherMayReplaceYume") is False),
 ("godot.prepTool",godot.get("tools",{}).get("assetPrep")=="tools/yumeGodotAssetPrep.py"),
 ("godot.noUniversalPolyBudget",godot.get("budgetLaw",{}).get("hardcodedUniversalPolygonBudget") is False),
 ("spellbook.present",(ROOT/"agents/yumeArtOni/GITHUB_SPELLBOOK.md").is_file()),
 ("taskTemplate.present",(ROOT/"agents/yumeArtOni/templates/bigBrotherArtTaskV1.template.json").is_file()),
 ("campaign.yume",campaign.get("creativeLead")=="yume"),
 ("campaign.bigBrother",campaign.get("providerAssist")=="bigBrother"),
 ("campaign.noAutoPosting","noAutomatedCrossPosting" in campaign.get("socialLaw",[])),
 ("truth.workstation",truth.get("yumeWorkstation",{}).get("contract")=="doctrine/yumeArtistWorkstationV1.json"),
 ("truth.campaign",truth.get("unifiedCampaignWorkbench",{}).get("contract")=="doctrine/unifiedCampaignWorkbenchV1.json"),
 ("control.artWorkbench",control.get("providerBoundary",{}).get("yumeArtWorkbench",{}).get("contract")=="doctrine/yumeBigBrotherArtDeskV1.json"),
 ("yume.workstation",yume.get("artistWorkstation")=="doctrine/yumeArtistWorkstationV1.json"),
 ("yume.spellbook",yume.get("githubSpellbook")=="agents/yumeArtOni/GITHUB_SPELLBOOK.md"),
 ("crown.stop",all(x.get("crownStatus")=="STOP" for x in [workstation,art,godot,campaign])),
]
failed=[n for n,o in checks if not o]
for i,(n,o) in enumerate(checks,1): print(f"{'PASS' if o else 'FAIL'} {i:02d}/{len(checks)} {n}")
if failed: raise SystemExit("YUME_WORKBENCH_AUDIT=RED failed="+",".join(failed))
print("YUME_WORKBENCH_AUDIT=GREEN")
print(f"passes={len(checks)}/{len(checks)}")
print("providerExecution=UNPROVEN_UNTIL_RECEIPT")
print("publication=STOP")
print("crown=STOP")
