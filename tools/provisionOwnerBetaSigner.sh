#!/usr/bin/env bash
# One-time, OWNER-ONLY beta signer bootstrap on a trusted Linux workstation.
# Creates NO credentials in GitHub source, logs, artifacts, or Google Drive.
# Keeps one durable private PKCS12 file outside the checkout for Android upgrades.
set -euo pipefail
umask 077
REPO="eggie-admin/LuHm-OS"
SIGNING_ENV="luhm-beta-signing"
ALIAS="luhmBetaRelease"
P12="${XDG_DATA_HOME:-$HOME/.local/share}/luhmOs/privateSigning/ownerBeta.p12"
required=(
  LUHM_BETA_SIGNING_P12_B64
  LUHM_BETA_SIGNING_PASSWORD
  LUHM_BETA_SIGNING_ALIAS
  LUHM_BETA_SIGNER_SHA256
)
die() { printf 'RED_OWNER_BETA_SIGNER: %s\n' "$*" >&2; exit 2; }
for tool in gh keytool base64 jq; do
  command -v "$tool" >/dev/null 2>&1 || die "Install $tool on the trusted owner workstation"
done
[[ -t 0 ]] || die "Interactive owner terminal required; no noninteractive key creation"
[[ "${EUID:-$(id -u)}" != 0 ]] || die "Do not provision signing keys as root"
gh auth status >/dev/null 2>&1 || die "Log in securely with gh auth login"
ACTOR="$(gh api user --jq .login)"
[[ "$ACTOR" == "eggie-admin" ]] || die "Must be authenticated as repository owner"
OWNER="$(gh api "repos/$REPO" --jq .owner.login)"
[[ "$OWNER" == "$ACTOR" ]] || die "GitHub repository owner mismatch"
env_info="$(gh api "repos/$REPO/environments/$SIGNING_ENV")" || die "Protected signing environment missing"
jq -e '.prevent_self_review == true and (.protection_rules | any(.type == "required_reviewers")) and (.deployment_branch_policy.protected_branches == true)' <<<"$env_info" >/dev/null ||
  die "Signing environment needs independent reviewer, no self-approval and protected branches"
[[ "$(gh api "repos/$REPO/branches/main" --jq '.protected')" == "true" ]] ||
  die "Protect main before creating/signing releases"
[[ ! -e "$P12" && ! -L "$P12" ]] || die "Durable signer already exists. Do NOT replace it: $P12"
existing="$(gh secret list --repo "$REPO" --env "$SIGNING_ENV" --json name --jq '.[].name')" || die "Cannot inspect secret names"
for key in "${required[@]}"; do
  if grep -Fxq "$key" <<<"$existing"; then
    die "$key already exists. Do NOT rotate an upgrade signer from this script."
  fi
done

printf '%s\n' \
  "OWNER-ONLY NEW SIGNER. Do not run if an older .beta APK is already installed" \
  "or if an older certificate must continue to sign upgrades." \
  "Key will be encrypted at: $P12" \
  "GitHub will receive encrypted environment-only Actions secrets, never the raw source file."
read -r -p "Type CREATE to make a new durable signer: " APPROVAL
[[ "$APPROVAL" == CREATE ]] || die "Signer creation not authorized"
read -r -s -p "New keystore passphrase (16+ characters, save in password manager): " LUHM_KEY_PASS
printf '\n'
[[ ${#LUHM_KEY_PASS} -ge 16 ]] || die "Passphrase must be at least 16 characters"
read -r -s -p "Repeat passphrase: " CONFIRM
printf '\n'
[[ "$LUHM_KEY_PASS" == "$CONFIRM" ]] || die "Passphrases did not match"
unset CONFIRM
export LUHM_KEY_PASS
trap 'unset LUHM_KEY_PASS' EXIT

mkdir -p "$(dirname "$P12")"
chmod 700 "$(dirname "$P12")"
keytool -genkeypair -noprompt -storetype PKCS12 \
  -keystore "$P12" -alias "$ALIAS" -storepass:env LUHM_KEY_PASS \
  -keyalg RSA -keysize 3072 -validity 9125 \
  -dname "CN=LuHm OS Owner Beta, O=Eggie Bagelface, C=US" \
  >/dev/null
[[ -s "$P12" && ! -L "$P12" ]] || die "Signer file missing or unsafe"
chmod 600 "$P12"
FINGERPRINT="$(keytool -list -v -storetype PKCS12 -keystore "$P12" \
  -alias "$ALIAS" -storepass:env LUHM_KEY_PASS \
  | sed -n 's/^[[:space:]]*SHA256: //p' | head -n 1 \
  | tr -d ':' | tr '[:upper:]' '[:lower:]')"
[[ "$FINGERPRINT" =~ ^[a-f0-9]{64}$ ]] || die "Cannot derive verified signing fingerprint"

printf '\nCertificate SHA256: %s\n' "$FINGERPRINT"
printf 'BACKUP REQUIRED: copy %s to offline encrypted storage.\n' "$P12"
printf '%s\n' "Save the passphrase separately in your password manager."
read -r -p "Type BACKED_UP after securing both, before uploading secrets: " BACKUP
[[ "$BACKUP" == BACKED_UP ]] || die "Private signer stays local; GitHub secrets not uploaded"
base64 -w0 "$P12" | gh secret set LUHM_BETA_SIGNING_P12_B64 --repo "$REPO" --env "$SIGNING_ENV"
printf '%s' "$LUHM_KEY_PASS" | gh secret set LUHM_BETA_SIGNING_PASSWORD --repo "$REPO" --env "$SIGNING_ENV"
printf '%s' "$ALIAS" | gh secret set LUHM_BETA_SIGNING_ALIAS --repo "$REPO" --env "$SIGNING_ENV"
printf '%s' "$FINGERPRINT" | gh secret set LUHM_BETA_SIGNER_SHA256 --repo "$REPO" --env "$SIGNING_ENV"
printf '\nOWNER_BETA_SIGNER_SECRETS_UPLOADED\n'
printf '%s\n' "No APK, F-Droid index, or tablet install has yet been proved."

SOURCE="$(gh api "repos/$REPO/branches/main" --jq .commit.sha)"
[[ "$SOURCE" =~ ^[a-f0-9]{40}$ ]] || die "Cannot resolve exact current main commit"
printf 'Exact source for private beta: %s\n' "$SOURCE"
read -r -p "Type CAST to dispatch the PRIVATE signed beta build now, or Enter to stop: " CAST
if [[ "$CAST" == CAST ]]; then
  gh workflow run samsung-lite-signed-beta.yml --repo "$REPO" --ref main \
    -f cast=cast -f sourceRef="$SOURCE"
  printf '%s\n' "Build dispatched. Check GitHub Actions for signed APK, SHA256, signer and private F-Droid stage receipts."
else
  printf '%s\n' "No build dispatched. Run the owner-signed workflow later with CAST and exact current main SHA."
fi
