#!/usr/bin/env bash
# LuHm OS owner-only GPG bootstrap. No private key is printed or exported.
set -euo pipefail
umask 077
if [[ "${1:-}" != "--configure" ]]; then
  cat <<'HELP'
LuHm OS owner GPG bootstrap. Run on YOUR trusted Linux workstation:
  bash tools/ownerGpgBootstrap.sh --configure
Requires gpg, git, gh; logged-in GitHub CLI with GPG key permissions.
No GitHub Actions runner or remote agent may run this bootstrap.
HELP
  exit 0
fi
if [[ ${EUID:-$(id -u)} -eq 0 || ! -t 0 ]]; then
  echo "ERROR: run interactively as your unprivileged owner user." >&2
  exit 2
fi
for cmd in gpg git gh awk grep; do
  command -v "$cmd" >/dev/null || { echo "ERROR: missing $cmd" >&2; exit 2; }
done
gh auth status >/dev/null 2>&1 || { echo "ERROR: run gh auth login first." >&2; exit 2; }
printf 'Authenticated GitHub account: '
gh api /user --jq '.login'
read -r -p 'Verified commit-signing name: ' signingName
read -r -p 'Verified GitHub commit-signing email: ' signingEmail
[[ -n "$signingName" && "$signingEmail" =~ ^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$ ]] ||
  { echo "ERROR: invalid signing name/email." >&2; exit 2; }
[[ "$signingName" != *'<'* && "$signingName" != *'>'* ]] ||
  { echo "ERROR: invalid signing name." >&2; exit 2; }
verifiedEmails="$(gh api /user/emails --jq '.[] | select(.verified == true) | .email' 2>/dev/null)" ||
  { echo "ERROR: unable to confirm verified GitHub email; refusing to guess." >&2; exit 2; }
grep -Fxqi -- "$signingEmail" <<< "$verifiedEmails" ||
  { echo "ERROR: email not verified on GitHub identity." >&2; exit 2; }
signerUid="$signingName <$signingEmail>"
fingerprint="$(gpg --list-secret-keys --with-colons --fingerprint "$signerUid" 2>/dev/null | awk -F: '$1=="fpr" {print $10; exit}' || true)"
if [[ -z "$fingerprint" ]]; then
  echo "Generating owner-held Ed25519 signing key (5-year expiry)."
  echo "Enter a LOCAL GPG passphrase in pinentry. Never paste it into chat."
  gpg --quick-generate-key "$signerUid" ed25519 sign 5y
  fingerprint="$(gpg --list-secret-keys --with-colons --fingerprint "$signerUid" | awk -F: '$1=="fpr" {print $10; exit}')"
fi
[[ "$fingerprint" =~ ^[A-Fa-f0-9]{40}$ ]] ||
  { echo "ERROR: invalid signing-key fingerprint." >&2; exit 2; }
pubDir="${XDG_DATA_HOME:-$HOME/.local/share}/luhm-security"
mkdir -p "$pubDir"
chmod 700 "$pubDir"
publicFile="$pubDir/owner-gpg-public.asc"
gpg --armor --export "$fingerprint" > "$publicFile"
chmod 600 "$publicFile"
[[ -s "$publicFile" ]] || { echo "ERROR: public key export failed." >&2; exit 2; }
keyId="${fingerprint: -16}"
registeredIds="$(gh api /user/gpg_keys --jq '.[].key_id' 2>/dev/null)" ||
  { echo "ERROR: cannot read GitHub public GPG keys; no git config changed." >&2; exit 2; }
if grep -Fxqi -- "$keyId" <<< "$registeredIds"; then
  echo "Public GPG key already registered in GitHub."
else
  gh api --method POST /user/gpg_keys -F "armored_public_key=@$publicFile" >/dev/null ||
    { echo "ERROR: GitHub declined public key; no git config changed." >&2; exit 2; }
fi
git config --global user.name "$signingName"
git config --global user.email "$signingEmail"
git config --global gpg.format openpgp
git config --global user.signingkey "$fingerprint"
git config --global commit.gpgsign true
git config --global tag.gpgsign true
echo "Running local signature self-test..."
printf 'luhm-owner-signing-self-test\n' | gpg --batch --local-user "$fingerprint" --armor --detach-sign --output /dev/null
echo "Owner Git signing configured."
echo "Public key file: $publicFile"
echo "GPG fingerprint: $fingerprint"
echo "Required: two encrypted owner-held OFFLINE recovery copies, including revocation certificate."
echo "Required: confirm a new signed Git commit shows Verified before requiring signed commits."
echo "No TLS or Android private keys were generated, moved or uploaded."
