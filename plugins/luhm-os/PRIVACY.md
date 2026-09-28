# LuHm OS Plugin Privacy

Status: development candidate. This document does not authorize publication.

LuHm OS is designed around minimum necessary data flow, explicit evidence boundaries, and human-controlled promotion.

## Plugin package

The portable plugin package contains instructions, metadata, and MCP connection configuration. It does not contain OpenAI API keys, Android signing keys, private Google Drive credentials, Render secrets, Cloudflare credentials, OAuth client secrets, or other production secrets.

## MCP tools

The current LuHm MCP tool surface is anonymous and read-only. Tool requests may include the task kind, routing flags, and source/proof identifiers needed to answer the request. The MCP server returns bounded source-truth, role, routing, and proof-contract data.

The current candidate does not expose user-specific account data or write actions. If that changes, OAuth 2.1 authentication and per-user authorization are required before deployment.

## Production hosting path

The intended production MCP origin is `https://mcp.eggiebagelface.art`, hosted as a Render web service.

Render terminates HTTPS and may create infrastructure logs needed for security, reliability, abuse prevention, and debugging. Cloudflare is intended to provide authoritative DNS for the hostname. During the initial production path the MCP record remains DNS-only, so Cloudflare does not proxy application HTTP traffic.

Final log retention, incident-response, and access-control settings must be documented and reviewed before public publication. Application logs must exclude secrets, raw credentials, and unnecessary personal data.

## Android proof vault

User-selected proof files are copied into app-private content-addressed storage on the Android device. Imported proof begins UNKNOWN until adjudicated. Raw Android SAF URIs and provider credentials are not intended to enter model-facing proof packets.

## External services

A deployed LuHm plugin may rely on OpenAI/ChatGPT, Render, and Cloudflare DNS. Those services have their own privacy practices. Adding another data processor, proxy, analytics service, identity provider, database, or persistent storage layer requires a privacy review before production use.

## Contact and changes

Privacy-impacting architecture changes require a new review and evidence receipt before publication. The canonical project source is https://github.com/eggie-admin/LuHm-OS.
