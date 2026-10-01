#!/usr/bin/env python3
"""Hardened LuHm OS MCP + ChatGPT presentation harness entrypoint.

The canonical MCP core remains in luhmMcpServer.py. This wrapper adds only
presentation resources/routes and keeps authority boundaries unchanged.
"""
from __future__ import annotations

import argparse
import os

import luhmMcpServer as core
from luhmHarness import register_harness
from luhmOniSummoner import register_oni_summoner

register_harness(
    core.server,
    root=core.ROOT,
    annotations=core.READ_ONLY_INTERNAL,
    status_provider=core._status_payload,
    roster_provider=core._roster_payload,
    profile_provider=core._profile,
)

register_oni_summoner(
    core.server,
    root=core.ROOT,
    annotations=core.READ_ONLY_INTERNAL,
    status_provider=core._status_payload,
    roster_provider=core._roster_payload,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("transport", nargs="?", default="streamable-http", choices=("streamable-http", "stdio"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        core._assert_source_contract()
        if core._profile() == "production":
            core._production_security()
        print("LUHM_HARNESS_SOURCE_GREEN")
        return 0

    if args.transport == "stdio":
        core.server.run(transport="stdio")
        return 0

    if core._profile() == "production":
        port = int(os.environ.get("PORT", "10000"))
        core.server.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=port,
            streamable_http_path="/mcp",
            stateless_http=True,
            json_response=True,
            max_request_body_size=1 * 1024 * 1024,
            transport_security=core._production_security(),
        )
        return 0

    core.server.run(
        transport="streamable-http",
        host=core.LOCAL_HOST,
        port=core.LOCAL_PORT,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        max_request_body_size=1 * 1024 * 1024,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
