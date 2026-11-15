#!/usr/bin/env python3
"""Four-pass private Canon art Android gallery source-only gate, with negative controls."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path): return (ROOT/path).read_text(encoding="utf-8")
H=read("frontEnd/index.html")
C=read("frontEnd/styles.css")
J=read("frontEnd/canonGallery.js")
K=read("androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt")
B=json.loads(read("doctrine/androidWeb3BridgeV2.json"))
L=json.loads(read("doctrine/privateCanonArtFourPassIntake20261114.json"))
P=read(".github/workflows/aramoor-samsung-arm64-test-apk.yml")

def audit(h=H,c=C,j=J,k=K,b=B,l=L,p=P):
    missing=[]
    def need(x,msg):
        if not x:missing.append(msg)
    need('data-luhm-canon-gallery' in h and 'data-luhm-gallery-pick' in h and 'data-luhm-gallery-file' in h,"GALLERY_DOM")
    need('data-luhm-gallery-button' in h and 'Canon Gallery' in h and 'canonGallery.js' in h,"VISIBLE_ENTRY")
    need('.canonGalleryLayer[hidden]' in c and 'z-index:85' in c,"MOBILE_OVERLAY_HIDDEN")
    need('role="dialog"' in h and 'aria-label="Close Canon gallery"' in h,"ACCESSIBILITY")
    need('postMessage(JSON.stringify({ type: "local_art_pick_requested" }))' in j,"TYPED_PICK")
    need('URL.createObjectURL' in j and 'URL.revokeObjectURL' in j and 'replaceChildren()' in j,"SESSION_OBJECT_LIFECYCLE")
    need('caption.textContent' in j and 'img.alt' in j and 'window.LuHmCanonGallery' in j,"SAFE_DISPLAY")
    need(all(t not in j for t in ('fetch(', 'XMLHttpRequest', 'localStorage.', 'sessionStorage.', 'eval(', '.innerHTML','http://','https://')),"NO_EXTERNAL_OR_PERSISTENCE")
    need('MAX_IMAGES = 8' in j and 'MAX_IMAGE_BYTES = 16 * 1024 * 1024' in j,"BROWSER_BOUNDS")
    need('Intent.ACTION_OPEN_DOCUMENT' in k and 'LOCAL_ART_PICK_REQUEST' in k,"DOCUMENT_PICKER")
    need('onMainActivityResult' in k and 'requestCode != LOCAL_ART_PICK_REQUEST' in k,"PICKER_RESULT_SCOPE")
    need('uri.scheme != "content"' in k and 'getType(uri)' in k,"MIME_AND_URI_GUARDS")
    need('MAX_ART_BYTES = 16L * 1024 * 1024' in k and 'MAX_ART_PICKS = 8' in k,"NATIVE_BOUNDS")
    need('MAX_PREVIEW_EDGE = 1600' in k and 'BitmapFactory.Options' in k,"MOBILE_IMAGE_DOWNSAMPLE")
    need('allowContentAccess = false' in k and 'allowFileAccess = false' in k,"NO_FILE_SCHEME")
    need('sourceOrigin.toString() != LOCAL_ORIGIN' in k and 'isMainFrame' in k,"ORIGIN_BOUNDARY")
    need('window.LuHmCanonGallery.addFromNative(' in k and 'JSONObject.quote(dataUrl)' in k,"SAFE_BRIDGE_RENDER")
    need('"world_requested", "aramoor_requested", "cockpit_ready", "local_art_pick_requested" -> setOf("type")' in k,"EXACT_TYPED_BRIDGE_KEYS")
    need('addJavascriptInterface' not in k and 'android.permission.INTERNET' not in k,"NO_PRIVILEGE_ESCALATION")
    types=[x.get('type') for x in b.get('javascriptToNative',[])]
    need(types==['cockpitReady','oniRequested','worldRequested','aramoorRequested','localArtPickRequested'],"CANON_TYPE_ARRAY")
    need(b.get('privateCanonGallery',{}).get('privateArtBundledIntoPublicSource') is False,"PUBLIC_ASSET_FIREWALL")
    need(l.get('status')=='PRIVATE_ART_REFERENCE_BYTES_VERIFIED_RUNTIME_IMPORT_PENDING',"NO_FAKE_RUNTIME")
    assets=l.get('assets',[])
    need(len(assets)==3 and len({x['sha256'] for x in assets})==2,"DEDUP_SOURCE_IMAGES")
    need(all(x.get('publicAllowed') is False and x.get('autoRuntimeBundled') is False for x in assets),"RIGHTS_FIREWALL")
    need(l.get('samplerVideo',{}).get('deviceGameplayProven') is False,"NO_FAKE_SAMSUNG")
    need(l.get('failClosed',{}).get('finalCrown')=='STOP',"CROWN_STOP")
    need('python3 tools/privateCanonArtGalleryAudit.py' in p and 'node --check frontEnd/canonGallery.js' in p,"APK_GATED")
    return missing

def main():
    errors=audit()
    mutations=[
        ("removed-gallery",dict(h=H.replace('data-luhm-canon-gallery','data-broken-gallery'))),
        ("exfiltration",dict(j=J+"\nfetch('https://example.net/art')")),
        ("no-revoke",dict(j=J.replace('URL.revokeObjectURL','URL.revokeImaginaryURL'))),
        ("bridge-origin",dict(k=K.replace('sourceOrigin.toString() != LOCAL_ORIGIN','false'))),
        ("enable-webview-files",dict(k=K.replace('allowFileAccess = false','allowFileAccess = true'))),
        ("no-picker",dict(k=K.replace('Intent.ACTION_OPEN_DOCUMENT','Intent.ACTION_VIEW'))),
        ("rights-bypass",dict(l={**L,"assets":[{**x,"publicAllowed":True} for x in L["assets"]]})),
        ("runtime-fake",dict(l={**L,"status":"FULL_GAMEPLAY_GREEN"})),
        ("unbounded",dict(k=K.replace('MAX_ART_BYTES = 16L * 1024 * 1024','MAX_ART_BYTES = Long.MAX_VALUE'))),
    ]
    for name,overrides in mutations:
        if not audit(**overrides):errors.append("NEGATIVE_CONTROL_FALSE_GREEN_"+name)
    if errors:raise SystemExit("RED_PRIVATE_CANON_ART_GALLERY:"+",".join(errors))
    print("GREEN_PRIVATE_CANON_ART_GALLERY_SOURCE_9_NEGATIVE_CONTROLS")
    print("PRIVATE_ART_BYTES_NOT_IN_GITHUB_RELEASE_OR_APK")
    print("PHYSICAL_SAMSUNG_PICKER_AND_GAMEPLAY_PENDING")

if __name__=="__main__":main()
