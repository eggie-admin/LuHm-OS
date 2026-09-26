#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
checks=[]
def check(name,condition,detail):
    status='GREEN' if condition else 'RED';checks.append((name,status,detail));print(f'{status:5} {name}: {detail}')
manifest_path=ROOT/'doctrine/finalInstallRoute-20260926.json'
agent_path=ROOT/'agents/luhm-agent-mesh/finalInstallWorkflow.json'
widget_path=ROOT/'cockpit/jquery/luhm.delivery.js'
index_path=ROOT/'cockpit/index.html'
app_path=ROOT/'cockpit/app.js'
webview_path=ROOT/'native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt'
profile_path=ROOT/'native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/SamsungSystemProfile.kt'
required=[manifest_path,agent_path,widget_path,index_path,app_path,webview_path,profile_path]
check('01_source_authority',all(p.is_file() for p in required),'required final-route sources exist')
manifest=json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
agent=json.loads(agent_path.read_text()) if agent_path.is_file() else {}
check('02_project_scope',manifest.get('source',{}).get('promotion')=='PROPOSED_ONLY' and manifest.get('authority',{}).get('human_final_authority') is True,'candidate remains human-promoted only')
hard=manifest.get('hard_boundaries',{})
check('03_privilege_boundary',hard.get('root_bridge') is False and hard.get('selinux_disable') is False and hard.get('silent_install') is False,'no root, SELinux bypass or silent install')
wv=webview_path.read_text() if webview_path.is_file() else ''
check('04_webview_boundary','WebViewAssetLoader' in wv and 'WEB_MESSAGE_LISTENER' in wv and 'addJavascriptInterface' not in wv,'packaged origin + typed WebMessage listener')
profile=profile_path.read_text() if profile_path.is_file() else ''
check('05_samsung_profile','getCurrentWebViewPackage' in profile and 'isDeviceOwnerApp' in profile and 'isProfileOwnerApp' in profile,'Samsung/WebView/admin state is detect-only')
front='\n'.join([index_path.read_text(),app_path.read_text(),widget_path.read_text()])
check('06_widget_boundary','luhmDelivery' in front and 'data-app-background' in front and 'data-app-exit' in front and 'Runtime.getRuntime().exec' not in front,'receipt UI and explicit app lifecycle controls exist without installer/shell path')
helpers=agent.get('helpers',{})
check('07_agent_mesh',agent.get('boss')=='Lum' and set(['Kiri','Tetsu','Momo','Shiori','Kugi']).issubset(helpers),'Lum + bounded oni workflow present')
openai=agent.get('openai_agent_boundary',{})
check('08_agent_secret_boundary',openai.get('api_key_in_apk') is False and openai.get('api_key_in_webview') is False and openai.get('background_autonomous_publish') is False,'connector orchestration without embedded OpenAI secrets')
route=manifest.get('delivery_route',[]);drive=manifest.get('google_drive',{})
check('09_delivery_receipts','github_exact_head_build' in route and 'google_drive_private_source_of_truth_build_directory' in route and drive.get('public_workspace_allowed') is False,'GitHub to private Drive route requires receipts')
law=manifest.get('green_law',{})
check('10_green_semantics',law.get('source_build_delivery_may_be_green_while_runtime_is_amber') is True and 'physical_samsung_install' in law.get('runtime_green_requires',[]),'device proof cannot be inferred from CI')
failed=[name for name,status,_ in checks if status!='GREEN']
print(json.dumps({'passes':checks,'result':'GREEN' if not failed else 'RED','failed':failed},indent=2))
sys.exit(1 if failed else 0)
