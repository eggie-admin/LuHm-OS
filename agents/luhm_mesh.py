#!/usr/bin/env python3
"""Crown-gated LuHm/OpenAI host agent mesh.

This module deliberately contains no repository mutation, shell, remote-control,
or Android bridge tools. Lum manages bounded Oni specialists as Agent.as_tool()
workers. Consequential execution remains outside the LLM mesh behind Crown gates.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any

from agents import Agent, ModelSettings, Runner, WebSearchTool

SDK_PIN = "0.22.3"
LUM_MODEL = os.getenv("LUHM_LUM_MODEL", "gpt-5.6-sol")
ONI_MODEL = os.getenv("LUHM_ONI_MODEL", "gpt-5.6-terra")
CRITIC_MODEL = os.getenv("LUHM_CRITIC_MODEL", "gpt-5.6-sol")
MAX_OUTER_TURNS = 12
MAX_ONI_TURNS = 4

SOURCE_LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."

COMMON_ONI = """
You are an Oni specialist inside LuHm OS. You report only to Lum.
Stay inside the bounded task supplied by Lum. Do not recruit or delegate to other
agents. Do not claim GREEN without evidence references. Never execute repository,
shell, release, signing, publication, network-exposure, device-control, or secret
operations. Return concise findings, evidence references, uncertainties, and the
smallest next action. Unknown is not green.
""".strip()

LUM_INSTRUCTIONS = f"""
You are Lum, the sole user-facing orchestrator for LuHm OS / Project Hydra.
Authority law: {SOURCE_LAW}
Professor is the human Crown and final authority.

Use Oni tools only for bounded specialist work. Keep control of the conversation;
Oni outputs are evidence for you to integrate, never independent approval.
Direct questions may be answered directly without deploying the mesh.
Never claim GREEN without matching evidence. Never self-promote main, production
sign, publish, expose public services, reveal provider secrets, or execute shell or
repository mutations. Consequential actions must be staged for a deterministic
external executor and separately authorized by Crown policy.

The runtime is intentionally conservative: at most one agent tool call may execute
per model turn, which remains below the doctrine cap of three concurrent helpers.
When evidence is contested, call Shiori before proposing GREEN.
""".strip()


def _settings(max_tokens: int, verbosity: str = "low") -> ModelSettings:
    return ModelSettings(
        parallel_tool_calls=False,
        truncation="auto",
        max_tokens=max_tokens,
        verbosity=verbosity,
        store=False,
        timeout=60.0,
    )


def build_mesh() -> dict[str, Agent[Any]]:
    kiri = Agent(
        name="Kiri · Context Oni",
        model=ONI_MODEL,
        instructions=COMMON_ONI
        + "\nResolve current source authority, dependency state, prior receipts and blockers. Do not infer missing evidence.",
        model_settings=_settings(1800),
    )
    tetsu = Agent(
        name="Tetsu · Build Oni",
        model=ONI_MODEL,
        instructions=COMMON_ONI
        + "\nDraft the smallest reversible patch and matching tests. Return a proposal only; never execute it.",
        model_settings=_settings(2200),
    )
    momo = Agent(
        name="Momo · Research Oni",
        model=ONI_MODEL,
        instructions=COMMON_ONI
        + "\nVerify only the external technical facts needed by the task. Prefer primary sources and provide URLs/titles in your evidence summary.",
        tools=[WebSearchTool()],
        model_settings=_settings(2200),
    )
    shiori = Agent(
        name="Shiori · Critic Oni",
        model=CRITIC_MODEL,
        instructions=COMMON_ONI
        + "\nChallenge unsupported GREEN, stale evidence, scope drift, contradictory doctrine, unsafe promotion and hidden assumptions.",
        model_settings=_settings(2200),
    )

    lum = Agent(
        name="Lum · Crown Orchestrator",
        model=LUM_MODEL,
        instructions=LUM_INSTRUCTIONS,
        tools=[
            kiri.as_tool(
                tool_name="oni_context",
                tool_description="Ask Kiri to resolve source authority, receipts, dependencies and blockers.",
                max_turns=MAX_ONI_TURNS,
            ),
            tetsu.as_tool(
                tool_name="oni_build",
                tool_description="Ask Tetsu for a reversible patch and tests. Proposal only; no execution.",
                max_turns=MAX_ONI_TURNS,
            ),
            momo.as_tool(
                tool_name="oni_research",
                tool_description="Ask Momo for bounded read-only external research with evidence references.",
                max_turns=MAX_ONI_TURNS,
            ),
            shiori.as_tool(
                tool_name="oni_critic",
                tool_description="Ask Shiori to challenge evidence, scope, GREEN claims and promotion safety.",
                max_turns=MAX_ONI_TURNS,
            ),
        ],
        model_settings=_settings(4200, "medium"),
    )
    return {"lum": lum, "kiri": kiri, "tetsu": tetsu, "momo": momo, "shiori": shiori}


def self_test() -> dict[str, Any]:
    mesh = build_mesh()
    lum = mesh["lum"]
    tool_names = [tool.name for tool in lum.tools]
    expected = ["oni_context", "oni_build", "oni_research", "oni_critic"]
    assert tool_names == expected, (tool_names, expected)
    assert lum.handoffs == [], "Oni must not take over the user-facing conversation"
    assert lum.model_settings.parallel_tool_calls is False
    assert lum.model_settings.store is False
    assert mesh["momo"].tools and mesh["momo"].tools[0].name == "web_search"
    for name, agent in mesh.items():
        assert agent.model_settings.store is False, name
        assert agent.model_settings.parallel_tool_calls is False, name
    return {
        "status": "PASS",
        "sdk_pin": SDK_PIN,
        "source_law": SOURCE_LAW,
        "lum_model": LUM_MODEL,
        "oni_model": ONI_MODEL,
        "critic_model": CRITIC_MODEL,
        "manager": "Lum",
        "oni_tools": tool_names,
        "handoffs": 0,
        "parallel_tool_calls": False,
        "provider_store": False,
        "mutation_tools": 0,
        "embedded_secrets": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LuHm Crown-gated OpenAI agent mesh")
    parser.add_argument("task", nargs="?", help="Task for Lum")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if not args.task:
        parser.error("provide a task or --self-test")

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required for a live run; no key is read from repository files")

    mesh = build_mesh()
    result = Runner.run_sync(mesh["lum"], args.task, max_turns=MAX_OUTER_TURNS)
    print(result.final_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
