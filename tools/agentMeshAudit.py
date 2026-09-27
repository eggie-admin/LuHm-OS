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
    "tests/agentMeshPackSmoke.gd",
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
    build = text("scripts/buildCathedralWebglass.sh")

    if contract.get("manager") != "Lum":
        fail("manager drift")
    if contract.get("userFacingAgentCount") != 1:
        fail("only Lum may be user-facing")
    if contract.get("runtimeParallelToolCalls") is not False:
        fail("parallel tool calls must fail closed")
    android = contract.get("android", {})
    for key in (
        "executesOpenAIAgents",
        "containsProviderSecret",
        "containsPythonRuntime",
        "termuxBridge",
        "remoteShell",
        "internetPermission",
    ):
        if android.get(key) is not False:
            fail(f"android boundary drift: {key}")

    requirements = text("agents/requirements.txt")
    if "openai-agents==0.22.3" not in requirements:
        fail("SDK pin drift")
    if doctrine.get("openai", {}).get("wheelSha256Observed") != "41dec9e2e703db32a627bf0290f3721a6ca37405603a8cb654213356dbb8ee9d":
        fail("OpenAI SDK provenance hash drift")
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
    if "doctrine/luhmAgentMeshFinal-20260927.json" not in export or "assets/system/luhmAgentMesh.json" not in export:
        fail("agent doctrine/contract not explicitly included in export")
    if "exclude_filter=\"agents/**,deploy/**,tools/**,.github/**\"" not in export:
        fail("host runtime exclusion from APK drifted")
    if "tests/agentMeshPackSmoke.gd" not in build:
        fail("export-pack isolation smoke missing from build")
    if "! grep -q 'android.permission.INTERNET' build/android/manifest.txt" not in build:
        fail("built manifest internet-deny proof missing")

    denied = set(release.get("deny", []))
    for item in (
        "production signing",
        "publishing",
        "stable promotion",
        "remote shell execution",
        "embedded provider secrets",
    ):
        if item not in denied:
            fail("release boundary weakened: " + item)

    for hardening in (
        "EnvironmentFile=/home/eggie/.secrets/luhm-agent.env",
        "Environment=OPENAI_AGENTS_DISABLE_TRACING=1",
        "NoNewPrivileges=true",
        "ProtectSystem=strict",
        "CapabilityBoundingSet=",
    ):
        if hardening not in service:
            fail("systemd hardening drift: " + hardening)

    secret_patterns = [
        r"sk-[A-Za-z0-9_-]{12,}",
        r"OPENAI_API_KEY\s*=\s*['\"][^$][^'\"]+",
    ]
    corpus = "\n".join(
        text(path)
        for path in REQUIRED
        if path.endswith((".py", ".md", ".json", ".example"))
    )
    for pattern in secret_patterns:
        if re.search(pattern, corpus):
            fail("possible embedded secret")

    if doctrine.get("sourceLaw") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        fail("source law drift")
    if doctrine.get("promotion", {}).get("canonicalMainMutated") is not False:
        fail("candidate must not claim canonical promotion")
    if doctrine.get("greenLaw", {}).get("hostRuntimeGreen") != "physical Hydra host activation + live provider smoke + local receipt":
        fail("host green law drift")
    if doctrine.get("greenLaw", {}).get("deviceGreen") != "physical Samsung install + runtime smoke":
        fail("device green law drift")

    print("AGENT_MESH_AUDIT=PASS")
    print("ANDROID_PROVIDER_SECRET=NONE")
    print("ANDROID_OPENAI_RUNTIME=NONE")
    print("ANDROID_INTERNET_PERMISSION=DENIED")
    print("HOST_AGENT_MESH=SOURCE_READY")
    print("LIVE_HOST_ACTIVATION=UNPROVED")
    print("PHYSICAL_SAMSUNG=UNPROVED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
