#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine/runtimeDoctrine-20260926.json"
AGENTS = ROOT / "agents/luhm-agent-mesh/crownedCathedralForgePipeline.json"
EXPORT = ROOT / "export_presets.cfg"
BRIDGE = ROOT / "scripts/platform/kaiWebViewBridge.gd"
RITUAL = ROOT / "scripts/game/ritualDirector.gd"
BUILD = ROOT / "scripts/buildCathedralWebglass.sh"


def require(condition: bool, label: str) -> None:
    if not condition:
        raise SystemExit(f"RED: {label}")
    print(f"GREEN: {label}")


doc = json.loads(DOCTRINE.read_text())
require(doc.get("schema") == "luhm-os.runtime-doctrine.v1", "runtime doctrine schema")
require(doc.get("status") == "FULL_MUTATION_CANDIDATE", "full mutation candidate status")

authority = doc["authority"]
require(authority.get("crown") == "Professor", "Professor holds Crown")
require(authority.get("human_final_authority") is True, "human final authority")
require(authority.get("ai_self_approval") is False, "AI self approval blocked")

runtime = doc["runtime"]
for key in ("runtime_downloads", "embedded_secrets", "generic_shell", "filesystem_bridge", "eval_bridge", "arbitrary_url_bridge", "root", "silent_install"):
    require(runtime.get(key) is False, f"forbidden runtime capability off: {key}")
require(runtime.get("network") == "dark", "WebGlass network dark")
require(runtime.get("web_origin") == "https://appassets.androidplatform.net", "caged appassets origin")

caps = runtime["bridge"]["capabilities"]
require(caps.get("rituals") == ["crown_wake", "oni_trinity", "witching_hour"], "exact three ritual allowlist")
require("system.capabilities" in caps.get("message_types", []), "capability handshake present")
for forbidden in ("shell.exec", "fs.write", "eval", "url.open"):
    require(forbidden not in caps.get("message_types", []), f"bridge excludes {forbidden}")

mesh = doc["agent_mesh"]
require(mesh.get("boss") == "Lum", "Lum is mesh boss")
require(mesh.get("default_helpers") == {"Context": "Oni-Kumo", "Build": "Oni-Tetsu", "Research": "Oni-Sumi"}, "canonical oni helper names")
require(mesh.get("conditional_helper") == {"Critic": "Oni-Ibara"}, "canonical critic name")
require(mesh.get("deterministic_executor") == "Kanabo Gate", "Kanabo Gate executor")
require(mesh.get("parallelism_max") == 3, "mesh parallelism max three")
require(mesh.get("delegation_depth_max") == 1, "delegation depth one")
require(mesh.get("recursive_recruitment") is False, "recursive recruitment blocked")
require(mesh.get("parallel_writes") is False, "parallel writes blocked")

agent_cfg = json.loads(AGENTS.read_text())
workers = {item["blade"]: item["name"] for item in agent_cfg.get("workers", [])}
require(agent_cfg.get("boss", {}).get("name") == "Lum", "agent config Lum boss")
require(workers.get("Context") == "Oni-Kumo", "agent config Oni-Kumo")
require(workers.get("Build") == "Oni-Tetsu", "agent config Oni-Tetsu")
require(workers.get("Research") == "Oni-Sumi", "agent config Oni-Sumi")
require(workers.get("Critic") == "Oni-Ibara", "agent config Oni-Ibara")
require(workers.get("Tool Executor") == "Kanabo Gate", "agent config Kanabo Gate")
require(agent_cfg.get("limits", {}).get("delegation_depth_max") == 1, "agent config delegation depth one")

learning = doc["learning"]
require(learning.get("mode") == "candidate_memory_only", "candidate memory only")
require(learning.get("candidate_state") == "CANDIDATE_NOT_ACTIVE", "candidate memory inactive until promotion")
require(learning.get("human_promotion_required") is True, "memory promotion requires human")
require(learning.get("autonomous_prompt_mutation") is False, "no autonomous prompt mutation")
require(learning.get("autonomous_source_mutation") is False, "no autonomous source mutation")
require(learning.get("autonomous_model_weight_mutation") is False, "no autonomous weight mutation")

kai = doc["kai9000"]
require(kai.get("termux") == "optional_external_companion", "Termux external companion")
require(kai.get("ollama") == "optional_loopback_companion", "Ollama loopback companion")
require(kai.get("android_to_termux_exec") is False, "APK cannot execute Termux")
require(kai.get("sidecar_public_bind") is False, "sidecar public bind forbidden")

build = doc["build"]
require(build.get("version_code") == 127, "version code 127")
require(build.get("version_name") == "1.0.27-cathedral.fullmutation.1", "full mutation version name")
require(build.get("target_sdk") == 36, "target SDK 36")
require(build.get("abi") == "arm64-v8a", "arm64 ABI")
require(build.get("internet_permission") is False, "Internet permission disabled")
require(build.get("production_signing") is False, "production signing untouched")

export = EXPORT.read_text()
require('version/code=127' in export, "export version code")
require('version/name="1.0.27-cathedral.fullmutation.1"' in export, "export version name")
require('permissions/internet=false' in export, "export Internet disabled")
require('architectures/arm64-v8a=true' in export, "export arm64 enabled")
require('doctrine/runtimeDoctrine-20260926.json' in export, "runtime doctrine packaged")

bridge = BRIDGE.read_text()
ritual = RITUAL.read_text()
require('DoctrineGateScript' in bridge and 'allows_message_type' in bridge, "bridge doctrine gated")
require('bridge.rejected' in bridge, "bridge rejection receipts")
require('DoctrineGateScript' in ritual and 'allows_ritual' in ritual, "ritual director doctrine gated")
require('const RITUALS :=' not in ritual, "ritual duplicate allowlist removed")

for path in (BRIDGE, RITUAL):
    text = path.read_text()
    require(not re.search(r"\b(OS\.execute|subprocess|Runtime\.getRuntime|eval\s*\(|exec\s*\()", text), f"no executor escape in {path.name}")

build_script = BUILD.read_text()
require('scripts/auditFullMutation.py' in build_script, "full mutation audit wired into build")
require('tests/doctrineGateSmoke.gd' in build_script, "doctrine smoke wired into build")
require('runtimeDoctrine-20260926.json' in build_script, "doctrine evidence wired into build")

promotion = doc["promotion_gates"]
require(promotion.get("main_merge") == "NOT_AUTHORIZED", "main merge still Crown-gated")
require(promotion.get("public_release") == "NOT_AUTHORIZED", "public release still Crown-gated")
require(promotion.get("unknown_is_not_green") is True, "unknown is not green")
require(doc.get("promotion") is False, "candidate not self-promoted")

print("LUHM FULL MUTATION DOCTRINE AUDIT GREEN")
