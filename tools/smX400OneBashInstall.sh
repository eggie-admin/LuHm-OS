#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

repoName="eggie-admin/LuHm-OS"
sourceRef="569e535ec3dbb17c6ba407ce23b0b216b816f883"
releaseTag="android-web3-569e535e-r37002117063"
apkName="LuHmOS-AndroidWeb3-${releaseTag}-arm64-v8a.apk"
shaName="${apkName}.sha256"
expectedApkSha256="368efd3c41fa92a55ff7cedbeeb48424a973eaec10104931615f02ba7f4cec2c"
workDir="${TMPDIR:-$HOME/.cache}/luhm-one-bash-install"
installerPath="${workDir}/termuxVirginInstall.sh"

die() {
  printf 'luhmOneBashInstall=red\nreason=%s\n' "$*" >&2
  exit 2
}

command -v curl >/dev/null || die "curl missing"
command -v bash >/dev/null || die "bash missing"

mkdir -p "$workDir"
rm -f "$workDir/$shaName" "$installerPath"

baseUrl="https://github.com/$repoName/releases/download/$releaseTag"
rawUrl="https://raw.githubusercontent.com/$repoName/$sourceRef/tools/termuxVirginInstall.sh"

printf 'luhmOneBashInstall=starting\n'
printf 'sourceRef=%s\n' "$sourceRef"
printf 'releaseTag=%s\n' "$releaseTag"

curl -fL --retry 4 --retry-all-errors -o "$workDir/$shaName" "$baseUrl/$shaName" \
  || die "could not fetch pinned release checksum"

releaseSha="$(awk 'NR==1 {print $1}' "$workDir/$shaName")"
[ "$releaseSha" = "$expectedApkSha256" ] \
  || die "pinned release checksum drift: expected $expectedApkSha256 got $releaseSha"

curl -fL --retry 4 --retry-all-errors -o "$installerPath" "$rawUrl" \
  || die "could not fetch exact-source virgin installer"
chmod 0700 "$installerPath"

printf 'luhmOneBashInstall=verifiedHandoff\n'
exec bash "$installerPath" "$releaseTag" "$apkName" "$shaName"
