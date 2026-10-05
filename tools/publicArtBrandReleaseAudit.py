#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
errors: list[str] = []

def need(ok: bool, msg: str) -> None:
    if not ok:
        errors.append(msg)

def load(path: str) -> dict:
    p = ROOT / path
    need(p.is_file(), f"missing {path}")
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}

brand = load("doctrine/organizationBrandRegistryV1.json")
art = load("doctrine/publicArtReleaseReadinessV1.json")
edge = load("doctrine/staticPublicEdgeV1.json")
ledger = load("media/public-release-art-ledger.json")
roleplay = load("doctrine/codingRoleplayDirectorV2.json")
truth = load("doctrine/currentSourceTruthV3.json")
campaign = load("doctrine/campaignLaunchKitV1.json")
plugin = load("doctrine/pluginPublicationV2.json")
trainer = load("doctrine/huggingFaceSpecialistTrainerV1.json")
estate = load("doctrine/godot4AssetEstateV1.json")
estate_ledger = load("media/godot4-game-asset-estate.json")
forge = load("doctrine/FORGE_TWINS_V3.json")
asset_architecture = load("doctrine/godot4AssetArchitectureDecisionV1.json")
asset_reconcile = load("media/godot4-asset-reconciliation-v1.json")
cast_ready = load("doctrine/publicReleaseCastReadinessV1.json")
canon = load("game/canon/CHARACTER_CANON_V1.json")
runtime_assets = load("game/assets/ASSET_MANIFEST_V1.json")

need(brand.get("authority") == "Professor", "brand authority drift")
need(brand.get("crownStatus") == "STOP", "brand Crown must STOP")
need(brand.get("publicationAuthority") is False, "brand publication authority must remain false")
need(set(brand.get("publicBrands", {})) >= {"luhmOs","eggieBagelface","pirateDaddiesFilm","bigDaddy"}, "public brand registry incomplete")
for alias in ("openDaddy","gitDaddy","samsungDaddy","bigBrother"):
    rec = brand.get("internalProviderRoleplay", {}).get(alias, {})
    need(rec.get("publicCoBrand") is False, f"{alias} must not be public co-brand")
    need(rec.get("officialAffiliationClaim") is False, f"{alias} must not imply official affiliation")

need(art.get("contentLane") == "cathedralPublic", "public art lane must be cathedralPublic")
need(art.get("publicationAuthority") is False, "art publication authority must remain false")
laws = set(art.get("assetCompletionLaw", []))
for law in (
    "generated_draft_is_private_only",
    "public_generative_ai_art_default_forbidden",
    "privateMutation_and_betaAfterDark_assets_never_satisfy_public_release",
    "provenance_and_hash_are_required",
):
    need(law in laws, f"missing public art law: {law}")

need(ledger.get("status") == "INVENTORY_NOT_COMPLETION_CLAIM", "ledger must not claim completion")
need(ledger.get("generatedDraftPublicAllowed") is False, "generated drafts cannot be public")
for character in ("lum","urd","belldandy","skuld"):
    need(character in ledger.get("characters", {}), f"missing public art character {character}")
    need(character in canon.get("characters", {}), f"character {character} absent from canon")
need(set(runtime_assets.get("characters", [])) >= {"lum","urd","belldandy","skuld"}, "runtime character slots drift")

need(edge.get("trafficController") == "cloudflare", "edge traffic controller drift")
need(edge.get("tls", {}).get("originTermination") == "RenderManagedTls", "origin TLS must be Render managed")
need(edge.get("tls", {}).get("manualCertbotOnPhone") is False, "phone certbot must remain false")
need(edge.get("tls", {}).get("manualLetsEncryptClientRequired") is False, "manual Let's Encrypt client must remain false")
need(edge.get("dnsBootstrap", {}).get("initialProxyMode") == "DNS_ONLY_FOR_RENDER_DOMAIN_VERIFICATION", "Render verification must start DNS-only")
need(edge.get("tls", {}).get("cloudflareWhenProxied", {}).get("preferredModeAfterValidOriginCertificateProof") == "FullStrict", "Cloudflare post-proof mode must prefer FullStrict")
for key, value in edge.get("liveMutation", {}).items():
    need(value is False, f"live mutation must remain false: {key}")
need(edge.get("crownStatus") == "STOP", "edge Crown must STOP")

pr = truth.get("publicReleaseReadiness", {})
need(pr.get("art") == "doctrine/publicArtReleaseReadinessV1.json", "source truth public art pointer drift")
need(pr.get("brandRegistry") == "doctrine/organizationBrandRegistryV1.json", "source truth brand pointer drift")
need(pr.get("staticEdge") == "doctrine/staticPublicEdgeV1.json", "source truth edge pointer drift")
need(pr.get("automaticPublication") is False, "source truth automatic publication must be false")
need(pr.get("publicationAuthority") is False, "source truth publication authority must be false")
need(pr.get("crownStatus") == "STOP", "source truth public release Crown must STOP")

presentation = roleplay.get("publicReleasePresentation", {})
need(presentation.get("contract") == "doctrine/publicArtReleaseReadinessV1.json", "roleplay public-release contract drift")
for law in (
    "roleplay_does_not_complete_missing_art",
    "generated_draft_does_not_become_publicAllowed",
    "internal_provider_nickname_does_not_imply_vendor_affiliation",
    "network_roleplay_does_not_mutate_dns_proxy_tunnel_or_certificates",
    "publish_candidate_is_not_published",
):
    need(law in presentation.get("law", []), f"missing roleplay law: {law}")
need(roleplay.get("bubbleLaw", {}).get("publicBrandingCannotEstablishAffiliation") is True, "roleplay affiliation guard missing")
need(roleplay.get("bubbleLaw", {}).get("networkBubbleCannotEstablishLiveDnsOrTls") is True, "roleplay network truth guard missing")

need(campaign.get("organizationBrandRegistry") == "doctrine/organizationBrandRegistryV1.json", "campaign brand registry pointer drift")
need(campaign.get("publicArtReleaseReadiness") == "doctrine/publicArtReleaseReadinessV1.json", "campaign art readiness pointer drift")
need(plugin.get("publicPresentation", {}).get("generatedPublicArtDefaultForbidden") is True, "plugin public generated-art guard missing")
need(plugin.get("networkActivation", {}).get("liveDnsMutation") is False, "plugin must not claim live DNS mutation")
need(plugin.get("networkActivation", {}).get("liveCertificateMutation") is False, "plugin must not claim live certificate mutation")

for path in (
    "agents/yumeArtOni/SKILL.md",
    "agents/belldandyQualityOni/SKILL.md",
    "agents/skuldResearchOni/SKILL.md",
    "agents/urdMutationOni/SKILL.md",
    "campaign/public-release-brand-readiness.md",
):
    need((ROOT / path).is_file(), f"missing cabinet/public release file {path}")



need(trainer.get("organizationalRole") == "specialistTrainer", "Hugging Face specialist trainer role drift")
need(trainer.get("reportsThrough") == "lum", "Hugging Face must route through Lum")
need(trainer.get("publicationAuthority") is False, "Hugging Face trainer may not publish")
need(trainer.get("crownStatus") == "STOP", "Hugging Face trainer Crown must STOP")
for law in (
    "specialist_trainer_does_not_replace_skuld_architecture",
    "specialist_trainer_does_not_replace_yume_art_direction",
    "specialist_trainer_does_not_replace_urd_sanity_and_evidence_adjudication",
    "specialist_trainer_does_not_replace_belldandy_records",
):
    need(law in trainer.get("operatingLaw", []), f"missing trainer role boundary: {law}")

role = art.get("roleDefinition", {})
need("art direction" in role.get("yume",""), "Yume role must be art direction")
need("architecture" in role.get("skuld",""), "Skuld role must own architecture")
need("sanity" in role.get("urd","") and "health" in role.get("urd",""), "Urd role must own sanity/health")
need("organization" in role.get("belldandy",""), "Belldandy role must own organization")
need("specialist trainer" in role.get("huggingFace",""), "Hugging Face role must be specialist trainer")
need("current doctrine and source truth" in role.get("lum",""), "Lum must operate against current doctrine/source truth")

need(estate.get("authority") == "Professor", "Godot asset estate authority drift")
need(estate.get("crownStatus") == "STOP", "Godot asset estate Crown must STOP")
need(estate.get("roles", {}).get("skuld","").startswith("choose and verify the sanest Godot architecture"), "Skuld Godot architecture role drift")
need(estate.get("roles", {}).get("belldandy","").startswith("maintain the canonical inventory"), "Belldandy estate records role drift")
need(estate.get("roles", {}).get("yume","").startswith("art direction"), "Yume estate art direction role drift")
need(estate.get("roles", {}).get("urd","").startswith("keep the estate sane and healthy"), "Urd estate sanity role drift")
need("folder_name_is_not_green" in estate.get("laws", []), "estate folder-name GREEN guard missing")
need(estate_ledger.get("status") == "DISCOVERED_INVENTORY_AUDIT_PENDING", "Godot asset estate ledger must remain audit pending")
need(estate_ledger.get("candidateScopeState") == "AMBER_ORIGINAL_ASSETS_HASHED_MORE_RECONCILIATION_REQUIRED", "Godot asset estate state drift")


need(forge.get("truthGuard", {}).get("adjudicator") == "urdDoctorGoddess", "Forge truth guard must be Urd")
need("URD_TRUTH_CHECK" in forge.get("workflow", []), "Forge workflow must use Urd truth check")
need("DR_NAO_TRUTH_CHECK" not in forge.get("workflow", []), "stale DrNao Forge workflow step remains")
need(forge.get("twins", {}).get("Tetsu", {}).get("allowedOperations") == ["PROTECT","INGEST","MUTATE","VERIFY","JANITOR"], "Tetsu source lane drift")
need(forge.get("twins", {}).get("Kaji", {}).get("allowedOperations") == ["PREPARE","CAST","BUILD","HASH","RECEIPT","JANITOR"], "Kaji compile lane drift")
need(forge.get("assetEstateIntegration", {}).get("sourceForgeOwner") == "Tetsu", "asset estate source forge drift")
need(forge.get("assetEstateIntegration", {}).get("compileForgeOwner") == "Kaji", "asset estate compile forge drift")
need(truth.get("forgeLayer", {}).get("truthGuard") == "urdDoctorGoddess", "source truth Forge guard drift")
need(truth.get("forgeLayer", {}).get("explicitSingleUseCastRequired") is True, "source truth CAST gate drift")


need(asset_architecture.get("owner") == "skuldResearch", "Skuld architecture owner drift")
need(asset_architecture.get("decisions", {}).get("threeDInterchange", {}).get("preferred") == "glTF 2.0 binary (.glb)", "Godot 3D interchange drift")
need(asset_architecture.get("decisions", {}).get("rigging", {}).get("secondaryMotion") == "SpringBoneSimulator3D first for bounded hair/cloth/tail/soft-chain motion", "secondary-motion architecture drift")
need(asset_architecture.get("decisions", {}).get("releaseSeparation", {}).get("eachScopeRequiresOwnCast") is True, "per-scope CAST law missing")
need(asset_reconcile.get("forge") == "Tetsu", "Tetsu reconciliation owner drift")
need(asset_reconcile.get("currentVerdict") == "AMBER_RECONCILIATION_ADVANCED_ORIGINAL_ASSETS_HASHED", "asset reconciliation state drift")
need(asset_reconcile.get("buildAllowed") is False, "asset estate build must remain blocked while AMBER")
need(cast_ready.get("status") == "AMBER_PRE_CAST", "public release CAST readiness state drift")
need(cast_ready.get("castReady") is False, "CAST readiness must remain false while asset reconciliation is AMBER")
need(cast_ready.get("exactCastSourceRef") == "PENDING_FINAL_CANDIDATE_HEAD", "CAST source must remain pending until final candidate")
need(cast_ready.get("compileForge") == "Kaji", "Kaji compile forge drift")
need(cast_ready.get("sourceForge") == "Tetsu", "Tetsu source forge drift")
need(cast_ready.get("currentGates", {}).get("godotAssetEstate") == "AMBER_RECONCILIATION_ADVANCED_ORIGINAL_ASSETS_HASHED", "CAST gate asset estate state drift")
need(truth.get("gameLayer", {}).get("assetArchitecture") == "doctrine/godot4AssetArchitectureDecisionV1.json", "source truth asset architecture pointer drift")
need(truth.get("gameLayer", {}).get("assetReconciliation") == "media/godot4-asset-reconciliation-v1.json", "source truth asset reconciliation pointer drift")
need(truth.get("gameLayer", {}).get("buildAllowedFromAssetEstate") is False, "source truth must block build while asset estate remains AMBER")

if errors:
    print("RED_PUBLIC_ART_BRAND_RELEASE_AUDIT")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("GREEN_PUBLIC_ART_BRAND_RELEASE_SOURCE")
print("publicationAuthority=false")
print("liveDnsMutation=false")
print("liveCertificateMutation=false")
print("generatedPublicArt=false")
print("crownStatus=STOP")
