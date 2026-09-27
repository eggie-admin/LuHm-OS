#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

REQUIRED = [
    "agents/luhm_mesh.py",
    "agents/requirements.txt",
    "agents/README.md",
    "assets/system/luhmAgentMesh.json",
    "scripts/game/agentMeshContract.gd",
    "tests/agentMeshContractSmoke.gd",
    "doctrine/luhmAgentMeshFinal-20260927.json",
    "deploy/systemd/luhm-agent-mesh.service.example",
]


def fail(message: str) -> None:
    print(f"AGENT_MESH_AUDIT=FAIL // {message}")
    raise SystemExit(1)


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing=" + ",".join(missing))

    contract = json.loads(text("assets/system/luhmAgentMesh.json"))
    doctrine = json.loads(text("doctrine/luhmAgentMeshFinal-20260927.json"))
    release = json.loads(text("doctrine/RELEASE_BOUNDARY.json"))
    export = text("export_presets.cfg")
    runtime = text("agents/luhm_mesh.py")
    service = text("deploy/systemd/luhm-agent-mesh.service.example")

    if contract.get("manager") != "Lum":
        fail("manager drift")
    if contract.get("userFacingAgentCount") != 1:
        fail("only Lum may be user-facing")
    if contract.get("runtimeParallelToolCalls") is not False:
        fail("parallel tool calls must fail closed")
    android = contract.get("android", {})
    for key in ("executesOpenAIAgents", "containsProviderSecret", "containsPythonRuntime", "termuxBridge", "remoteShell", "internetPermission"):
        if android.get(key) is not False:
            fail(f"android boundary drift: {key}")

    if "openai-agents==0.22.3" not in text("agents/requirements.txt"):
        fail("SDK pin drift")
    if '"gpt-5.6-sol"' not in runtime or '"gpt-5.6-terra"' not in runtime:
        fail("model defaults missing")
    if "parallel_tool_calls=False" not in runtime or "store=False" not in runtime:
        fail("provider hardening settings missing")
    if ".as_tool(" not in runtime:
        fail("manager-style bounded delegation missing")
    if "handoff(" in runtime or "ShellTool" in runtime or "ApplyPatchTool" in runtime or "ComputerTool" in runtime:
        fail("unsafe or takeover-capable tool present")

    if "permissions/internet=false" not in export:
        fail("Android internet permission must remain disabled")
    denied = set(release.get("deny", []))
    for item in ("production signing", "publishing", "stable promotion", "remote shell execution", "embedded provider secrets"):
        if item not in denied:
            fail("release boundary weakened: " + item)

    secret_patterns = [
        r"sk-[A-Za-z0-9_-]{12,}",
        r"OPENAI_API_KEY\s*=\s*['\"][^$][^'\"]+",
    ]
    corpus = "\n".join(text(path) for path in REQUIRED if path.endswith((".py", ".md", ".json", ".example")))
    for pattern in secret_patterns:
        if re.search(pattern, corpus):
            fail("possible embedded secret")

    if doctrine.get("sourceLaw") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        fail("source law drift")
    if doctrine.get("promotion", {}).get("canonicalMainMutated") is not False:
        fail("candidate must not claim canonical promotion")

    print("AGENT_MESH_AUDIT=PASS")
    print("ANDROID_PROVIDER_SECRET=NONE")
    print("ANDROID_OPENAI_RUNTIME=NONE")
    print("HOST_AGENT_MESH=SOURCE_READY")
    print("LIVE_HOST_ACTIVATION=UNPROVED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
