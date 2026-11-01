#!/usr/bin/env python3
"""LuHm brand seal MCP Apps widget source registration.

Adds a distinct *candidate* UI resource. Existing published cockpit and mobile
routes remain unchanged. Does not boot a VM, update a hosted plugin or deploy.
"""
from __future__ import annotations
import base64
import importlib.util
from pathlib import Path
from typing import Any

RESOURCE="ui://luhm-os/brand-vm-seal-v1.html"
MIME="text/html;profile=mcp-app"
HISTORICAL_GODOT="https://luhm-os-godot-harness-green.onrender.com"


def register_brand_vm_seal(server:Any, *,root:Path,annotations:Any)->None:
    source=root/"tools"/"brandVmSealAudit.py"
    policy=root/"doctrine"/"brandVmArchitectureSealV1.json"
    art=root/"publicationSite"/"brandSealCandidate.svg"
    page=root/"publicationSite"/"vmBootPreview.html"
    if not all(p.is_file() for p in (source,policy,art,page)):
        raise RuntimeError("RED_VM_BRAND_SOURCE_MISSING")
    spec=importlib.util.spec_from_file_location("brandVmSealAudit",source)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_VM_BRAND_AUDITOR_IMPORT")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    @server.resource(
       RESOURCE,name="luhm-brand-vm-seal",
       title="LuHm-OS · Branded Machine Seal Preview",
       description="Mobile-friendly original vector and simulated VM boot UI. Explicitly NOT a hypervisor, real kernel or public release.",
       mime_type=MIME,
       meta={
          "ui":{"prefersBorder":True,
                "csp":{"connectDomains":[],
                       "resourceDomains":[],
                       "frameDomains":[HISTORICAL_GODOT]}},
          "openai/ui":{"availableDisplayModes":["inline","fullscreen"]},
          "openai/widgetDescription":"LuHm branded source loader, simulated boot and optional historical Godot web-harness handoff."
       }
    )
    def luhm_brand_vm_seal_resource()->str:
        verified=module.audit()
        if verified["issues"]:
            raise RuntimeError("RED_VM_BRAND_AUDIT")
        data=base64.b64encode(art.read_bytes()).decode("ascii")
        html=page.read_text(encoding="utf8")
        return html.replace('src="brandSealCandidate.svg"',
                            'src="data:image/svg+xml;base64,'+data+'"')

    @server.tool(
       name="luhm_open_brand_vm_seal",
       title="Open LuHm-OS VM-style brand seal preview",
       description="Show the in-app candidate source loader. Animation is not an OS boot. No VM is started, no plugin installed, and Godot is user-clicked only.",
       annotations=annotations,
       meta={"ui":{"resourceUri":RESOURCE,"visibility":["model","app"]},
             "openai/outputTemplate":RESOURCE,
             "openai/toolInvocation/invoking":"Opening source-only LuHm machine seal…",
             "openai/toolInvocation/invoked":"LuHm simulated machine seal ready."}
    )
    def luhm_open_brand_vm_seal()->dict[str,Any]:
        return {
           "schema":"luhmOs.inChatBrandVmSeal.v1",
           "surface":"mcp-app",
           "resourceUri":RESOURCE,
           "status":module.audit(),
           "existingHistoricalWebHost":HISTORICAL_GODOT,
           "liveGuestRunning":False,
           "candidatePluginInstalled":False,
           "realKernelBooted":False,
           "publicationAuthorized":False,
        }
