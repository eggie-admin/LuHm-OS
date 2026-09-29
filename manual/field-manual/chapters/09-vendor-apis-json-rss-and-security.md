---
id: chapter09
title: "Vendor APIs, JSON, RSS, and Security"
subtitle: "Capability providers are not authority providers."
scene: ../scenes/09-vendor-apis-json-rss-and-security.yaml
art: null
statusSource: ../generated/status-blocks.md
---

# 09 // Vendor APIs, JSON, RSS, and Security

*Capability providers are not authority providers.*

{{ scene: chapter09-vendor-apis-json-rss-and-security }}

## Professor Lecture

Plain JSON is the canonical machine-readable manifest format. Base64 is a transport representation, not security.

RSS/event feeds can carry status, metadata, artifact references, and notifications. The conveyor belt does not become the foreman. Feeds do not grant authority.

OpenAI, Hugging Face, or other model providers sit behind provider-neutral boundaries where practical. Providers provide capability. Policy provides authority. Humans provide final authorization.

Cloudflare belongs at the public edge for DNS/TLS/Zero Trust/tunnel patterns. Google identity can answer who a user is. Authentication, authorization, approval, and evidence remain separate questions.

## Lum Tech Demo / Field Notes

- No secrets in manifests, docs, feeds, repos, or screenshots.
- Use short-lived scoped sessions and revocable credentials.
- Keep provider adapters swappable.
- Treat diagrams as architecture, not proof of live deployment.

{{ statusBlock: current }}


> **Source law:** AI proposes. Policy authorizes. CI proves. Human promotes.
