#!/usr/bin/env python3
import copy
import hashlib
import json
import unittest
from tools import castTypedHexBoundaries as gate

class TestCastTypedHexBoundaries(unittest.TestCase):
    def setUp(self):
        self.config=json.loads(gate.CONTRACT.read_text(encoding="utf-8"))

    def testActualFourByFourContract(self):
        result=gate.validate(self.config)
        self.assertEqual(result["cellsMapped"],16)
        self.assertEqual(result["planned8x8RuntimeVerified"],0)
        self.assertEqual(result["activeWorkers"],0)
        self.assertEqual(result["crownStatus"],"STOP")

    def testHexCellsExactlyOneNibble(self):
        self.assertEqual(len(set(gate.logical_cell(r,c) for r in range(4) for c in range(4))),16)
        self.assertEqual(gate.logical_cell(0,0),"0x00")
        self.assertEqual(gate.logical_cell(3,3),"0x0F")
        for values in ((4,0),(-1,0),(0,4),(False,0),(0,2.0)):
            with self.subTest(values=values),self.assertRaises(gate.BoundaryError):
                gate.logical_cell(*values)

    def testSourceSyntaxDigestAndClassNoAuthority(self):
        raw=b"synthetic sample"
        digest=hashlib.sha256(raw).hexdigest()
        proof=gate.receipt_flags(self.config["basedOnMain"],raw,digest,"firmwareTrust")
        self.assertEqual(proof["auditFlags"],"0x07")
        self.assertFalse(proof["cryptographicSignatureVerified"])
        self.assertFalse(proof["humanReleaseAuthorized"])
        self.assertFalse(proof["kernelPolicyEnforced"])

    def testDigestMismatchRejected(self):
        with self.assertRaisesRegex(gate.BoundaryError,"DIGEST_NOT_MATCHED"):
            gate.receipt_flags(self.config["basedOnMain"],b"fixture","0"*64,"firmwareTrust")

    def testUnknownOrMalformedDigestTypesRejected(self):
        for key,value in (("source","0"*64),("source","zz"*20),("source",42)):
            with self.subTest(key=key,value=value),self.assertRaises(gate.BoundaryError):
                gate.receipt_flags(value,b"fixture",hashlib.sha256(b"fixture").hexdigest(),"kernelIsolation")
        with self.assertRaisesRegex(gate.BoundaryError,"SHA256_DIGEST"):
            gate.receipt_flags(self.config["basedOnMain"],b"fixture","ff"*20,"networkScope")

    def testNoSignatureFromHash(self):
        bad=copy.deepcopy(self.config)
        bad["integrity"]["sha256DigestIsSignature"]=True
        with self.assertRaisesRegex(gate.BoundaryError,"SIGNATURE_CONFLATION"):
            gate.validate(bad)

    def testNoECDSAAuthorityExpansion(self):
        bad=copy.deepcopy(self.config)
        bad["typedIdentities"]["ecdsa"]="AutomaticEscalationAuthority"
        with self.assertRaisesRegex(gate.BoundaryError,"ECDSA_MISINTERPRETATION"):
            gate.validate(bad)

    def testNoIPv6SubnetAsAuthz(self):
        bad=copy.deepcopy(self.config)
        bad["network"]["ipv6PrefixDoesNotAuthorizeTraffic"]=False
        with self.assertRaisesRegex(gate.BoundaryError,"IPV6_AUTHORIZATION_CONFLATION"):
            gate.validate(bad)

    def testIpv6StrictNoIpv4AndNoZones(self):
        self.assertEqual(gate.ipv6_network("2001:db8::/32")["addressBits"],128)
        for prefix in ("127.0.0.1/8","2001:db8::1/32","fe80::1%eth0/64","invalid",42):
            with self.subTest(prefix=prefix),self.assertRaises(gate.BoundaryError):
                gate.ipv6_network(prefix)

    def testRejectFalseRuntimeAndReleaseClaims(self):
        for field,value in (("hasLiveDeviceProof",True),("activeAgentWorkers",1),
                            ("firmwareChanged",True),("networkChanged",True),
                            ("mutationsPerformed",True)):
            with self.subTest(field=field):
                bad=copy.deepcopy(self.config)
                bad[field]=value
                with self.assertRaises(gate.BoundaryError):
                    gate.validate(bad)

    def testRejectClaimed8x8RuntimeSuccess(self):
        bad=copy.deepcopy(self.config)
        bad["levels"][1]["runtimeVerified"]=64
        with self.assertRaisesRegex(gate.BoundaryError,"FALSE_SCALE_COVERAGE"):
            gate.validate(bad)

    def testNoSourceOnlyHumanReleaseBit(self):
        bad=copy.deepcopy(self.config)
        bad["flags"]["sourceOnlyMaximum"]="0x0F"
        with self.assertRaisesRegex(gate.BoundaryError,"FLAG_AUTHORITY_DRIFT"):
            gate.validate(bad)

    def testNoMissingProtectedActionStop(self):
        bad=copy.deepcopy(self.config)
        bad["prohibited"].remove("loadKernelModule")
        with self.assertRaisesRegex(gate.BoundaryError,"MISSING_STOP_ACTION"):
            gate.validate(bad)

    def testNoPrivilegedPackageOperations(self):
        bad=copy.deepcopy(self.config)
        bad["debian"]["noPackageAutoInstall"]=False
        with self.assertRaisesRegex(gate.BoundaryError,"DEBIAN_KERNEL_ROLE"):
            gate.validate(bad)

if __name__=="__main__":
    unittest.main()
