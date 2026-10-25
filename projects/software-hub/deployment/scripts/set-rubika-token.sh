#!/usr/bin/env bash
# Owner chooses the official bot token locally; never pass it as an argument.
set -Eeuo pipefail
umask 077
[[ $# == 0 && -t 0 && -t 1 && "$(id -u)" == 0 ]] || { echo 'Run without arguments in an interactive administrator SSH terminal.' >&2; exit 2; }
OPS=/opt/tehnet-software/operations/mirrors-20261018
BASE=/opt/tehnet-software/releases/engine-active-20261018
export PYTHONPATH="$BASE/host-site:$OPS" PYTHONDONTWRITEBYTECODE=1
cd "$OPS"
exec 9>/run/lock/tehnet-software-rubika.lock
flock -n 9 || { echo 'Another Rubika setup/probe is active.' >&2; exit 75; }
python3 -m tools.rubika_probe set-token
python3 -m tools.rubika_probe check
