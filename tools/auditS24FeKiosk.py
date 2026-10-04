#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
policy=json.loads((ROOT/'doctrine/s24feKioskHarness-20260926.json').read_text())
wv=(ROOT/'native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt').read_text()
bridge=(ROOT/'scripts/platform/kaiWebViewBridge.gd').read_text()
main=(ROOT/'scripts/main.gd').read_text()
html=(ROOT/'cockpit/index.html').read_text()
css=(ROOT/'cockpit/styles.css').read_text()
deck=(ROOT/'cockpit/jquery/luhm.deck.js').read_text()
manifest=(ROOT/'native/kaiwebview/kaiwebview/src/main/AndroidManifest.xml').read_text()
checks=[]
def gate(name,ok,detail):
    state='GREEN' if ok else 'RED'; checks.append((name,state,detail)); print(f'{state:5} {name}: {detail}')

gate('01_launch_full', policy.get('launch_mode')=='full' and '_enter_backend("full")' in main, 'candidate launches into full caged glass')
gate('02_modes', all(x in wv for x in ['"full"','"mini"','"pet"','"bubble"']) and all(x in html for x in ['data-shell="full"','data-shell="mini"','data-shell="pet"','data-shell="bubble"']), 'full/mini/pet/bubble state machine present')
gate('03_winamp_pet_bubble', 'Winamp style minimal shell' in html and 'Lum pet inspector' in html and 'Lum chat head bubble' in html and 'miniShell' in css and 'petShell' in css and 'bubbleShell' in css, 'compact UI shells present')
gate('04_background_semantics', 'moveTaskToBack(true)' in wv and 'persistent service' not in wv.lower() and 'backgroundTask' in bridge, 'background means ordinary Android task backgrounding')
gate('05_exit_semantics', 'finishAndRemoveTask()' in wv and 'System.exit' not in wv and 'killProcess' not in wv, 'explicit clean task exit, no process kill shortcut')
gate('06_immersive_soft_kiosk', 'WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE' in wv and 'SYSTEM_UI_FLAG_IMMERSIVE_STICKY' in wv, 'soft immersive kiosk supports modern and legacy Android paths')
gate('07_caged_webview', all(x in wv for x in ['WebViewAssetLoader','allowFileAccess = false','allowContentAccess = false','MIXED_CONTENT_NEVER_ALLOW','domStorageEnabled = false','setSupportMultipleWindows(false)']), 'WebView local origin and unsafe capabilities disabled')
gate('08_no_overlay_install_privilege', 'SYSTEM_ALERT_WINDOW' not in manifest and 'REQUEST_INSTALL_PACKAGES' not in manifest and 'MANAGE_EXTERNAL_STORAGE' not in manifest, 'no draw-over-other-apps or installer/storage super-permissions')
gate('09_bridge_allowlist', all(x in deck for x in ["'ui.mode'","'app.background'","'app.exit'"]) and 'shizuku.permission.request' not in deck and 'Runtime.getRuntime().exec' not in wv, 'UI behavior is typed; no WebView privilege/shell path')
gate('10_canary_semantics', policy['webview']['provider_selection']=='Android system controlled' and 'com.google.android.webview.canary' in manifest and 'com.chrome.canary' in manifest, 'Canary packages are detectable but provider selection stays with Android')
failed=[n for n,s,_ in checks if s!='GREEN']
print(json.dumps({'schema':'luhm.s24fe.kiosk.audit.v1','result':'GREEN' if not failed else 'RED','passes':checks,'failed':failed},indent=2))
sys.exit(1 if failed else 0)
