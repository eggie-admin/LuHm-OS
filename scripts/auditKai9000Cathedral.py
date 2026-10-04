#!/usr/bin/env python3
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]

def read(path):
    return (root / path).read_text(encoding="utf-8")

def load(path):
    return json.loads(read(path))

roles = load("agents/luhm-agent-mesh/roles.json")
agents = load("cathedral/agents.json")
api = load("cathedral/api/contract.json")
learning = load("cathedral/learning/contract.json")
audit = load("doctrine/kai9000CathedralHardAudit-20260925.json")
seal = load("doctrine/kai9000CathedralSeal-20260925.json")
site = read("cockpit/jquery/luhm.site.js")
headless = read("cathedral/sidecar/kai9000_headless.py")
termux = read("cathedral/termux/kai-cathedral")
skill = read("skills/kai9000-cathedral/SKILL.md")
index = read("cockpit/index.html")

assert roles["boss"]["role_id"] == "Lum"
assert roles["limits"]["max_parallel_helpers"] == 3
assert roles["limits"]["max_delegation_depth"] == 1
assert roles["limits"]["recursive_recruitment"] is False
assert roles["limits"]["parallel_writes"] is False
assert agents["boss"] == "Lum"
assert agents["limits"]["max_parallel_helpers"] == 3
assert "Kanabo Gate" in agents["routing"]["writer"]

assert api["transport"]["webview_direct_access"] is False
assert api["transport"]["public_bind_forbidden"] is True
assert api["transport"]["cors"] is False
for forbidden in ["shell execution", "filesystem browse", "eval", "remote bind", "memory auto-promotion"]:
    assert forbidden in api["forbidden"]

assert learning["active_by_default"] is False
assert learning["promotion_requires_human"] is True
assert "rewrite agent instructions" in learning["never"]
assert "edit source code" in learning["never"]
assert "fine-tune model weights automatically" in learning["never"]

assert "$.fn[pluginName]" in site
assert "luhm:site:route" in site
for forbidden in ["$.ajax", "fetch(", "XMLHttpRequest", "WebSocket(", "eval("]:
    assert forbidden not in site

assert "connect-src 'none'" in index
assert "./jquery/luhm.site.js" in index
assert "http://127.0.0.1:11434" in headless
assert "CANDIDATE_NOT_ACTIVE" in headless
for forbidden in ["subprocess", "os.system", "eval(", "exec("]:
    assert forbidden not in headless
assert "ollama serve" in termux
assert "sudo" not in termux
assert "su -" not in termux

assert len(audit["passes"]) == 10
assert audit["status"] == "AMBER_PROPOSED_BUILD"
assert seal["status"] == "SEALED_CANDIDATE_NOT_PROMOTED"
assert seal["promotion_requires_human"] is True
assert "AI proposes. Policy authorizes. CI proves. Human promotes." in skill
assert "candidate-memory distillation" in skill

print("KAI 9000 CATHEDRAL HARD AUDIT: PASS / OVERALL AMBER")
for item in audit["passes"]:
    print(f"PASS {item['pass']:02d} {item['name']}: {item['result']}")
