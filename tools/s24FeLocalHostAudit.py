#!/usr/bin/env python3
from pathlib import Path
import json, sys

root=Path(__file__).resolve().parents[1]
errors=[]

def req(ok,msg):
    if not ok: errors.append(msg)

def load(path):
    p=root/path
    req(p.is_file(),f"missing {path}")
    return json.loads(p.read_text()) if p.is_file() else {}

host=load("doctrine/s24FeLocalHostV1.json")
source=load("doctrine/SOURCE_OF_TRUTH.json")
chat=load("doctrine/projectChatCanonV1.json")
x11=load("doctrine/shizukuX11UnifiedV1.json")

req(host.get("primaryHost",{}).get("surface")=="ordinaryTermuxOutsideSecureFolder","ordinary Termux is not canonical host")
req(host.get("secureFolder",{}).get("defaultControlPlane") is False,"Secure Folder regained default control-plane status")
req(host.get("secureFolder",{}).get("requiredForNormalWorkflow") is False,"Secure Folder incorrectly required")
req(host.get("localStack",{}).get("termux")=="authoritativeMobileHost","Termux host role drift")
req(host.get("loopbackLaw",{}).get("phoneIsNotPublicWebServer") is True,"phone public-web-server prohibition missing")
req(host.get("migrationLaw",{}).get("newMobileWorkTargetsOrdinaryTermux") is True,"new mobile work not bound to ordinary Termux")
req(host.get("migrationLaw",{}).get("doNotMoveOrDeleteSecureFolderDataWithoutExplicitProfessorApproval") is True,"Secure Folder migration deletion guard missing")

mobile=source.get("mobileHost",{})
req(mobile.get("contract")=="doctrine/s24FeLocalHostV1.json","source truth local-host contract missing")
req(mobile.get("host")=="ordinaryTermuxOutsideSecureFolder","source truth host drift")
req(mobile.get("secureFolder")=="OPTIONAL_ISOLATION_ONLY","source truth Secure Folder role drift")

req(chat.get("mobileHost",{}).get("canonical")=="ordinaryTermuxOutsideSecureFolder","chat canon mobile host drift")
req(chat.get("mobileHost",{}).get("secureFolderRole")=="optionalIsolationOnly","chat canon Secure Folder role drift")

req(x11.get("mobileHost")=="doctrine/s24FeLocalHostV1.json","Shizuku/X11 lane local-host binding missing")
req(x11.get("runtimeLayers",{}).get("termux")=="authoritativeControlPlaneOutsideSecureFolder","Shizuku/X11 Termux host drift")
req(x11.get("runtimeLayers",{}).get("secureFolder")=="optionalIsolationOnly","Shizuku/X11 Secure Folder role drift")

print(json.dumps({
  "schema":"luhmOs.s24FeLocalHostAudit.v1",
  "status":"greenS24FeLocalHostSource" if not errors else "redS24FeLocalHostSource",
  "host":"ordinaryTermuxOutsideSecureFolder",
  "secureFolder":"optionalIsolationOnly",
  "physicalRuntime":"pendingDeviceReceipt",
  "errors":errors,
  "crownStatus":"stop"
},indent=2))
sys.exit(1 if errors else 0)
