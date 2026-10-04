#!/usr/bin/env python3
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'doctrine/androidWebViewCockpit-20260925.json').read_text())
index=(root/'cockpit/index.html').read_text()
deck=(root/'cockpit/jquery/luhm.deck.js').read_text()
arch=(root/'cockpit/ARCHITECTURE.md').read_text()
assert manifest['status']=='AMBER_DESIGN_CANDIDATE'
assert manifest['architecture']['bottom_layer']=='full-screen Godot 4 canvas'
assert manifest['architecture']['overlay']=='caged Android WebView'
assert manifest['security']['webview_asset_loader_required'] is True
assert manifest['security']['runtime_cdn'] is False
assert manifest['production_actions_authorized'] is False
assert "connect-src 'none'" in index
assert 'window.LuHmNative' in deck
for allowed in ['chat.send','panel.set','status.request','model.select','cms.select']:
    assert allowed in deck
for forbidden in ['KAI.exec(', 'KAI.shell(', 'eval(', 'readFile(']:
    assert forbidden not in deck
assert 'WebViewAssetLoader' in arch
assert 'AI proposes. Policy authorizes. CI proves. Human promotes.' in arch
print('AMBER cockpit static audit: PASS')
