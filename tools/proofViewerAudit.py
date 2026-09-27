#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def audit() -> None:
    html = text("frontEnd/index.html")
    viewer = text("frontEnd/jquery/luhm.proof.viewer.js")
    workbench = text("frontEnd/jquery/luhm.chat.workbench.js")
    app = text("frontEnd/app.js")
    contract = text("frontEnd/PROOF_VIEWER_CONTRACT.md")

    for token in (
        'data-luhm-proof-viewer', 'data-proof-stage', 'proof-viewer.css',
        'luhm.proof.viewer.js', 'data-proof-close', 'data-proof-pin'
    ):
        require(token in html, f"missing proof-viewer shell token: {token}")

    for proof_type in ("pdf", "docx", "website", "image", "asset", "json", "text"):
        require(f"{proof_type}:true" in viewer, f"missing proof type: {proof_type}")

    require("new URL" in viewer and "safeUrl" in viewer, "proof viewer must validate URLs")
    require("protocol === 'https:'" in viewer, "HTTPS safe URL path missing")
    require("protocol === 'blob:'" in viewer, "blob proof path missing")
    require("sandbox:''" in viewer, "website live frame must be fully sandboxed")
    require("referrerpolicy:'no-referrer'" in viewer, "proof viewer must suppress referrer leakage")
    require("allow-scripts" not in viewer, "website proof frame must not enable scripts")
    require("allow-same-origin" not in viewer, "website proof frame must not enable same-origin privilege")
    require(".html(" not in viewer and "innerHTML" not in viewer, "raw HTML injection is forbidden")
    require("javascript:" not in viewer.lower(), "javascript URL literal is forbidden")
    require("data:" not in viewer.lower(), "data URL literal is forbidden")

    require("detail.proof" in workbench, "chat receipts must accept proof packets")
    require("data-chat-proof-open" in workbench, "chat receipt proof trigger missing")
    require("luhm:proof:open" in workbench, "chat proof-open event missing")
    require("proofs:" in workbench, "Proofs quick action missing")

    require("openProof" in app and "closeProof" in app and "currentProof" in app, "front-end proof bridge incomplete")
    require("luhm:transport:proof-pin" in app, "proof pin must remain a request boundary")

    for phrase in (
        "Raw DOCX/Office HTML is never injected",
        "No proof packet executes tools",
        "Website live mode is sandboxed and opt-in",
        "The HTML workbench is a renderer and request surface only",
    ):
        require(phrase in contract, f"missing proof security doctrine: {phrase}")

    forbidden_authority = ("merge_main", "production_sign", "self_approve", "stable_promote")
    for token in forbidden_authority:
        require(token not in viewer, f"proof viewer gained forbidden authority token: {token}")

    print("PROOF_VIEWER_GREEN")


if __name__ == "__main__":
    audit()
