#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors = []

def need(ok, msg):
    if not ok:
        errors.append(msg)

storage_path = root / "doctrine/storageTopologyV1.json"
source_path = root / "doctrine/currentSourceTruthV3.json"
canon_path = root / "doctrine/projectChatCanonV1.json"
trust_path = root / "doctrine/goddessTrustSealV1.json"
control_path = root / "doctrine/ONI_MESH_CONTROL_PLANE_V2.json"

need(storage_path.is_file(), "missing storage topology")
need((root / "agents/shared/storageLawV1.md").is_file(), "missing shared storage law")

if storage_path.is_file():
    storage = json.loads(storage_path.read_text())
    need(storage.get("primeLaw") == "databases point to files; databases do not become the file server", "prime law drift")
    roles = storage.get("roles", {})
    need(roles.get("openAi", {}).get("role") == "semanticDb", "OpenAI semanticDb drift")
    need(roles.get("github", {}).get("role") == "sourceDb", "GitHub sourceDb drift")
    need(roles.get("googleDrive", {}).get("role") == "fileServer", "Drive fileServer drift")
    need(roles.get("googleDrive", {}).get("canonicalBinaryStorage") is True, "Drive durable binary authority missing")
    need(roles.get("github", {}).get("durableBinaryStorage") is False, "GitHub must not become durable binary store")
    need(roles.get("openAi", {}).get("durableBinaryStorage") is False, "OpenAI must not become binary store")
    need(storage.get("rules", {}).get("unknownStorageLocationIsNotGreen") is True, "UNKNOWN storage must fail closed")
    need(storage.get("crownStatus") == "stop", "storage doctrine Crown must stop")
    library = roles.get("chatGptLibrary", {})
    need(library.get("role") == "workingReviewLayer", "Library working-role missing")
    need(library.get("canonicalSourceAuthority") is False, "Library must not be source authority")
    need(library.get("canonicalBinaryStorage") is False, "Library must not replace Drive masters")
    need(library.get("automaticallySynchronizedWithDrive") is False, "unproven Library-Drive sync")
    need(storage.get("rules", {}).get("chatGptLibraryAutomaticSyncProven") is False, "unknown sync must not claim proof")


need(source_path.is_file(), "current Canon source truth missing")
if source_path.is_file():
    source = json.loads(source_path.read_text())
    need(source.get("schema") == "luhmOs.currentSourceTruth.v3", "source truth schema mismatch")
    need(source.get("product") == "LuHm-OS", "product must use canonical LuHm-OS display")
    need(source.get("storageTopology", {}).get("contract") == "doctrine/storageTopologyV1.json", "current source truth missing storage contract")
    need(source.get("storageTopology", {}).get("automaticDriveLibrarySyncProven") is False, "unproven source sync must not be GREEN")
    need(source.get("promotion") is False and source.get("crownStatus") == "STOP", "source authority gate changed")

if canon_path.is_file():
    canon = json.loads(canon_path.read_text())
    need("doctrine/storageTopologyV1.json" in canon.get("loadOrder", []), "chat canon must load storage topology")
    need(canon.get("alwaysLoadedCore", {}).get("storageTopology") == "doctrine/storageTopologyV1.json", "storage topology not always loaded")
    gr = canon.get("goddessRoleMap", {})
    need(gr.get("urd", {}).get("canonicalRole") == "doctorGoddess", "Urd role drift")
    need(gr.get("belldandy", {}).get("canonicalRole") == "secretary", "Belldandy role drift")
    need(gr.get("skuld", {}).get("canonicalRole") == "research", "Skuld role drift")


if trust_path.is_file():
    trust = json.loads(trust_path.read_text())
    roles = trust.get("roles", {})
    need(roles.get("urd", {}).get("role") == "doctorGoddess", "trust seal Urd role drift")
    need(roles.get("belldandy", {}).get("role") == "secretary", "trust seal Belldandy role drift")
    need(roles.get("skuld", {}).get("role") == "research", "trust seal Skuld role drift")

if control_path.is_file():
    control = json.loads(control_path.read_text())
    roles = control.get("roles", {})
    need(roles.get("Urd", {}).get("kind") == "doctor-goddess-system-diagnostician", "mesh Urd role drift")
    need(roles.get("Belldandy", {}).get("kind") == "secretary-goddess-state-records-keeper", "mesh Belldandy role drift")
    need(roles.get("Skuld", {}).get("kind") == "research-goddess-compatibility-scout", "mesh Skuld role drift")
    need(roles.get("Fumi", {}).get("kind") == "records-registrar-helper", "Fumi registrar role drift")

required_text = {
    "agents/projectChatBootstrap/SKILL.md": "databases point to files; databases do not become the file server",
    "agents/urdMutationOni/SKILL.md": "Canonical machine identity: `urdDoctorGoddess`",
    "agents/belldandyQualityOni/SKILL.md": "Canonical machine identity: `belldandySecretary`",
    "agents/skuldResearchOni/SKILL.md": "Canonical machine identity: `skuldResearch`",
    "agents/lum/SKILL.md": "Google Drive is the durable binary file server",
    "agents/fumiSecretaryOni/SKILL.md": "Drive is the durable binary file server",
    "agents/mediaAssetFactory/SKILL.md": "Google Drive is the durable binary file server",
    "agents/sumiAssetOni/SKILL.md": "durableStorageRef",
    "agents/kugiToolOni/SKILL.md": "durable binary",
    "plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md": "Google Drive is the durable binary file server",
}
for rel, token in required_text.items():
    p = root / rel
    need(p.is_file(), f"missing {rel}")
    if p.is_file():
        need(token in p.read_text(), f"{rel} missing storage law token")

print(json.dumps({
    "schema": "luhmOs.storageTopologyAudit.v1",
    "status": "greenStorageTopologyCandidate" if not errors else "redStorageTopologyCandidate",
    "errors": errors,
    "deviceProof": False,
    "crownStatus": "stop"
}, indent=2))
raise SystemExit(1 if errors else 0)
