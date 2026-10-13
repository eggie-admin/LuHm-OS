#!/usr/bin/env python3
"""Read-only Google Cloud billing and Vertex API evidence; never permits spending."""
from __future__ import annotations
import argparse
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler

projectPattern = re.compile(r"[a-z][a-z0-9-]{4,28}[a-z0-9]")

def probe(projectId, getJson):
    if not projectPattern.fullmatch(projectId):
        raise ValueError("RED_INVALID_PROJECT_ID")
    result = {
        "schema": "luhmOs.cloudVideoPreflight.v1", "projectId": projectId,
        "mode": "READ_ONLY_GOOGLE_CLOUD", "billing": "UNVERIFIED",
        "vertexApi": "UNVERIFIED", "iam": "UNVERIFIED",
        "veoModelEntitlement": "UNVERIFIED", "quota": "UNVERIFIED",
        "gcsWrite": "UNVERIFIED", "sql": "UNVERIFIED",
        "readyToSpend": False, "publicationAuthority": False, "crown": "STOP"
    }
    urls = {
        "billing": "https://cloudbilling.googleapis.com/v1/projects/" + projectId + "/billingInfo",
        "vertexApi": "https://serviceusage.googleapis.com/v1/projects/" + projectId + "/services/aiplatform.googleapis.com",
    }
    for kind, url in urls.items():
        try:
            payload = getJson(url)
            if kind == "billing":
                enabled = payload.get("billingEnabled")
                valid = payload.get("projectId") == projectId and type(enabled) is bool
                result[kind] = ("ENABLED" if enabled else "DISABLED") if valid else "INVALID_PROVIDER_RESPONSE"
            else:
                # Numeric project aliases require separately verified identity; fail closed here.
                name = payload.get("name", "")
                valid = name == "projects/" + projectId + "/services/aiplatform.googleapis.com"
                state = payload.get("state")
                result[kind] = state if valid and state in ("ENABLED", "DISABLED") else "INVALID_PROVIDER_RESPONSE"
        except HTTPError as error:
            result[kind] = "ACCESS_DENIED_OR_NOT_FOUND" if error.code in (401, 403, 404) else "PROVIDER_HTTP_ERROR"
        except (URLError, TimeoutError, ValueError, TypeError, OSError, KeyError):
            result[kind] = "UNVERIFIED_NETWORK_OR_RESPONSE"
    return result

def authenticatedGet():
    try:
        import google.auth
        from google.auth.transport.requests import Request as GoogleRequest
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        credentials.refresh(GoogleRequest())
        token = credentials.token
        if not token:
            raise RuntimeError("RED_GOOGLE_CLOUD_IDENTITY_UNAVAILABLE")
    except Exception:
        raise RuntimeError("RED_GOOGLE_CLOUD_IDENTITY_UNAVAILABLE") from None

    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, request, response, code, message, headers, newUrl):
            return None

    opener = build_opener(NoRedirect())
    def getJson(url):
        if not (url.startswith("https://cloudbilling.googleapis.com/v1/projects/") or
                url.startswith("https://serviceusage.googleapis.com/v1/projects/")):
            raise ValueError("RED_PROVIDER_URL")
        with opener.open(Request(url, method="GET", headers={"Authorization": "Bearer " + token}), timeout=12) as response:
            return json.load(response)
    return getJson

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true")
    parser.add_argument("--project", default=os.getenv("GOOGLE_CLOUD_PROJECT", ""))
    args = parser.parse_args(argv)
    if not args.online:
        print(json.dumps({"schema":"luhmOs.cloudVideoPreflight.v1","mode":"OFFLINE_NO_REQUESTS",
            "cloudProjectConfigured":bool(args.project),"billing":"UNVERIFIED",
            "vertexApi":"UNVERIFIED","iam":"UNVERIFIED","quota":"UNVERIFIED",
            "readyToSpend":False,"publicationAuthority":False,"crown":"STOP"},indent=2))
        return 0
    if not projectPattern.fullmatch(args.project):
        raise SystemExit("CROWN_STOP_PROJECT_ID_REQUIRED")
    try:
        result = probe(args.project, authenticatedGet())
    except RuntimeError:
        result = {"schema":"luhmOs.cloudVideoPreflight.v1","projectId":args.project,
            "mode":"READ_ONLY_GOOGLE_CLOUD","cloudIdentity":"UNAVAILABLE",
            "billing":"UNVERIFIED","vertexApi":"UNVERIFIED","iam":"UNVERIFIED",
            "quota":"UNVERIFIED","readyToSpend":False,
            "publicationAuthority":False,"crown":"STOP"}
    print(json.dumps(result,indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

