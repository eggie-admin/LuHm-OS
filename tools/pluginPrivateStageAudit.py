#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def main() -> int:
    stage = load("doctrine/PLUGIN_PRIVATE_STAGE_V1.json")
    plugin = load("plugins/luhm-os/plugin.json")
    prod_mcp = load("plugins/luhm-os/mcp.json")
    private_mcp = load("plugins/luhm-os/mcp.private.json")
    tests = load("plugins/luhm-os/review-tests.json")
    server = text("host/mcp/luhmMcpServer.py")

    require(stage.get("status") == "PRIVATE_STAGING", "private stage status drift")
    require(stage.get("releaseLaw") == LAW, "source law drift")
    distribution = stage.get("distribution", {})
    require(distribution.get("mode") == "PRIVATE_PERSONAL", "distribution mode drift")
    require(distribution.get("publicDirectory") is False, "private stage became public directory")
    require(distribution.get("publicSubmission") is False, "private stage became public submission")
    require(distribution.get("workspacePublishing") is False, "workspace publishing enabled unexpectedly")
    require(distribution.get("requiresExplicitCrownForPublicSubmission") is True, "public submission lost Crown gate")

    require(plugin.get("extensions", {}).get("com.openai", {}).get("interface", {}).get("capabilities") == ["Read"], "plugin is no longer read-only")
    require(prod_mcp["mcpServers"]["luhm"]["url"] == "https://mcp.eggiebagelface.art/mcp", "canonical MCP URL drift")
    require(private_mcp["mcpServers"]["luhm_private"]["url"] == "https://luhm-os-mcp.onrender.com/mcp", "private fallback MCP URL drift")

    mcp = stage.get("mcp", {})
    require(mcp.get("toolsReadOnly") is True, "private MCP write surface enabled")
    require(mcp.get("writeToolsAllowed") is False, "private stage allows write tools")
    require(mcp.get("oauthRequiredBeforePrivateOrWriteTools") is True, "OAuth boundary drift")

    for token in ("readOnlyHint=True", "destructiveHint=False", "openWorldHint=False", "luhm_status", "luhm_agent_roster", "luhm_validate_scope", "luhm_route_task", "luhm_proof_contract"):
        require(token in server, f"MCP read-only contract missing: {token}")
    for forbidden in ("merge_pull_request", "production_sign", "checkout", "complete_checkout"):
        require(forbidden not in server, f"private MCP gained forbidden capability: {forbidden}")

    require(len(tests.get("positive", [])) == 5, "public review staging requires five positive tests")
    require(len(tests.get("negative", [])) == 3, "public review staging requires three negative tests")
    ids = [item.get("id") for item in tests["positive"] + tests["negative"]]
    require(len(ids) == len(set(ids)), "review test ids must be unique")

    money = stage.get("monetization", {})
    require(money.get("enabled") is False, "monetization enabled in private stage")
    require(money.get("checkoutEnabled") is False, "checkout enabled in private stage")
    require(money.get("digitalSubscriptionSalesInPlugin") is False, "digital subscription sales enabled")
    require(money.get("digitalServiceUpsellInPlugin") is False, "digital service upsell enabled")

    for required in (
        "plugins/luhm-os/PRIVATE_STAGE.md",
        "plugins/luhm-os/PUBLIC_SUBMISSION_DRAFT.md",
        "plugins/luhm-os/PRIVACY.md",
        "plugins/luhm-os/TERMS.md",
    ):
        require((ROOT / required).is_file(), f"missing release staging file: {required}")

    print("LUHM_PRIVATE_PLUGIN_STAGE_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
