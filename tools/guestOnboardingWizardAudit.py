#!/usr/bin/env python3
"""Fail-closed source audit for a strictly non-authenticating guest-access wizard."""
from __future__ import annotations
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "doctrine/guestOnboardingWizardV1.json"
UI = ROOT / "plugins/luhm-os/guestWizard/index.html"


def need(v: bool, why: str) -> None:
    if not v:
        raise ValueError("RED_GUEST_ONBOARDING_" + why)


def audit(d: dict, html: str) -> None:
    need(d["schema"] == "luhmOs.guestOnboardingWizard.v1", "SCHEMA")
    need(d["status"] == "SOURCE_ONLY_NO_INVITATION_NO_LOGIN_NO_PERMISSION_GRANT", "STATUS")
    need(d["guestIdentity"] == "NOT_STORED_IN_PUBLIC_REPOSITORY", "GUEST_PRIVACY")
    need(d["recipientChange"] == "PREVIOUS_CANDIDATE_ON_HOLD_NO_AUTOMATIC_REVOCATION_OR_INVITE", "HOLD")
    need(d["scope"] == "one-private-voluntary-adult-guest-candidate", "SCOPE")
    ident = d["identityFlow"]
    need(ident["primary"] == "GOOGLE_OIDC_CODE_PKCE_CONSENT_VERIFIED_BACKEND_ONLY", "OIDC")
    for k in ("identityIsNotAuthorization", "googleDoesNotAuthorizeInstagram"):
        need(ident[k] is True, "IDENTITY_LAW_" + k)
    for k in ("loginClientIdConfigured", "backendOauthImplemented", "realSignInProven"):
        need(ident[k] is False, "FALSE_LOGIN_PROOF_" + k)
    need(all(s in ident["requirements"] for s in
             ("authorizationCodePlusPkceS256", "stateAndNonceBoundToSession",
              "verifyIssuerAudienceExpirySignature", "serverSideCodeExchange",
              "secureHttpOnlySameSiteSession")), "OIDC_BOUNDARY")
    insta = d["accountConnections"]["instagram"]
    need(insta["connection"] ==
         "META_OFFICIAL_INSTAGRAM_LOGIN_FOR_ELIGIBLE_PROFESSIONAL_ACCOUNT", "META_AUTH")
    need(insta["eligibleAccountTypes"] == ["business", "creator"], "META_ELIGIBILITY")
    for k in ("personalAccountApiAccessPromised", "googleLoginIsInstagramLogin",
              "oauthAppReviewed", "registeredRedirectConfigured", "connected",
              "mayImportOtherPeoplesAccounts"):
        need(insta[k] is False, "META_FALSE_AUTH_" + k)
    for k in ("neverCollectPassword", "neverCopySessionCookies"):
        need(insta[k] is True, "META_CREDENTIAL_" + k)
    need(d["accountConnections"]["chatgpt"]["privatePersonalPluginNotAutomaticallyShareable"] is True,
         "PLUGIN_SHARING")
    roles = d["roleRequest"]
    need(roles["default"] == "creativeCollaborator", "ROLE_DEFAULT")
    need([r["id"] for r in roles["allowed"]] ==
         ["betaReviewer", "creativeCollaborator"], "ONLY_SAFE_ROLES")
    need("ownerAdmin" in roles["deniedByDefault"] and
         "privateDriveMasters" in roles["deniedByDefault"] and
         "CASTDispatch" in roles["deniedByDefault"], "AUTHORITY_LIMITS")
    for k in ("fullProjectAccessRequiresSeparateExplicitOwnerAndProviderAuthorization",
              "accountOwnerPermissionIndependent", "revocable", "leastPrivilege"):
        need(roles[k] is True, "ROLE_REVIEW_" + k)
    handoff = d["handoff"]
    need(handoff["oneClickMeaning"] == "PREPARE_SCOPED_INVITE_PROPOSAL_ONLY", "ONE_CLICK_LAW")
    for k in ("neverStorePersonalContactInPublicArtifacts",
              "unconfiguredProviderButtonMustNeverPretendToLogIn", "noAutomaticInvites",
              "noAutomaticActivation", "offlineSafeUi", "candidatePlanMayBeCopiedLocally"):
        need(handoff[k] is True, "HANDOFF_" + k)
    for k, v in d["boundaries"].items():
        need(v is True, "BOUNDARY_" + k)
    need(d["proof"] and all(v is False for v in d["proof"].values()), "FALSE_PROOF")
    for k in ("buildDispatched", "invitationSent", "productionDeployed", "promotion"):
        need(d[k] is False, "AUTOMATION_" + k)
    need(d["crownStatus"] == "STOP", "CROWN")

    # Do not create a lookalike Google/Meta login page. Only prepare a safe plan.
    need('<button type="button" id="prepare">' in html, "ACTION")
    need("navigator.clipboard.writeText(current)" in html, "LOCAL_COPY")
    need("Google login: PENDING" in html, "GOOGLE_WARNING")
    need("not an invitation" in html.lower(), "INVITE_WARNING")
    need("No passwords, browser cookies or credentials are collected" in html,
         "NO_PASSWORD_CLAIM")
    need("textContent=current" in html and "plan.hidden=false" in html, "SAFE_RENDER")
    need(not re.search(r"<input[^>]*type=['\"]?(?:password|email)", html, re.I), "SENSITIVE_INPUT")
    for unsafe in ("fetch(", "XMLHttpRequest", "WebSocket(", "localStorage.",
                   "sessionStorage.", "document.cookie", "innerHTML", "eval(",
                   "google.accounts.", "instagram.com/accounts/login"):
        need(unsafe not in html, "UNVERIFIED_AUTH_" + unsafe)
    # No named individual, email address, private OAuth secret, or targeted account.
    for forbidden in ("Alex", "Toby", "client_secret", "access_token", "refresh_token"):
        need(forbidden not in html, "PUBLIC_IDENTITY_OR_SECRET")


def self_test() -> None:
    document = json.loads(DOC.read_text(encoding="utf-8"))
    html = UI.read_text(encoding="utf-8")
    audit(document, html)
    for path, key, value in (
        (("identityFlow",), "backendOauthImplemented", True),
        (("accountConnections", "instagram"), "connected", True),
        (("accountConnections", "instagram"), "neverCollectPassword", False),
        (("roleRequest",), "default", "ownerAdmin"),
        (("handoff",), "noAutomaticInvites", False),
        (("proof",), "liveInviteSent", True),
        ((), "invitationSent", True),
        ((), "crownStatus", "GREEN"),
    ):
        copy_d = copy.deepcopy(document)
        cursor = copy_d
        for step in path:
            cursor = cursor[step]
        cursor[key] = value
        try:
            audit(copy_d, html)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe guest access or proof claim accepted: " + key)
    for tampered in (html.replace('type="button" id="prepare"', 'type="password" id="prepare"'),
                     html + '<input type="password">',
                     html + 'fetch("https://example.com")'):
        try:
            audit(document, tampered)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe interface modification passed audit")
    print("GUEST_WIZARD_SOURCE_ONLY_CONSENT_AND_AUTH_REFUSAL_GREEN")


if __name__ == "__main__":
    self_test()
