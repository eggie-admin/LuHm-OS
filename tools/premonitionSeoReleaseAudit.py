#!/usr/bin/env python3
"""Read-only SEO and release discoverability gate for LuHm Project Premonition.

Audits the proposed publication site, tags, OG/Twitter text cards, release
flags and noindex mock-up. Does not run a crawler, publish, submit sitemaps,
create GitHub releases/tags, or touch domain/Render/DNS accounts.
"""
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/premonitionPublicDiscoveryV1.json"
BRAND = ROOT / "doctrine/organizationBrandRegistryV1.json"
RELEASE = ROOT / "doctrine/premonitionEnterpriseBrandV1.json"
QUARANTINE = ROOT / "doctrine/companyWideOperationalQuarantineV1.json"
STATIC = ROOT / "publicationSite"

EXPECTED_ROUTES = (
    "/", "/release.html", "/tester.html", "/pocketLab.html",
    "/support.html", "/privacy.html", "/terms.html"
)
EXPECTED_FLAGS = (
    "publicRelease", "activateSitemap", "submitIndexing", "marketing",
    "enableAppDownloads", "socialImageApproved", "merge", "deploy"
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_text = ""
        self._title_open = False
        self.headings: list[str] = []
        self.meta: list[dict[str, str]] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): v or "" for k, v in attrs}
        if tag == "title":
            self._title_open = True
        if tag == "h1":
            self.headings.append("h1")
        if tag == "meta":
            self.meta.append(a)
        if tag in ("a", "link") and a.get("href"):
            self.links.append(a["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._title_open = False

    def handle_data(self, data: str) -> None:
        if self._title_open:
            self.title_text += data


def _load(path: Path) -> dict[str, Any]:
    x = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(x, dict):
        raise ValueError("RED_SEO_POLICY_SHAPE")
    return x


def _meta(page: PageParser, key: str, value: str) -> list[str]:
    return [x.get("content", "") for x in page.meta if x.get(key) == value]


def parse_page(source: str) -> PageParser:
    result = PageParser()
    result.feed(source)
    result.close()
    return result


def _local_link_target(href: str) -> Path | None:
    if not href.startswith("/") or href.startswith("//"):
        return None
    if "?" in href or "#" in href or "\\" in href or ".." in href:
        return STATIC / "__invalid_static_link__"
    target = href.lstrip("/") or "index.html"
    return STATIC / target


def audit() -> dict[str, Any]:
    issues: list[str] = []
    policy = _load(POLICY)
    if policy.get("schema") != "luhmOs.premonitionPublicDiscovery.v1":
        issues.append("RED_SEO_CONTRACT")
    brand = policy.get("brand", {})
    current = _load(BRAND).get("publicBrands", {}).get("luhmOs", {})
    release = _load(RELEASE)
    if (brand != {"product":"LuHm-OS", "project":"Project Premonition",
                  "publisher":"Eggie Bagelface", "legacy":"Project Hydra"}
        or current.get("displayName") != brand.get("product")
        or current.get("publisher") != brand.get("publisher")
        or current.get("currentProject") != brand.get("project")
        or release.get("state") != "SOURCE_INTEGRATED_NOT_PUBLICLY_RELEASED"
        or release.get("authorizations", {}).get("publicMarketing") is not False):
        issues.append("RED_SEO_BRAND_AND_RELEASE_TRUTH")
    source = policy.get("canonicalSource", {})
    if (source.get("repo") != "eggie-admin/LuHm-OS"
            or source.get("branch") != "main"
            or source.get("publicationBranch") !=
            "publication/plugin-full-green-20260930"):
        issues.append("RED_SEO_GITHUB_SOURCE")
    origin = policy.get("canonicalWebsite", {})
    if (origin.get("origin") is not None or origin.get("tlsVerified") is not False
            or origin.get("publicDeployedSha") is not None
            or origin.get("searchConsoleVerified") is not False):
        issues.append("RED_SEO_UNVERIFIED_HOST")
    flags = policy.get("flags", {})
    if any(flags.get(k) is not False for k in EXPECTED_FLAGS):
        issues.append("RED_SEO_UNAPPROVED_RELEASE_FLAG")
    rules = policy.get("rules", {})
    for k in (
        "noUnverifiedCanonical", "noAutoIndex", "noAutoReleases",
        "previewNoindex", "preserveExistingAlphaIndexing",
        "structuredDataAfterOriginProof", "sitemapAfterApproval",
        "neverIndexPrivateMedia", "marketingNeedsRights",
        "noRankingGuarantees"
    ):
        if rules.get(k) is not True:
            issues.append("RED_SEO_SAFETY_RULES")
            break
    actual_pages = policy.get("pages")
    if not isinstance(actual_pages, list) or tuple(
            p.get("path") for p in actual_pages if isinstance(p, dict)) != EXPECTED_ROUTES:
        issues.append("RED_SEO_ROUTE_REGISTRY")
        actual_pages = []
    inspected = []
    for row in actual_pages:
        route = row["path"]
        fname = "index.html" if route == "/" else route[1:]
        path = STATIC / fname
        if not path.is_file():
            issues.append("RED_SEO_PAGE_MISSING")
            continue
        html = path.read_text(encoding="utf8")
        page = parse_page(html)
        if (not page.title_text.strip() or
                page.title_text.strip() != row.get("title") or
                len(page.headings) != 1 or
                not page.title_text.lower().count("luhm-os") == 1):
            issues.append("RED_SEO_TITLE_OR_H1_" + fname)
        desc = _meta(page, "name", "description")
        if len(desc) != 1 or not 45 <= len(desc[0]) <= 240:
            issues.append("RED_SEO_DESCRIPTION_" + fname)
        if (_meta(page, "name", "keywords") or
                _meta(page, "property", "og:url") or
                _meta(page, "property", "og:image") or
                _meta(page, "name", "twitter:image")):
            issues.append("RED_SEO_UNAPPROVED_PROMOTION_" + fname)
        if any(x.get("rel") == "canonical" for x in page.meta):
            issues.append("RED_SEO_INVALID_CANONICAL_" + fname)
        for href in page.links:
            if href.startswith("/"):
                target = _local_link_target(href)
                if target is None or not target.is_file():
                    issues.append("RED_SEO_BROKEN_LOCAL_LINK_" + fname)
        inspected.append({
            "page": route,
            "titleSha256": hashlib.sha256(page.title_text.encode("utf8")).hexdigest(),
            "descriptionLength": len(desc[0]) if len(desc) == 1 else 0,
            "h1Count": len(page.headings)
        })
    home = parse_page((STATIC / "index.html").read_text(encoding="utf8"))
    social = policy.get("social", {})
    for field, key, want in (
        ("property", "og:type", "website"),
        ("property", "og:site_name", "LuHm-OS"),
        ("property", "og:title", actual_pages[0].get("title") if actual_pages else ""),
        ("name", "twitter:card", "summary")
    ):
        if _meta(home, field, key) != [want]:
            issues.append("RED_SEO_SOCIAL_TAGS_" + key)
    if (social.get("imageUrl") is not None
            or social.get("graphicApprovedForNewRelease") is not False
            or social.get("sourceMark") != "publicationSite/logo.svg"
            or social.get("preview") != "publicationSite/share-card-preview.html"):
        issues.append("RED_SEO_SOCIAL_ART_RIGHTS")
    preview = STATIC / "share-card-preview.html"
    if not preview.is_file():
        issues.append("RED_SEO_PREVIEW_ABSENT")
    else:
        card = parse_page(preview.read_text(encoding="utf8"))
        directives = _meta(card, "name", "robots")
        if len(directives) != 1 or "noindex" not in directives[0].split(",")[0]:
            issues.append("RED_SEO_PREVIEW_INDEXABLE")
    q = _load(QUARANTINE)
    if q.get("state") != "QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False:
        issues.append("RED_SEO_QUARANTINE")
    # robots and sitemap must not be added to a public static origin blindly.
    for candidate in ("sitemap.xml", "robots.txt"):
        if (STATIC / candidate).is_file():
            issues.append("RED_SEO_PREMATURE_" + candidate)
    return {
        "schema":"luhmOs.premonitionPublicDiscoveryAudit.v1",
        "state":"SOURCE_METADATA_STAGED_ONLY" if not issues else "RED_SOURCE_DRIFT",
        "issues":sorted(set(issues)),
        "inspectedPages":inspected,
        "pageCount":len(inspected),
        "brandedSocialPreviewSource":preview.is_file(),
        "socialImageRasterApproved":False,
        "canonicalOriginVerified":False,
        "searchConsoleVerified":False,
        "sitemapEmitted":False,
        "publicationAuthorized":False,
        "liveCrawlProven":False,
        "googleIndexingProven":False,
        "productionGitTagCreated":False,
        "networkCalls":0,
        "greenAuthority":False,
        "crownAuthority":False
    }


def proposed_sitemap() -> dict[str, Any]:
    """Hold plan only. No fabricated absolute site URL or sitemap file."""
    base = audit()
    if base["issues"]:
        return {"state":"STOP_SOURCE_DRIFT","issues":base["issues"]}
    return {
        "schema":"luhmOs.premonitionIndexPlan.v1",
        "state":"HOLD_PUBLIC_ORIGIN_RIGHTS_AND_RELEASE_APPROVAL",
        "candidatePaths":[p["page"] for p in base["inspectedPages"]],
        "canonicalOrigin":None,
        "actualXmlSitemapGenerated":False,
        "robotsTxtPublished":False,
        "searchConsoleSubmitted":False,
        "needed":["trustedProductionOriginTls","actualPublishedSourceRef",
                  "brandAndSocialArtApproval","publicFeatureClaimsAndLegalReview",
                  "ProfessorExactReleaseAuthorization"],
        "greenAuthority":False,"crownAuthority":False
    }


if __name__=="__main__":
    print(json.dumps(audit(),indent=2))
