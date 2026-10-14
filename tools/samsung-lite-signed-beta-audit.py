#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[1]/".github/workflows/samsung-lite-signed-beta.yml"
text=p.read_text(encoding="utf-8")
checks={
"manual-cast": "workflow_dispatch:" in text and '== "cast"' in text,
"owner": 'test "$GITHUB_ACTOR"' in text,
"exact-main": 'gh api "repos/$GITHUB_REPOSITORY/branches/main"' in text,
"owner-key-secret": "secrets.LUHM_BETA_SIGNING_P12_B64" in text,
"stable-fingerprint": 'test "$OBSERVED" == "$TRUSTED_SIGNER"' in text,
"release-mode": "--export-release 'Android Proposed'" in text,
"nondebug": "RED_DEBUG_CERTIFICATE_MODE" in text,
"beta-app-id": "art.eggiebagelface.luhmos.beta" in text,
"private-only": "gh release create" not in text and "gh release upload" not in text,
"no-wipe": "pm clear" not in text and "pm uninstall" not in text and "adb uninstall" not in text,
"no-device-claims": '"deviceProof":False' in text and '"betaUpgradeProof":False' in text,
}
for name,passed in checks.items():
    print(("GREEN" if passed else "RED")+"_"+name)
raise SystemExit(0 if all(checks.values()) else 2)
