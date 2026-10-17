#!/usr/bin/env bash
# Owner-operated hidden prompt; no password argument, environment variable or pipe.
set -Eeuo pipefail
umask 077
[[ $# == 1 && "$1" =~ ^sha256:[a-f0-9]{64}$ ]] || { echo 'Usage: set-password.sh sha256:<locally-tested-engine-image-id>' >&2; exit 2; }
[[ -t 0 && -t 1 ]] || { echo 'Run in an interactive SSH terminal; never pipe a password.' >&2; exit 2; }
[[ "$(id -u)" == 0 ]] || { echo 'Run as the server administrator.' >&2; exit 2; }
AUTH=/srv/tehnet-software/auth
[[ ! -L "$AUTH" && ! -L /srv/tehnet-software && ! -L /srv ]] || exit 2
docker image inspect "$1" >/dev/null
install -d -m 700 -o 10001 -g 10001 "$AUTH"
docker run --rm -it --network none --read-only --user 10001:10001 \
  --cap-drop ALL --security-opt no-new-privileges:true --memory 192m --cpus .5 --pids-limit 32 \
  --tmpfs /tmp:rw,nosuid,noexec,size=16m \
  -e TEHNET_SOFTWARE_AUTH=/auth -e TEHNET_SOFTWARE_RESTRICTED=0 \
  -v "$AUTH:/auth:rw" "$1" python -m app.cli set-password
echo 'Password configured; all old sessions invalidated. Engine deployment is a separate gate.'
