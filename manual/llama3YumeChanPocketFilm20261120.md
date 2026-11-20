# LuHm OS: Llama 3 + Yume-chan Pocket Film Studio (tutorial POC)

**Source baseline:** `2a9cd0c9d544c156655213bad0736caa204cd226`. **Recovery branch:** `snapshot/pre-llama3-yume-chan-20261120-2a9cd0c9`. **Date:** 2026-11-20. **Crown:** STOP. **Operational agents:** QUARANTINED.

## What was saved in ChatGPT

- Existing private `pirate-daddy-yume-film` updated to **Yume-chan • Film Studio v0.3.0**. Preserves earlier directing and Titan7 skills; adds a beginner camera/editing skill and a portable `assets/yume-chan-pocket-studio/` HTML/CSS/jQuery/XMB-like demo (jQuery vendored, no remote script).
- New private `llama3-luhm-canon` **v0.1.0**. Adds a Canon-focused Llama 3 setup skill and stdlib Python localhost-only probe. It provides no downloaded weights, new host server, agent runtime or verified model execution.

These are **skills/private account releases**. An account plugin release does not by itself make a static website publicly hosted or give it an FFmpeg server, private Drive data, Cloudflare access, or a live camera test.

## First no-code Yume-chan tutorial

1. Shoot a real clip with the Samsung Camera application first; keep the original on your phone and private owner archive. The HTML demo can record a short clip when served from a secure origin and granted browser permissions.
2. Download the exported pocket-studio ZIP from the private plugin release or current chat and unzip it. Open its `index.html` to inspect/import an existing clip; camera requires HTTPS or localhost and is browser-dependent.
3. Tap **Timeline**, mark IN/OUT, select a permitted effect, add a shot, then **Shot list → Download EDL JSON**. This does not edit the binary video or upload to a model.
4. Back up the video and EDL. The private Titan 7 Python/FFmpeg candidate in PR #594 remains on security hold; Copilot found high-severity protocol and token-log problems. After a targeted patch and new exact-head CI, test a **private** worker and link imported media IDs to EDL before rendering.
5. Only then consider GitHub → Cloudflare static hosting. Cloudflare may serve the static UI over HTTPS, but private footage should not be uploaded there. Never expose the unpatched backend as a public route.

## First Llama 3 tutorial

1. Open `Llama 3 • LuHm Canon` and ask to inspect current GitHub Canon.
2. Use packaged `assets/llama3-local-probe.py` with Python 3 for a **dry run**, no model involved. Explicit `--invoke --url http://127.0.0.1:8080 --model <approved-model>` can test a verified owner-started local compatible server. Do not take the dry-run as model proof.
3. Choose a model variant/hardware/license only with a verified local or provider entitlement and cost receipt. No keys in GitHub, browser or Android package.

## Canon and architecture

GitHub controls source and CI. Python 3 orchestrates. SQL stores bounded metadata/receipts. npm is Node dependency and test tooling, **not** Copilot. Copilot may review coding PRs; it does not automatically give runtime authority. ChatGPT/Lum coordinates model/tool use through existing capability-first policy. Google AI, OpenAI and Cloudflare stay subject to the existing Four-Pillar adapter/budget gates.

Current evidence: **two account plugin packages saved and read back; local JavaScript syntax/HTML structural checks pass; Llama probe default dry-run passes; static Cloudflare deployment, live model inference, phone physical recording, private editor backend and Instagram auto-publishing are NOT proven.**

## Next bounded integration work

Mirroring plugin static assets into GitHub, independently validating its deployed HTTPS UI, hardening Titan7 backend, and authorizing a sanitized GitHub/Cloudflare build/release are distinct tasks. This source-only PR **does not** update live Cloudflare zones, Render, MCP server tools, Android firmware, or public websites.

**Doctrine:** AI proposes. Policy authorizes. CI proves. Human promotes.
