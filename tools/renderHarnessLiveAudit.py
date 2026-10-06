#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "doctrine" / "ASSET_DESK_HARNESS_LIVE_20260930.json"
BLUEPRINT = ROOT / "render.yaml"
SOURCE_TRUTH = ROOT / "doctrine" / "SOURCE_OF_TRUTH.json"
HARNESS_SERVER = ROOT / "host" / "mcp" / "luhmHarnessServer.py"
HARNESS = ROOT / "host" / "harness" / "index.html"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def main() -> int:
    for path in (RECEIPT, BLUEPRINT, SOURCE_TRUTH, HARNESS_SERVER, HARNESS):
        require(path.is_file(), f"RED_RENDER_HARNESS_MISSING:{path.relative_to(ROOT)}")

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    truth = json.loads(SOURCE_TRUTH.read_text(encoding="utf-8"))
    blueprint = BLUEPRINT.read_text(encoding="utf-8")
    server = HARNESS_SERVER.read_text(encoding="utf-8")

    require(receipt.get("status") == "GREEN_ASSET_DESK_SOURCE_CI_RENDER_LIVE", "RED_RECEIPT_STATUS")
    require(receipt.get("promotedByMergeCommit") == "c4fd6c254c8b0c620c152edd2cfd7861dfe53bf2", "RED_MERGE_BINDING")
    require(receipt.get("testedFeatureHead") == "761524e179ddf8e69594d34c7e1839e3fba0d625", "RED_TESTED_HEAD_BINDING")

    render = receipt.get("render", {})
    require(render.get("serviceName") == "luhm-os-harness-green", "RED_RENDER_SERVICE")
    require(render.get("serviceId") == "srv-daubsi1srm7s73bl5lh0", "RED_RENDER_SERVICE_ID")
    require(render.get("deployId") == "dep-daubsihsrm7s73bl5nj0", "RED_RENDER_DEPLOY_ID")
    require(render.get("sourceCommit") == receipt.get("promotedByMergeCommit"), "RED_RENDER_SOURCE_DRIFT")
    require(render.get("deployStatus") == "live", "RED_RENDER_NOT_LIVE")
    require(render.get("observedHarnessPath") == "/harness/", "RED_HARNESS_ROUTE")
    require(render.get("observedHarnessStatus") == 200, "RED_HARNESS_HTTP_PROOF")
    require(render.get("autoDeploy") is False, "RED_AUTODEPLOY_POLICY")
    require(render.get("defaultHealthCheckModeAtCreation") == "TCP", "RED_HEALTH_MODE_OVERCLAIM")
    require(render.get("blueprintHealthCheckPath") == "/healthz", "RED_BLUEPRINT_HEALTH_PATH")
    require(render.get("blueprintAppliedToExistingService") is False, "RED_BLUEPRINT_APPLIED_OVERCLAIM")

    boundaries = receipt.get("boundaries", {})
    for key in ("publicationAuthority", "releaseAuthority", "productionSigningAuthority", "directoryPublicationProven", "godotWebArtifactProven"):
        require(boundaries.get(key) is False, f"RED_AUTHORITY_WIDENING:{key}")
    require(boundaries.get("crownStatus") == "STOP", "RED_CROWN_DRIFT")

    require(truth.get("source_law") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "RED_SOURCE_LAW")
    publication = truth.get("publicationMilestone", {})
    require(publication.get("publicationAuthority") is False, "RED_PUBLICATION_AUTHORITY_DRIFT")
    require(publication.get("directoryPublicationProven") is False, "RED_DIRECTORY_PUBLICATION_OVERCLAIM")
    require(publication.get("crownStatus") == "STOP", "RED_PUBLICATION_CROWN_DRIFT")

    required_blueprint_fragments = (
        "name: luhm-os-harness-green",
        "runtime: python",
        "branch: main",
        "region: ohio",
        "plan: free",
        "startCommand: python host/mcp/luhmHarnessServer.py streamable-http",
        "healthCheckPath: /healthz",
        "autoDeployTrigger: off",
        "key: LUHM_MCP_PROFILE",
        "value: production",
        "key: RENDER_EXTERNAL_HOSTNAME",
        "value: luhm-os-harness-green.onrender.com",
        "key: LUHM_HARNESS_PUBLIC_ORIGIN",
        "value: https://luhm-os-harness-green.onrender.com",
    )
    for fragment in required_blueprint_fragments:
        require(fragment in blueprint, f"RED_BLUEPRINT_CONTRACT:{fragment}")

    require('host="0.0.0.0"' in server, "RED_RENDER_BIND")
    require('os.environ.get("PORT", "10000")' in server, "RED_RENDER_PORT")
    require('streamable_http_path="/mcp"' in server, "RED_MCP_PATH")
    require("stateless_http=True" in server, "RED_MCP_STATEFUL_DRIFT")

    print("GREEN_RENDER_HARNESS_LIVE_RECEIPT")
    print("MERGE_COMMIT=" + receipt["promotedByMergeCommit"])
    print("SERVICE=" + render["serviceName"])
    print("DEPLOY=" + render["deployId"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
