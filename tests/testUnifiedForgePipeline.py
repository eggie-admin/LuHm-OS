#!/usr/bin/env python3
"""Source-only negative controls: Base64url, JSON, SQLite, mail isolation."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name,relative):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
forge=load("unifiedForgePipeline","tools/unifiedForgePipeline.py")
mail=load("ownerImapUnreadCheck","tools/ownerImapUnreadCheck.py")
SHA="a"*40

def sample(mode="headless"):
    return {"schema":"luhmOs.aiTaskManifest.v2","taskId":"test-1","sourceRef":SHA,
            "scopeId":"source-only","providerId":"local","capabilityId":"forgeSourceAudit",
            "status":"SOURCE_CANDIDATE","mode":mode,"tier":0,
            "budget":{"maxRequests":0,"maxParallel":0,"maxPasses":1},
            "authority":{"mutation":False,"green":False,"crown":False},
            "inputRefs":[],"requiredOutputSchema":"luhmOs.forgeSourceProjection.v1"}

class FakeIMAP:
    def __init__(self,*args,**kwargs):
        self.calls=[]
    def authenticate(self,kind,func):
        assert kind=="XOAUTH2"
        self.calls.append("auth")
        return ("OK",[b""])
    def select(self,folder,readonly=False):
        assert folder=="INBOX" and readonly
        self.calls.append("readonly-select")
        return ("OK",[b"3"])
    def search(self,*args):
        assert args==(None,"UNSEEN")
        self.calls.append("search")
        return ("OK",[b"11 12"])
    def logout(self):self.calls.append("logout")

class UnifiedForgeTests(unittest.TestCase):
    def test_all_four_routes(self):
        for mode in ("headless","witchingHour","corporate","githubDevelopment"):
            data=sample(mode)
            output=forge.project(forge.decode(forge.encode(data)),SHA)
            self.assertEqual(output["mode"],mode)
            self.assertFalse(output["workerExecuted"])
            self.assertEqual(output["sql"],"SQLITE_STRICT_JSON1_GREEN")

    def test_bad_source_rejected(self):
        data=sample();data["sourceRef"]="b"*40
        with self.assertRaises(ValueError):forge.project(data,SHA)

    def test_permission_escalation_rejected(self):
        data=sample();data["authority"]["mutation"]=True
        with self.assertRaises(ValueError):forge.validate(data,SHA)

    def test_runtime_provider_rejected(self):
        data=sample();data["providerId"]="openAi"
        with self.assertRaises(ValueError):forge.validate(data,SHA)

    def test_unknown_keys_rejected(self):
        data=sample();data["secret"]="oops"
        with self.assertRaises(ValueError):forge.validate(data,SHA)

    def test_duplicate_json_keys_rejected(self):
        malformed=b'{"a":1,"a":2}'
        import base64
        with self.assertRaises(ValueError):
            forge.decode(base64.urlsafe_b64encode(malformed).decode().rstrip("="))

    def test_base64url_not_encryption(self):
        payload=forge.encode(sample())
        self.assertNotIn("=",payload)
        self.assertEqual(forge.decode(payload),sample())

    def test_max_44_kib(self):
        with self.assertRaises(ValueError):
            forge.encode({"large":"a"*forge.MAX_BYTES})

    def test_tier_bool_not_integer(self):
        data=sample();data["tier"]=True
        with self.assertRaises(ValueError):forge.validate(data,SHA)

    def test_schema_contract_matches_validator(self):
        schema=json.loads((ROOT/"doctrine/fourSourceTask.schema.json").read_text())
        self.assertEqual(set(schema["required"]),set(sample()))
        self.assertFalse(schema["additionalProperties"])

    def test_mail_default_no_network_and_no_body_fetch(self):
        self.assertFalse(getattr(mail,"AUTO_RUN_ON_IMPORT",False))
        receipt=mail.check_unread("imap.example.test","owner@example.test","mock",
                                 client_factory=FakeIMAP)
        self.assertEqual(receipt["unreadCount"],2)
        self.assertFalse(receipt["bodyFetched"])
        self.assertFalse(receipt["mailMutated"])

if __name__=="__main__":
    unittest.main()
