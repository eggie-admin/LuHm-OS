#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

contract=json.loads((root/"doctrine/staticChatTransmogrifierV1.json").read_text(encoding="utf-8"))
experience=json.loads((root/"doctrine/inChatExperienceV1.json").read_text(encoding="utf-8"))
index=(root/"host/harness/index.html").read_text(encoding="utf-8")
js=(root/"host/harness/chat-transmogrifier.js").read_text(encoding="utf-8")
css=(root/"host/harness/chat-transmogrifier.css").read_text(encoding="utf-8")
widget=(root/"host/harness/widget.html").read_text(encoding="utf-8")
harness=(root/"host/mcp/luhmHarness.py").read_text(encoding="utf-8")

need(contract.get("schema")=="luhmOs.staticChatTransmogrifier.v1","static chat schema drift")
need(contract.get("authority")=="Professor" and contract.get("boss")=="lum","authority chain drift")
need([x.get("id") for x in contract.get("messageClasses",[])]==["chat","tool","proof","control"],"message class order drift")
need(contract.get("fourByFour",{}).get("horizontalBeats")==["hear","resolve","act","verify"],"4:4 beat drift")
security=contract.get("security",{})
for key in ("evalAllowed","newFunctionAllowed","arbitraryRemoteScriptAllowed","thirdPartyCdnAllowed","directFilesystemAccessAllowed","directShellAuthority","directNetworkAuthority","providerSecretAccess","htmlFromUntrustedMessageAllowed"):
    need(security.get(key) is False,f"security drift: {key}")
authority=contract.get("authorityBoundary",{})
for key in ("mutationAuthority","mergeAuthority","deploymentAuthority","publicationAuthority","signingAuthority","greenAuthority","crownAuthority"):
    need(authority.get(key) is False,f"authority leak: {key}")
need(contract.get("donorStudy",{}).get("mirc",{}).get("codeCopied") is False,"mIRC code-copy boundary missing")
need('chat-transmogrifier.css' in index and 'chat-transmogrifier.js' in index,"standalone static chat assets not wired")
need('data-luhm-static-chat' in index,"standalone mount target missing")
need("window.LuhmStaticChat" in js,"static chat export missing")
need("window.openai?.sendFollowUpMessage" in js,"ChatGPT follow-up bridge missing")
need('luhm:static-chat:command' in js,"standalone fallback event missing")
need("innerHTML" not in js,"unsafe innerHTML added")
need("eval(" not in js and "new Function" not in js,"dynamic code execution added")
need('id="staticChatStatus"' in widget and 'id="staticChatInput"' in widget,"in-chat focus deck missing")
need('"staticChat": static_chat' in harness,"MCP payload missing static chat contract")
need('"staticChat": static_chat' in harness,"harness config missing static chat contract")
need('"chat-transmogrifier.css"' in harness and '"chat-transmogrifier.js"' in harness,"asset allowlist missing static chat files")
need(experience.get("sources",{}).get("staticChat")=="doctrine/staticChatTransmogrifierV1.json","experience source pointer missing")
need("staticChat" in experience.get("runtime",{}).get("panels",[]),"experience panel missing")

print(json.dumps({
  "schema":"luhmOs.staticChatTransmogrifierAudit.v1",
  "status":"GREEN_STATIC_CHAT_TRANSMOGRIFIER_CANDIDATE" if not errors else "RED_STATIC_CHAT_TRANSMOGRIFIER_CANDIDATE",
  "messageClasses":["chat","tool","proof","control"],
  "liveChatGptProof":False,
  "sourceOnly":True,
  "promotion":False,
  "crownStatus":"STOP",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)
