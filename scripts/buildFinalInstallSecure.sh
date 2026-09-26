#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SECURITY_TMP="${RUNNER_TEMP:-/tmp}/luhm-enterprise-security-audit.txt"
python3 tools/auditEnterpriseSecurity.py | tee "$SECURITY_TMP"

bash scripts/buildFinalInstallCandidate.sh

cp "$SECURITY_TMP" build/android/enterprise-security-audit.txt
cp doctrine/enterpriseSecurity-20260926.json build/android/
openssl version | tee build/android/openssl-version.txt

grep -q 'rikka.shizuku.ShizukuProvider' build/android/manifest.txt
grep -q 'assets/cockpit/index.html' build/android/ziplist.txt
grep -q 'assets/cockpit/jquery/luhm.delivery.js' build/android/ziplist.txt
! grep -q 'android.permission.REQUEST_INSTALL_PACKAGES' build/android/permissions.txt
! grep -q 'android.permission.MANAGE_EXTERNAL_STORAGE' build/android/permissions.txt
! grep -q 'android.permission.QUERY_ALL_PACKAGES' build/android/permissions.txt

grep -q 'dev.rikka.shizuku:api:13.1.5' addons/kai_webview/export_plugin.gd
grep -q 'dev.rikka.shizuku:provider:13.1.5' addons/kai_webview/export_plugin.gd
grep -q 'autoPermissionRequest", false' native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/ShizukuCapability.kt
! grep -R -nE 'Shizuku\.newProcess|bindUserService|Runtime\.getRuntime\(\)\.exec|ProcessBuilder\(|su[[:space:]]+-c' native/kaiwebview cockpit

sha256sum doctrine/enterpriseSecurity-20260926.json tools/auditEnterpriseSecurity.py >> build/android/source-components-sha256.txt
printf 'enterprise_source_security=GREEN\nenterprise_external_gates=AMBER\nshizuku=OPTIONAL_EXPLICIT_NATIVE_GRANT\ngoogle_connector_token_export=FORBIDDEN\nopenvpn=OPTIONAL_NOT_ACTIVATED\n' >> build/android/final-install-receipt.txt

echo 'KAI 9000 ENTERPRISE SECURITY SOURCE/BUILD GATES GREEN; EXTERNAL ENTERPRISE GATES REMAIN AMBER'
