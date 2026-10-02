#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

repoName="eggie-admin/LuHm-OS"
sourceRef="b25cfad18051ba2799b19e27f035487366b256c9"
releaseTag="android-web3-b25cfad1-r37000025238"
apkName="LuHmOS-AndroidWeb3-${releaseTag}-arm64-v8a.apk"
shaName="${apkName}.sha256"
expectedApkSha256="2a030cd15f6409464b9fc0fcd65f39f60635dcdabfdc298db3e25ae51ee4e3c8"
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
