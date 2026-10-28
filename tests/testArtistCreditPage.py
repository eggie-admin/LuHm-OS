#!/usr/bin/env python3
"""Fail-closed artist-credit tests for LuHm game about page."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"tools/buildArtistCreditsPage.py"
spec=importlib.util.spec_from_file_location("buildArtistCreditsPage",MODULE)
page=importlib.util.module_from_spec(spec)
spec.loader.exec_module(page)


def approvedAsset():
    return {
        "assetId":"test-source-asset","assetTitle":"Candle Crown",
        "creatorDisplayName":"Example Studio","requestedCreditString":"Artwork by Example Studio",
        "creatorUrlWhenPublic":"https://artist.example/work",
        "license":"CC-BY-4.0","licenseUrlOrFile":"https://creativecommons.org/licenses/by/4.0/",
        "sourceUrl":"https://artist.example/candle-crown","sourceHash":"a"*64,
        "publicAllowed":True,"rightsReviewed":True,"professorArtApproval":True,
        "reviewState":"runtimeImportProven","contentLane":"cathedralPublic",
    }


def mockRecords(used=None):
    return (
        {"schema":"luhmOs.artistCreditsApproved.v1","approvedAssets":used or []},
        {"scope":"referenceCatalogOnly","cards":[{"id":"ref1","title":"Sketch study","creator":"Some Artist",
                                                   "url":"https://sketchfab.com/3d-models/example","kind":"Reference"}]},
        {"schema":"luhmOs.artistCreditLedger.v1"}
    )


class ArtistCreditPageTests(unittest.TestCase):
    def test_current_candidate_has_no_false_claims_about_used_art(self):
        index=page.buildIndex(
            json.loads(page.APPROVED.read_text()),
            json.loads(page.REFERENCE.read_text()),
            json.loads(page.DOCTRINE.read_text()))
        self.assertEqual(len(index["used"]),0)
        self.assertGreater(len(index["references"]),0)
        self.assertTrue(all(r["scope"]=="researchReferenceNotUsed" for r in index["references"]))
        self.assertTrue(index["noTracking"])
        self.assertTrue(index["noRuntimeDownloads"])

    def test_valid_exact_asset_receipt_generates_credit(self):
        a,r,d=mockRecords([approvedAsset()])
        index=page.buildIndex(a,r,d)
        self.assertEqual(index["used"][0]["credit"],"Artwork by Example Studio")
        self.assertEqual(index["references"][0]["creator"],"Some Artist")

    def test_unapproved_asset_rejected_even_when_creator_known(self):
        for field in ("publicAllowed","rightsReviewed","professorArtApproval"):
            candidate=approvedAsset()
            candidate[field]=False
            a,r,d=mockRecords([candidate])
            with self.subTest(field=field),self.assertRaises(ValueError):
                page.buildIndex(a,r,d)

    def test_private_lane_and_rough_art_rejected(self):
        for key,value in (("contentLane","privateMutation"),("reviewState","candidateReview")):
            a=approvedAsset()
            a[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                page.buildIndex(*mockRecords([a]))

    def test_unchecked_license_or_missing_sha_rejected(self):
        for key,value in (("license","UNKNOWN"),("sourceHash","not-sha-256"),
                          ("licenseUrlOrFile","not-a-license-file")):
            a=approvedAsset()
            a[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                page.buildIndex(*mockRecords([a]))

    def test_duplicate_credit_asset_rejected(self):
        a=approvedAsset()
        with self.assertRaises(ValueError):
            page.buildIndex(*mockRecords([a,copy.deepcopy(a)]))

    def test_malicious_source_link_rejected(self):
        for url in ("javascript:alert(1)","https://person@example.com/page","http://artist.example/asset"):
            a=approvedAsset()
            a["sourceUrl"]=url
            with self.subTest(url=url),self.assertRaises(ValueError):
                page.buildIndex(*mockRecords([a]))

    def test_reference_url_and_origin_must_be_known(self):
        a,r,d=mockRecords()
        r["cards"][0]["url"]="https://malicious.example/cat"
        with self.assertRaises(ValueError):
            page.buildIndex(a,r,d)

    def test_render_escapes_html_in_json_script(self):
        a,r,d=mockRecords()
        r["cards"][0]["title"]='Look</script><script>alert("x")</script>'
        doc=page.renderPage(page.buildIndex(a,r,d))
        self.assertNotIn('</script><script>alert',doc)
        self.assertIn("\\u003c/script",doc)
        self.assertIn('Credits',doc)

    def test_no_external_js_or_external_vector_service(self):
        doc=page.renderPage(page.buildIndex(*mockRecords()))
        self.assertIn('type="application/json"',doc)
        self.assertNotIn('<script src=',doc)
        self.assertNotIn('https://cdn.',doc)


if __name__=="__main__":
    unittest.main()
