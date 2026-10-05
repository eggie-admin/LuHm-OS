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
