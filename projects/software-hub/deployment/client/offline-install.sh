#!/usr/bin/env bash
# Run on the destination Ubuntu client, never the TehNet website host.
set -Eeuo pipefail
umask 022
export LC_ALL=C
[[ "$(id -u)" == 0 ]] || { echo 'Run with sudo on the destination client.' >&2; exit 2; }
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 && "$(dpkg --print-architecture)" == amd64 ]] || { echo 'This kit targets Ubuntu 24.04 amd64 only.' >&2; exit 2; }
KIT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
[[ "$KIT" != /srv/tehnet-software* && "$KIT" != /opt/tehnet* && "$KIT" != /var/www* ]] || exit 2
[[ -f "$KIT/packages.tsv" && -f "$KIT/seeds.txt" && -d "$KIT/repo/dists" && -d "$KIT/archives" ]]
STATE=$(mktemp -d /tmp/tehnet-offline-apt.XXXXXX)
cleanup(){ case "$STATE" in /tmp/tehnet-offline-apt.*) rm -rf -- "$STATE";; esac; }
trap cleanup EXIT
chmod 755 "$STATE"
mkdir -p "$STATE/lists/partial"
[[ "$KIT" != *$'\n'* && "$KIT" != *$'\t'* ]]
REPO_URI=${KIT//%/%25}; REPO_URI=${REPO_URI// /%20}; REPO_URI=${REPO_URI//#/%23}; REPO_URI=${REPO_URI//\?/%3F}
for suite in noble noble-updates noble-security; do
 printf 'deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] file:%s/repo %s main universe\n' "$REPO_URI" "$suite" >> "$STATE/sources.list"
done
OPTIONS=(-o "Dir::Etc::sourcelist=$STATE/sources.list" -o 'Dir::Etc::sourceparts=-'
 -o "Dir::State::lists=$STATE/lists" -o "Dir::Cache::archives=$KIT/archives"
 -o 'Acquire::Languages=none' -o 'Acquire::By-Hash=false'
 -o 'Acquire::AllowInsecureRepositories=false' -o 'Acquire::AllowDowngradeToInsecureRepositories=false'
 -o 'Acquire::Check-Date=true' -o 'Acquire::Check-Valid-Until=true'
 -o 'APT::Update::Error-Mode=any' -o 'Acquire::Retries=0')
printf 'Frozen Ubuntu package snapshot: '; cat "$KIT/snapshot.txt"
echo 'The kit proves the recorded versions, not future security freshness.'
# Only local files are configured. Native APT checks original Ubuntu signatures,
# dates and complete index hashes into an initially empty private list directory.
apt-get "${OPTIONS[@]}" update
count=0
declare -A exact_versions
all_targets=()
while IFS=$'\t' read -r package version architecture relative_path digest size cache_filename; do
 [[ "$package" =~ ^[a-z0-9][a-z0-9+.-]*$ && "$version" =~ ^[A-Za-z0-9.+:~_-]+$ ]]
 [[ "$architecture" == amd64 || "$architecture" == all ]]
 [[ "$cache_filename" =~ ^[A-Za-z0-9+_.%:~-]+\.deb$ && "$digest" =~ ^[a-f0-9]{64}$ && "$size" =~ ^[0-9]+$ ]]
 file="$KIT/archives/$cache_filename"
 [[ -f "$file" && ! -L "$file" ]]
 metadata=$(apt-cache "${OPTIONS[@]}" show "$package=$version")
 signed_hash=$(printf '%s\n' "$metadata" | awk '$1=="SHA256:"{print $2}' | sort -u)
 signed_size=$(printf '%s\n' "$metadata" | awk '$1=="Size:"{print $2}' | sort -u)
 [[ "$signed_hash" == "$digest" && "$signed_size" == "$size" && "$(stat -c %s "$file")" == "$size" ]] || { echo "Signed identity mismatch: $package" >&2; exit 1; }
 printf '%s  %s\n' "$signed_hash" "$file" | sha256sum --check --status
 installed=$(dpkg-query -W -f='${db:Status-Status}\t${Version}' "$package" 2>/dev/null || true)
 if [[ "$installed" == installed$'\t'* ]]; then
  current_version=${installed#*$'\t'}
  if dpkg --compare-versions "$current_version" gt "$version"; then echo "Refusing downgrade before any installation: $package $current_version > $version" >&2; exit 2; fi
 fi
 exact_versions["$package"]="$version"
 all_targets+=("$package=$version")
 count=$((count+1))
done < "$KIT/packages.tsv"
[[ "$count" -gt 0 && "$count" -le 200 ]]
mapfile -t seeds < "$KIT/seeds.txt"
[[ "${#seeds[@]}" == 9 ]]
for seed in "${seeds[@]}"; do [[ "$seed" =~ ^[a-z0-9][a-z0-9+.-]*=[A-Za-z0-9.+:~_-]+$ ]]; done
apt-get "${OPTIONS[@]}" --simulate --no-download --no-install-recommends install -- "${all_targets[@]}" > "$STATE/transaction.txt"
if grep -q '^Remv ' "$STATE/transaction.txt"; then echo 'Refusing a transaction that removes existing packages.' >&2; exit 2; fi
while IFS=$'\t' read -r package version; do
 package=${package%:amd64}
 [[ -n "${exact_versions[$package]:-}" && "${exact_versions[$package]}" == "$version" ]] || { echo "Unpinned transaction item: $package $version" >&2; exit 2; }
done < <(awk '$1=="Inst" {for(i=3;i<=NF;i++) if(substr($i,1,1)=="(") {print $2 "\t" substr($i,2);break}}' "$STATE/transaction.txt")
echo 'Every archive matches native authenticated APT metadata; installing with downloads prohibited.'
apt-get "${OPTIONS[@]}" --assume-yes --no-download --no-install-recommends install -- "${all_targets[@]}"
while IFS=$'\t' read -r package version architecture relative_path digest size cache_filename; do
 [[ "$(dpkg-query -W -f='${Version}' "$package")" == "$version" ]] || { echo "Installed version mismatch: $package" >&2; exit 1; }
done < "$KIT/packages.tsv"
audit=$(dpkg --audit)
[[ -z "$audit" ]] || { printf '%s\n' "$audit" >&2; exit 1; }
echo 'OFFLINE_INSTALL_PASS: exact package versions and dpkg audit verified.'
