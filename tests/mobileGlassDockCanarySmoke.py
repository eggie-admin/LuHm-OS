#!/usr/bin/env python3
"""Headless Chrome evidence for the real LuHm MCP mobile glass-dock HTML.

This is a sandboxed browser interaction test with a synthetic, read-only tool
payload. It does NOT claim that ChatGPT mounted the widget or that Android is
in lock-task/kiosk mode. No internet, provider inference, credentials or writes.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "host/harness/mobileCockpitWidget.html").read_text(encoding="utf-8")
POLICY = json.loads((ROOT / "doctrine/glassPluginDockV1.json").read_text(encoding="utf-8"))
OUT = ROOT / "build" / "canaryKioskBrowserProof"


def fake_payload(policy: dict) -> dict:
    return {
        "schema": "luhmOs.mobileCockpitPayload.v1",
        "sourceRef": os.environ.get("GITHUB_SHA", "LOCAL_SOURCE_FIXTURE"),
        "sourceTruth": "AMBER_PROPOSED_SEAL_OF_TRUTH",
        "authority": {
            "readOnly": True,
            "mutationAuthority": False,
            "promotionAuthority": False,
            "publicationAuthority": False,
            "crownAuthority": False,
        },
        "companyQuarantine": {
            "state": "QUARANTINED",
            "activeTaskWorkersAllowed": False,
        },
        "roster": {
            "roles": [{"agentId": "lum", "displayName": "Lum"}] +
            [{"agentId": "member%d" % i, "displayName": "Member %d" % i}
             for i in range(1, 15)]
        },
        "glassDock": policy,
    }


def make_page(browser, width: int, *, policy: dict | None = None,
              followup: bool = True, fullscreen: bool = True):
    context = browser.new_context(
        viewport={"width": width, "height": 820},
        device_scale_factor=1,
        reduced_motion="reduce",
    )
    payload = fake_payload(POLICY if policy is None else policy)
    script = (
        "window.__luhmIntents=[];window.__luhmModes=[];"
        "window.openai={toolOutput:" + json.dumps(payload) + "};"
    )
    if followup:
        script += (
            "window.openai.sendFollowUpMessage=async({prompt})=>"
            "{window.__luhmIntents.push(prompt);};"
        )
    if fullscreen:
        script += (
            "window.openai.requestDisplayMode=async({mode})=>"
            "{window.__luhmModes.push(mode);return {mode:'inline'};};"
        )
    context.add_init_script(script)
    page = context.new_page()
    requests: list[str] = []
    errors: list[str] = []
    page.on("request", lambda request:
            requests.append(request.url) if request.url.startswith(("http://", "https://")) else None)
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto("about:blank")
    page.set_content(HTML, wait_until="load")
    return context, page, requests, errors


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def run() -> None:
    launch: dict = {"headless": True, "args": ["--no-sandbox"]}
    installed = os.environ.get("LUHM_CHROME_EXECUTABLE")
    if installed:
        launch["executable_path"] = installed
    else:
        launch["channel"] = "chrome"
    results = []
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch)
        try:
            for width in (320, 390, 640):
                ctx, page, requests, errors = make_page(browser, width)
                try:
                    require("tool response received" in page.locator("#bridge").inner_text().lower(),
                            "read-only tool payload did not render")
                    require(page.locator("#roster li").count() == 15, "roster count")
                    require("quarantined" in page.locator("#workers").inner_text().lower(),
                            "operational hold not visible")
                    launcher = page.locator("#glassToggle")
                    require(launcher.count() == 1, "exactly one gear launcher")
                    require(launcher.bounding_box()["height"] >= 44, "touch target")
                    launcher.click()
                    require(page.locator("#glassDock").is_visible(), "gear failed to open dock")
                    require(launcher.get_attribute("aria-expanded") == "true", "expanded state")
                    buttons = page.locator("#glassModules .glassModule button")
                    require(buttons.count() == 5, "five registered module cards")
                    require(page.locator("#glassClose").evaluate("(el)=>document.activeElement===el"),
                            "focus not moved into drawer")
                    for idx, module in enumerate(POLICY["modules"]):
                        buttons.nth(idx).click()
                        page.wait_for_function("(n)=>window.__luhmIntents.length===n", arg=idx + 1)
                        require(page.evaluate("(i)=>window.__luhmIntents[i]", idx) == module["chatIntent"],
                                "incorrect or unintended chat handoff")
                    page.locator("#glassExpand").click()
                    page.wait_for_function("()=>window.__luhmModes.length===1")
                    require(page.evaluate("window.__luhmModes[0]") == "fullscreen",
                            "fullscreen was not requested through host")
                    page.keyboard.press("Escape")
                    require(not page.locator("#glassDock").is_visible(), "Escape failed")
                    require(launcher.evaluate("(el)=>document.activeElement===el"),
                            "focus did not return to launcher")
                    require(launcher.get_attribute("aria-expanded") == "false",
                            "closed launcher not reflected")
                    require(page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"),
                            "horizontal overflow")
                    require(not requests, "unexpected external network requests: " + str(requests))
                    require(not errors, "page errors: " + str(errors))
                    page.screenshot(path=str(OUT / ("mobile-" + str(width) + ".png")))
                    results.append({"width": width, "toolPayload": True, "modules": 5,
                                    "userClickedFollowUps": 5, "focusEscape": True,
                                    "fullscreenHostRequest": True, "overflow": False})
                finally:
                    ctx.close()

            ctx, page, requests, errors = make_page(browser, 390, followup=False, fullscreen=False)
            try:
                page.locator("#glassToggle").click()
                page.locator("#glassModules .glassModule button").first.click()
                require("BLOCKED" in page.locator("#glassStatus").inner_text(),
                        "unavailable chat host must fail closed")
                page.locator("#glassExpand").click()
                require("unavailable" in page.locator("#glassStatus").inner_text().lower(),
                        "unavailable fullscreen host must be visible")
                require(not requests and not errors, "fallback emitted network call or JS error")
            finally:
                ctx.close()

            tampered = copy.deepcopy(POLICY)
            tampered["promotion"] = True
            ctx, page, requests, errors = make_page(browser, 390, policy=tampered)
            try:
                require(page.locator("#glassModules button").count() == 0,
                        "unauthorized dock contract generated controls")
                require("VERIFY" in page.locator("#glassStatus").inner_text(),
                        "tampered contract not rejected")
                require(not requests and not errors, "tampered contract made request or JS error")
            finally:
                ctx.close()
        finally:
            browser.close()

    receipt = {
        "schema": "luhmOs.canaryKioskBrowserProof.v1",
        "sourceRef": os.environ.get("GITHUB_SHA", "LOCAL_SOURCE_FIXTURE"),
        "status": "GREEN_HEADLESS_MOBILE_WIDGET_INTERACTION_ONLY",
        "runner": "headless Chrome/Chromium",
        "layouts": results,
        "negativeControls": ["noHostBridge", "noFullscreenHost", "invalidDockPromotion"],
        "internetRequests": 0,
        "chatGptClientMountProven": False,
        "androidCanaryDeviceProven": False,
        "kioskDeviceLockProven": False,
        "godotGameplayProven": False,
        "providerAgentsReleased": False,
        "crownStatus": "STOP",
    }
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    run()
