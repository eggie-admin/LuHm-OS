# LuHm OS Plugin Privacy

Status: development candidate. This document does not authorize publication.

LuHm OS is designed around minimum necessary data flow, explicit evidence boundaries, and human-controlled promotion.

## Plugin package

The portable plugin package contains instructions, metadata, and MCP connection configuration. It does not contain OpenAI API keys, Android signing keys, private Google Drive credentials, or other production secrets.

## MCP tools

The current LuHm MCP tool surface is read-only. Tool requests may include the task kind, routing flags, and source/proof identifiers needed to answer the request. The MCP server returns source-truth, role, routing, and proof-contract data.

A production remote MCP deployment may create infrastructure logs needed for security, reliability, abuse prevention, and debugging. The final retention policy and hosting provider must be documented and reviewed before public publication.

## Android proof vault

User-selected proof files are copied into app-private content-addressed storage on the Android device. Imported proof begins UNKNOWN until adjudicated. Raw Android SAF URIs and provider credentials are not intended to enter model-facing proof packets.

## External services

A deployed LuHm plugin may rely on OpenAI/ChatGPT and an explicitly approved MCP hosting provider. Those services have their own privacy practices. No production hosting provider is declared by this candidate document.

## Contact and changes

Privacy-impacting architecture changes require a new review and evidence receipt before publication. The canonical project source is https://github.com/eggie-admin/LuHm-OS.
