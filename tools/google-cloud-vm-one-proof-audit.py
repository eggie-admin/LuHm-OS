#!/usr/bin/env python3
"""Offline strict-security and one-proof gate; never contact Google or DNS."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
profile=json.loads((root/"infrastructure/google-cloud-vm/vm-profile.json").read_text())
proof=json.loads((root/"doctrine/crown-single-proof-v1.json").read_text())
vm=profile["vm"]
assert profile["schema"]=="luhmOs.googleCloudVmSnapshot.v1"
assert profile["canonicalRepo"]==proof["sourceAuthority"]=="eggie-admin/LuHm-OS"
assert profile["sourceRef"]==proof["sourceRef"] and len(proof["sourceRef"])==40
assert vm["machineType"]=="e2-micro" and vm["diskType"]=="pd-standard"
assert vm["diskGb"]<=30 and vm["externalIp"] is False
assert vm["osLogin"] and vm["blockProjectSshKeys"]
assert vm["shieldedSecureBoot"] and vm["shieldedVtpm"] and vm["integrityMonitoring"]
assert vm["serviceAccount"]=="NONE" and vm["publicIngress"] is False
assert profile["routing"]["currentAuthoritativeDns"]=="cloudflare"
assert profile["routing"]["googleCloudDns"].startswith("RESEARCH_ONLY")
assert profile["gate"]["instanceCreated"] is False and profile["gate"]["diskSnapshotCreated"] is False
assert proof["schema"]=="luhmOs.crownSingleProof.v1"
assert [t["id"] for t in proof["tiers"]]==[
 "mythicRitualLayer","corporateResearchAndGameDevelopment","yumeProofStudio","partnerPublicShowcase"]
assert proof["evidence"]["site"]["cacheBridgeGreen"] is False
assert proof["security"]["newRecurringSpend"] is False
assert proof["evidence"]["beta"]["externalInstallProven"] is False
assert proof["gate"]["crown"]=="STOP"
installer=(root/"infrastructure/google-cloud-vm/install-web.sh").read_text()
provision=(root/"infrastructure/google-cloud-vm/provision.sh").read_text()
assert "127.0.0.1:8080" in installer and "/healthz" in installer
assert "nginx -t" in installer and "systemctl enable --now nginx" in installer
assert "--no-service-account" in provision and "no-address" in provision
assert "EXPECTED_GOOGLE_ACCOUNT" in provision and "ALLOW_VM_COSTS" in provision
assert "PRIVATE_APT_EGRESS_VERIFIED" in provision
assert "compute dns" not in provision and "firewall-rules create" not in provision
print("PASS_ONE_PROOF_FOUR_CANON_TIERS_SOURCE_ONLY_PRIVATE_VM")
