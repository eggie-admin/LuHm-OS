#!/usr/bin/env bash
# LuHm OS owner-only read-only GitHub signing gate inspection.
# Never reads secret values, creates signing material, or dispatches a build.
set -euo pipefail
REPO="eggie-admin/LuHm-OS"
ENV="luhm-beta-signing"
fail() { printf 'RED_SIGNING_GATE: %s\n' "$*" >&2; exit 2; }
for bin in gh jq python3; do command -v "$bin" >/dev/null || fail "missing tool: $bin"; done
gh auth status >/dev/null 2>&1 || fail "sign in as repository owner using gh auth login"
actor="$(gh api user --jq '.login')"
[[ "$actor" == "eggie-admin" ]] || fail "repository owner access required"
gh api "repos/$REPO/branches/main" --jq '.protected' | grep -qx true ||
  fail "main has no active branch protection/ruleset"
policy="$(gh api "repos/$REPO/environments/$ENV")" ||
  fail "cannot read environment protection (gh account needs admin read)"
jq -e '(.protection_rules | any(.type == "required_reviewers" and
          .prevent_self_review == true and
          ((.reviewers // []) | length > 0))) and
       (.deployment_branch_policy.protected_branches == true)' <<<"$policy" >/dev/null ||
  fail "environment needs independent required reviewer, prevent-self-review and protected branches"
required=(
  LUHM_SIGNING_POLICY_READ_TOKEN
  LUHM_BETA_SIGNING_P12_B64
  LUHM_BETA_SIGNING_PASSWORD
  LUHM_BETA_SIGNING_ALIAS
  LUHM_BETA_SIGNER_SHA256
)
env_names="$(gh secret list --repo "$REPO" --env "$ENV" --json name --jq '.[].name')" ||
  fail "cannot read protected environment secret NAMES"
repo_names="$(gh secret list --repo "$REPO" --json name --jq '.[].name')" ||
  fail "cannot read repository secret NAMES"
for name in "${required[@]}"; do
  grep -Fxq "$name" <<<"$env_names" || fail "missing protected environment secret: $name"
  if grep -Fxq "$name" <<<"$repo_names"; then
    fail "unprotected/redundant repository secret exists: $name; review and remove securely"
  fi
done
python3 - <<'PY'
import json
from pathlib import Path
p=Path("doctrine/androidBetaReleaseBaselineV1.json")
r=json.loads(p.read_text(encoding="utf-8"))
assert r.get("status") in ("VERIFIED_FIRST_BETA","VERIFIED_PREVIOUS_BETA"), "RED_UNVERIFIED_RELEASE_BASELINE"
assert isinstance(r.get("evidenceRef"),str) and len(r["evidenceRef"].strip())>=12, "RED_MISSING_BASELINE_PROOF"
print("GREEN_BASELINE_HAS_EVIDENCE_REFERENCE_NOT_INDEPENDENTLY_VERIFIED")
PY
printf '%s\n' "GREEN_SIGNING_CONFIGURATION_NAMES_AND_PROTECTION"
printf '%s\n' "NOTE: no key material, previous APK, build artifact, or Samsung device inspected"
