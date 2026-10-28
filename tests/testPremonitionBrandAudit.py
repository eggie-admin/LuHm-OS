#!/usr/bin/env python3
"""Brand contract negative tests, no network, installer or signing required."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("brandAudit",ROOT/"tools/premonitionBrandAudit.py")
brand=importlib.util.module_from_spec(spec);spec.loader.exec_module(brand)
class BrandTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.p=brand.load("doctrine/premonitionEnterpriseBrandV1.json")
    cls.r=brand.load("doctrine/organizationBrandRegistryV1.json")
    cls.c=brand.load("doctrine/projectChatCanonV1.json")
    cls.f=(ROOT/"tools/prepareFdroidRepoCandidate.py").read_text()
    cls.rd=(ROOT/"README.md").read_text()
    cls.memo=(ROOT/"manual/premonition-funding-one-pager.md").read_text()
  def verdict(self,p=None,r=None,c=None,f=None,rd=None,memo=None):
    return brand.evaluate(p or self.p,r or self.r,c or self.c,
      f if f is not None else self.f,rd if rd is not None else self.rd,
      memo if memo is not None else self.memo)
  def testCurrentCanonIsOnlySourceGreen(self):
    self.assertEqual(self.verdict(),[])
    self.assertEqual(self.p["crownStatus"],"STOP")
  def testBadCaseRejected(self):
    r=json.loads(json.dumps(self.r));r["publicBrands"]["luhmOs"]["displayName"]="LumOS"
    self.assertIn("REGISTRY_PRODUCT",self.verdict(r=r))
  def testFDRoidNameCannotDrift(self):
    self.assertIn("FDROID_METADATA_BRAND",self.verdict(f=self.f.replace("LuHm-OS: Project Premonition Beta","LuHm OS Tablet Beta")))
  def testAppIdentityNeverSilentlyChanges(self):
    self.assertIn("PACKAGE_ID_UNCHANGED",self.verdict(f=self.f.replace("art.eggiebagelface.luhmos.beta","art.eggiebagelface.luhmos.production")))
  def testFundingDraftCannotClaimRelease(self):
    p=json.loads(json.dumps(self.p));p["authorizations"]["publicMarketing"]=True
    self.assertIn("NO_AUTOMATIC_RELEASE_publicMarketing",self.verdict(p=p))
  def testHistoricalNamesRemainsValid(self):
    c=json.loads(json.dumps(self.c));c["bootstrapTrigger"]["projectNames"].remove("LuHm OS")
    self.assertIn("LEGACY_ALIAS",self.verdict(c=c))
if __name__=="__main__":unittest.main()
