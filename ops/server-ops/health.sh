#!/usr/bin/env bash
set -uo pipefail
check_url() { code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 "https://tehnet.ir$1"); [ "$code" = "200" ] && echo ok || echo "fail:$code"; }
out="{\"generated_at\":\"$(date -u +%FT%TZ)\""
for route in "/" "/shop/" "/software/" "/b2b/" "/support/"; do
  name=$(echo "$route" | tr -d '/' | sed 's/^$/home/'); [ -z "$name" ] && name=home
  out="$out,\"route_${name}\":\"$(check_url "$route")\""
done
ntp=$(python3 -c "
import socket,struct,sys
try:
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.settimeout(3)
    s.sendto(b'\x1b'+47*b'\0',('127.0.0.1',123)); d,_=s.recvfrom(512)
    print('ok' if len(d)==48 else 'fail')
except Exception: print('fail')
")
out="$out,\"ntp\":\"$ntp\""
out="$out,\"redis\":\"$(docker inspect --format '{{.State.Running}}' tehnet-redis 2>/dev/null | grep -q true && echo ok || echo fail)\""
out="$out,\"wordpress\":\"$(docker inspect --format '{{.State.Running}}' tehnet-wordpress 2>/dev/null | grep -q true && echo ok || echo fail)\""
out="$out,\"disk_free_gb\":$(df --output=avail -BG / | tail -1 | tr -dc '0-9')"
latest=$(ls -dt /root/tehnet-backups/*-store-review 2>/dev/null | head -1)
out="$out,\"last_backup\":\"$latest\""
echo "$out}" > /opt/tehnet/ops/status.json; chmod o+r /opt/tehnet/ops/status.json
