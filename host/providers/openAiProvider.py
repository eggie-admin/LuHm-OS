#!/usr/bin/env python3
"""Server-side OpenAI Responses adapter for LuHm OS.

External SDK spellings are isolated in this file. LuHm callers use camelHump
functions and bounded packets. This adapter never grants GREEN, Crown, publish,
merge, build, or canon authority.
"""
from __future__ import annotations

import json
import os
import uuid
from typing import Any

from openai import OpenAI

defaultModel = "gpt-5.6-sol"

def getModelId() -> str:
    return os.environ.get("LUHM_OPENAI_MODEL", defaultModel).strip() or defaultModel

def hasOpenAiCredential() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())

def makeClient() -> OpenAI:
    apiKey = os.environ.get("OPENAI_API_KEY", "").strip()
    if not apiKey:
        raise RuntimeError("OPENAI_API_KEY is not configured on the trusted host")

    orgId = os.environ.get("OPENAI_ORG_ID", "").strip() or None
    projectId = os.environ.get("OPENAI_PROJECT_ID", "").strip() or None

    return OpenAI(
        api_key=apiKey,
        organization=orgId,
        project=projectId,
        timeout=60.0,
        max_retries=2,
    )

def makeRequestMeta(taskId: str, sourceRef: str, scopeId: str) -> dict[str, str]:
    return {
        "taskId": str(taskId)[:64],
        "sourceRef": str(sourceRef)[:64],
        "scopeId": str(scopeId)[:64],
    }

def createTextResponse(
    *,
    instructions: str,
    userText: str,
    taskId: str,
    sourceRef: str,
    scopeId: str,
) -> dict[str, Any]:
    client = makeClient()
    clientRequestId = str(uuid.uuid4())

    response = client.responses.create(
        model=getModelId(),
        instructions=instructions,
        input=userText,
        store=False,
        metadata=makeRequestMeta(taskId, sourceRef, scopeId),
        extra_headers={"X-Client-Request-Id": clientRequestId},
    )

    return {
        "schema": "luhmOs.openAiTextResult.v1",
        "providerId": "openAi",
        "modelId": getattr(response, "model", getModelId()),
        "responseId": getattr(response, "id", "unknown"),
        "requestId": getattr(response, "_request_id", None),
        "clientRequestId": clientRequestId,
        "outputText": response.output_text,
        "providerSuccessMeans": "observed",
        "greenAuthority": False,
        "crownStatus": "stop",
    }

def createStructuredResponse(
    *,
    instructions: str,
    userText: str,
    schemaName: str,
    jsonSchema: dict[str, Any],
    taskId: str,
    sourceRef: str,
    scopeId: str,
) -> dict[str, Any]:
    client = makeClient()
    clientRequestId = str(uuid.uuid4())

    response = client.responses.create(
        model=getModelId(),
        instructions=instructions,
        input=userText,
        store=False,
        metadata=makeRequestMeta(taskId, sourceRef, scopeId),
        text={
            "format": {
                "type": "json_schema",
                "name": schemaName,
                "strict": True,
                "schema": jsonSchema,
            }
        },
        extra_headers={"X-Client-Request-Id": clientRequestId},
    )

    return {
        "schema": "luhmOs.openAiStructuredResult.v1",
        "providerId": "openAi",
        "modelId": getattr(response, "model", getModelId()),
        "responseId": getattr(response, "id", "unknown"),
        "requestId": getattr(response, "_request_id", None),
        "clientRequestId": clientRequestId,
        "data": json.loads(response.output_text),
        "providerSuccessMeans": "observed",
        "greenAuthority": False,
        "crownStatus": "stop",
    }
