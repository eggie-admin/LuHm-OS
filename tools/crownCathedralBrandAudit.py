#!/usr/bin/env python3
"""Crown Cathedral brand consistency source gate.

Uses only Python stdlib and checked-out public repository files. Does not
approve art, publish social posts, change ChatGPT host, or grant Crown.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = {
    "brand": "doctrine/brandCanonV1.json",
    "characters": "doctrine/characterCanonRegistryV1.json",
    "widgets": "doctrine/widgetSystemCanonV1.json",
    "motion": "doctrine/motionBrandCanonV1.json",
    "vault": "doctrine/publicPrivateBrandVaultV1.json",
    "assets": "doctrine/brandAssetRegistryV1.json",
    "organization": "doctrine/organizationBrandRegistryV1.json",
    "canonCast": "game/canon/CHARACTER_CANON_V1.json",
    "lanes": "doctrine/contentLaneDoctrineV1.json",
    "dock": "doctrine/glassPluginDockV1.json",
    "plugin": "plugins/luhm-os/plugin.json"
}
NAMES = {"publisher": "Eggie Bagelface", "studio": "PIRATE DADDIES FILM",
         "product": "LuHm-OS", "world": "Project Premonition"}
CAST = {"lum", "urd", "belldandy", "skuld"}
GLASS = {"music", "avatars", "yume", "social", "admin"}


def inspect(j: dict, site_logo: str, plugin_logo: str, html: str, license_text: str) -> list[str]:
    problems: list[str] = []
    def need(ok: bool, code: str) -> None:
        if not ok:
            problems.append(code)
    b, c, w, m, v, a = (j[k] for k in ("brand", "characters", "widgets", "motion", "vault", "assets"))
    org, canon, lanes, dock, plugin = (j[k] for k in ("organization", "canonCast", "lanes", "dock", "plugin"))
    for key, obj, schema in [
        ("brand", b, "luhmOs.brandCanon.v1"),
        ("characters", c, "luhmOs.characterCanonRegistry.v1"),
        ("widgets", w, "luhmOs.widgetSystemCanon.v1"),
        ("motion", m, "luhmOs.motionBrandCanon.v1"),
        ("vault", v, "luhmOs.publicPrivateBrandVault.v1"),
        ("assets", a, "luhmOs.brandAssetRegistry.v1")
    ]:
        need(obj.get("schema") == schema and obj.get("authority") == "Professor"
             and obj.get("crownStatus") == "STOP", "contract:" + key)
        need(obj.get("status", "").startswith(("PROPOSED", "REQUIRED")),
             "candidateOnly:" + key)
        need(obj.get("publicationAuthority") is not True, "noSilentPublication:" + key)

    ids = b.get("identity", {})
    for role, name in NAMES.items():
        need(ids.get(role, {}).get("display") == name, "identity:" + role)
    org_public = org.get("publicBrands", {})
    for key, name in [("eggieBagelface", NAMES["publisher"]),
                      ("pirateDaddiesFilm", NAMES["studio"]),
                      ("luhmOs", NAMES["product"])]:
        need(org_public.get(key, {}).get("displayName") == name,
             "existingRegistry:" + key)
    need(ids.get("product", {}).get("parent") == "eggieBagelface" and
         ids.get("world", {}).get("parent") == "luhmOs" and
         b.get("extensionLaw", {}).get("legacyReceiptsNeverRewritten") is True,
         "evergreenHierarchy")
    need(b.get("visualSystem", {}).get("sourceMark", {}).get("path") ==
         "publicationSite/logo.svg" and
         b.get("visualSystem", {}).get("pluginMark", {}).get("path") ==
         "plugins/luhm-os/assets/logo.svg" and
         site_logo == plugin_logo and "<svg" in site_logo, "actualLogoSource")
    need(plugin.get("extensions", {}).get("com.openai", {}).get("interface", {}).get("brandColor") ==
         b.get("visualSystem", {}).get("currentExistingTokens", {}).get("pluginBrandColor"),
         "existingPluginColor")
    need(license_text.lstrip().startswith("GNU GENERAL PUBLIC LICENSE") and
         plugin.get("license") == "GPL-3.0-only", "licenseTruth")
    need(set(c.get("canonicalGameCast", {})) == CAST and
         CAST == set(canon.get("characters", {})), "oneCanonicalGameCast")
    need(c.get("rules", {}).get("oneCanon") is not False and
         c.get("technicalRules", {}).get("privateSourceNeverPublic") is True and
         c.get("technicalRules", {}).get("unknownRightsBlockPublic") is True,
         "characterSourcePrivacy")
    need(c.get("technicalRules", {}).get("blenderMasterPrivate") is True and
         "GLB" in c.get("technicalRules", {}).get("format3d", ""),
         "blenderGodotPipeline")
    need(set(w.get("moduleFamilies", {})) >= GLASS and
         GLASS == {x.get("id") for x in dock.get("modules", [])},
         "glassModulesPreserved")
    need("data-luhm-cockpit" in html and
         "data-luhm-asset-factory" in html and
         w.get("hostBoundary", {}).get("pageWideOverlay") is False and
         w.get("hostBoundary", {}).get("readOnlyByDefault") is True,
         "realCockpitAndHostBoundary")
    need(w.get("proof", {}).get("hostWidgetMount") == "UNVERIFIED" and
         w.get("publicationAuthority") is False, "noFakeHostProof")
    need(m.get("completedFinalVideo") is False and
         m.get("publicUploadAuthority") is False and
         m.get("renderLaw", {}).get("musicRights") ==
         "VERIFY_TRACK_OR_COMMISSION_OR_LICENSE_BEFORE_PUBLIC", "videoRightsGate")
    need(set(v.get("lanes", {})) == set(lanes.get("lanes", {})) ==
         {"privateMutation", "betaAfterDark", "cathedralPublic"},
         "reuseActualThreeContentLanes")
    need(v.get("lanes", {}).get("privateMutation", {}).get("canPublish") is False and
         v.get("lanes", {}).get("betaAfterDark", {}).get("canPublish") is False and
         v.get("lanes", {}).get("cathedralPublic", {}).get("canPublish", "").startswith("ONLY_AFTER"),
         "privatePublicFirewall")
    need(all(v.get("migration", {}).get(k) is False for k in
             ("autoDelete", "autoArchive", "autoEdit", "autoPost")),
         "nondestructivePortfolioRestoration")
    need(v.get("crown", {}).get("designSystemRatified") is False and
         v.get("crown", {}).get("eachPostSeparateApproval") is True,
         "noCrownPromotion")
    need(a.get("publishing", {}).get("oneParentMasterManyDerivatives") is True and
         a.get("publishing", {}).get("publicAssetRequiresLicenseAndExplicitHumanReview") is True,
         "assetMasterLineage")
    need({x.get("id") for x in a.get("requiredBrands", [])} ==
         {"luhmOs", "eggieBagelface", "pirateDaddiesFilm", "bigDaddy"} and
         all(x.get("publicApproved") is False for x in a.get("existingCandidateSources", [])),
         "noFakeFinishedBrandAssets")
    need(b.get("approvalRecord", {}).get("finalPublicAssetApproval") ==
         "PER_ASSET_PENDING" and
         b.get("proof", {}).get("publicProfilesUpdated") is False and
         b.get("publicationAuthority") is False, "ownerReleaseAuthority")
    return problems


def main() -> None:
    j = {key: json.loads((ROOT / path).read_text(encoding="utf-8"))
         for key, path in CONTRACTS.items()}
    site_logo = (ROOT / "publicationSite/logo.svg").read_text(encoding="utf-8")
    plugin_logo = (ROOT / "plugins/luhm-os/assets/logo.svg").read_text(encoding="utf-8")
    html = (ROOT / "frontEnd/index.html").read_text(encoding="utf-8")
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    baseline = (j, site_logo, plugin_logo, html, license_text)
    errors = inspect(*baseline)
    if errors:
        raise SystemExit("RED_CROWN_BRAND_CANON:" + ",".join(errors))
    negatives: list[tuple[str, tuple]] = []
    def alter(label: str, key: str, mutate) -> None:
        sample = deepcopy(j)
        mutate(sample[key])
        negatives.append((label, (sample, site_logo, plugin_logo, html, license_text)))
    alter("renameProduct", "brand", lambda x: x["identity"]["product"].update(display="LuHm OS X"))
    alter("fakeCrown", "brand", lambda x: x.update(crownStatus="GREEN"))
    alter("fakePublicLogo", "assets", lambda x: x["existingCandidateSources"][0].update(publicApproved=True))
    alter("privateAutoPost", "vault", lambda x: x["migration"].update(autoPost=True))
    alter("dropBetaAfterDark", "vault", lambda x: x["lanes"].pop("betaAfterDark"))
    alter("fakeChatGptHost", "widgets", lambda x: x["proof"].update(hostWidgetMount="PROVEN"))
    alter("unlicensedVideo", "motion", lambda x: x["renderLaw"].update(musicRights="SKIP"))
    alter("missingCanonicalCast", "characters", lambda x: x["canonicalGameCast"].pop("skuld"))
    negatives.append(("mismatchedLogo", (j, site_logo, "<svg/>", html, license_text)))
    negatives.append(("fakeLicense", (j, site_logo, plugin_logo, html,
                                      "Apache License Version 2.0")))
    for label, args in negatives:
        if not inspect(*args):
            raise SystemExit("RED_CROWN_BRAND_FALSE_GREEN:" + label)
    print("GREEN_CROWN_CATHEDRAL_BRAND_SOURCE_10_NEGATIVE_CONTROLS")
    print("SOURCE_ONLY: brand visual approvals, public post changes, 3D models, and ChatGPT host unproven")


if __name__ == "__main__":
    main()
