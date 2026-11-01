#!/usr/bin/env python3
"""Strict source-only SEO, cards, tags and indexing readiness tests."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "premonitionSeoReleaseAudit",ROOT/"tools/premonitionSeoReleaseAudit.py")
assert spec and spec.loader
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class TestPremonitionPublicDiscovery(unittest.TestCase):
    def test_existing_public_alpha_pages_have_distinct_brand_metadata(self):
        status=gate.audit()
        self.assertEqual(status["state"],"SOURCE_METADATA_STAGED_ONLY",status["issues"])
        self.assertEqual(status["pageCount"],7)
        self.assertTrue(status["brandedSocialPreviewSource"])
        self.assertEqual(len({
            p["titleSha256"] for p in status["inspectedPages"]
        }),7)
        self.assertFalse(status["googleIndexingProven"])
        self.assertFalse(status["publicationAuthorized"])
        self.assertFalse(status["crownAuthority"])

    def test_no_unverified_canonical_or_social_image_or_sitemap_submission(self):
        plan=gate.proposed_sitemap()
        self.assertEqual(plan["state"],"HOLD_PUBLIC_ORIGIN_RIGHTS_AND_RELEASE_APPROVAL")
        self.assertEqual(len(plan["candidatePaths"]),7)
        self.assertIsNone(plan["canonicalOrigin"])
        self.assertFalse(plan["actualXmlSitemapGenerated"])
        self.assertFalse(plan["searchConsoleSubmitted"])
        self.assertFalse(plan["greenAuthority"])
        homepage=gate.parse_page((ROOT/"publicationSite/index.html").read_text())
        self.assertEqual(gate._meta(homepage,"property","og:site_name"),["LuHm-OS"])
        self.assertEqual(gate._meta(homepage,"name","twitter:card"),["summary"])
        self.assertEqual(gate._meta(homepage,"property","og:image"),[])

    def test_site_robots_directives_are_in_preview_only(self):
        preview=gate.parse_page(
            (ROOT/"publicationSite/share-card-preview.html").read_text())
        self.assertEqual(
            gate._meta(preview,"name","robots"),["noindex, nofollow, noarchive"])
        self.assertEqual(gate._local_link_target("/logo.svg"),
                         ROOT/"publicationSite/logo.svg")
        self.assertFalse((ROOT/"publicationSite/sitemap.xml").is_file())

    def test_all_release_flags_locked_and_canonical_missing(self):
        original=gate._load
        def forged(path):
            item=original(path)
            if path==gate.POLICY:
                item=copy.deepcopy(item)
                item["flags"]["publicRelease"]=True
                item["canonicalWebsite"]["origin"]="https://unknown.invalid"
                item["social"]["imageUrl"]="https://example.invalid/unproved.png"
            return item
        with patch.object(gate,"_load",side_effect=forged):
            result=gate.audit()
        self.assertIn("RED_SEO_UNAPPROVED_RELEASE_FLAG",result["issues"])
        self.assertIn("RED_SEO_UNVERIFIED_HOST",result["issues"])
        self.assertIn("RED_SEO_SOCIAL_ART_RIGHTS",result["issues"])

    def test_no_duplicate_routes_or_metadata_keyword_spam(self):
        original=gate._load
        def forged(path):
            item=original(path)
            if path==gate.POLICY:
                item=copy.deepcopy(item)
                item["pages"][1]["path"]="/"
            return item
        with patch.object(gate,"_load",side_effect=forged):
            result=gate.audit()
        self.assertIn("RED_SEO_ROUTE_REGISTRY",result["issues"])
        self.assertEqual(result["state"],"RED_SOURCE_DRIFT")

    def test_internal_link_traversal_refused(self):
        for path in ("/../.env","/release.html?code=private",
                     "/%2e%2e/.env","/release.html#frag"):
            candidate=gate._local_link_target(path)
            self.assertFalse(candidate is not None and candidate.is_file())


if __name__=="__main__":
    unittest.main()
