#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'frontEnd/index.html').read_text(encoding='utf-8')
JS = (ROOT / 'frontEnd/jquery/luhm.chat.workbench.js').read_text(encoding='utf-8')
APP = (ROOT / 'frontEnd/app.js').read_text(encoding='utf-8')
CSS = (ROOT / 'frontEnd/chat-workbench.css').read_text(encoding='utf-8')

required_actions = [
    'continue', 'audit', 'verify', 'build', 'fix',
    'assets', 'research', 'drive', 'crown'
]
for action in required_actions:
    assert f'data-chat-action="{action}"' in HTML, action
    assert f'{action}:' in JS, action

for token in [
    'data-chat-context="branch"',
    'data-chat-context="sourceRef"',
    'data-chat-context="target"',
    'data-luhm-oni-dock',
    'data-chat-voice',
    'data-chat-attach',
    'data-chat-stop',
    'data-chat-state-line',
    'textarea',
]:
    assert token in HTML, token

for event in [
    'luhm:chat:assistant',
    'luhm:chat:receipt',
    'luhm:chat:context',
    'luhm:chat:state',
    'luhm:chat:workbench-submit',
]:
    assert event in JS or event in APP, event

# Crown quick action is preparation only. The front end must not expose
# direct promotion/signing/publishing authority.
assert 'Prepare Crown' in HTML
assert 'Do not promote' in JS
for forbidden in ['merge_main(', 'production_sign(', 'publish_release(', 'self_approve(']:
    assert forbidden not in JS
    assert forbidden not in APP

# The bridge carries requests outward but does not invent observed success.
assert 'observed: false' in APP
assert 'luhm:transport:send' in APP

# The UI must keep source identity visible and UNKNOWN-safe.
assert "branch: 'UNKNOWN'" in JS
assert "sourceRef: 'UNKNOWN'" in JS
assert '.chatContextPill.isUnknown' in CSS

# Accessibility and mobile/reduced-motion contracts.
assert 'aria-live="polite"' in HTML
assert '@media (max-width: 720px)' in CSS
assert '@media (prefers-reduced-motion: reduce)' in CSS

print('LUHM_CHAT_WORKBENCH_GREEN')
