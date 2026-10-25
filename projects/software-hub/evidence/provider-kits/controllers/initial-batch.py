from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib,shutil,os,time
BASE=Path('/opt/tehnet-software/operations/provider-kits-20261019-v1')
SEED=Path('/opt/tehnet-software/operations/offline-devtools-20261018')
from tools.refresh_transport import save
from tools.offline_refresh import validate_acceptance
def now():return datetime.now(timezone.utc).isoformat()
profile=json.loads((BASE/'frozen-profile.json').read_text());profile_sha=hashlib.sha256((BASE/'frozen-profile.json').read_bytes()).hexdigest()
results={'started_at':now(),'profile_sha256':profile_sha,'status':'running','providers':[]};save(BASE/'results.json',results)
for provider in ['arvan','linuxmirrors','liara','hamravesh']:
    budget=json.loads((BASE/'batch-budget.json').read_text());amount=192*1024**2
    if budget['reserved']+amount>budget['limit'] or len(budget['attempts'])>=4:raise ValueError('Finite manual qualification budget exhausted')
    budget['reserved']+=amount;budget['attempts'].append({'provider':provider,'reserved_bytes':amount,'started_at':now()});save(BASE/'batch-budget.json',budget)
    ops=BASE/'runs'/provider;ops.mkdir(mode=0o700);meta=ops/'metadata';meta.mkdir()
    for name in ['app','tools','deployment']:(ops/name).symlink_to(BASE/name,target_is_directory=True)
    for name in ['SHA256SUMS','SHA256SUMS.gpg']:shutil.copyfile(SEED/'metadata'/name,meta/name)
    (meta/'profile-unaccepted.json').write_bytes((BASE/'frozen-profile.json').read_bytes())
    shutil.copyfile(BASE/'deployment/qualification/devtools-smoke.py',ops/'devtools-smoke.py')
    save(meta/'network-budget.json',{'limit':amount,'used':0,'requests':0})
    protected=json.loads(Path('/opt/tehnet-software/operations/offline-watch-state-20261019/config.json').read_text())['protected_hashes']
    protected['/etc/nginx/snippets/tehnet-software.conf']=hashlib.sha256(Path('/etc/nginx/snippets/tehnet-software.conf').read_bytes()).hexdigest()
    (ops/'protected.before').write_text(''.join(hashlib.sha256(Path(name).read_bytes()).hexdigest()+'  '+name+'\n' for name in protected))
    (ops/'containers.before').write_bytes(subprocess.check_output(['docker','ps','-a','--no-trunc','--format','{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}']))
    unit='tehnet-provider-kit-'+provider+'-20261019.service'
    text='''[Unit]
Description=TehNet selected-provider native offline qualification
After=network-online.target
[Service]
Type=oneshot
WorkingDirectory=BASE
Environment=PYTHONPATH=BASE:/opt/tehnet-software/releases/engine-active-20261018/host-site
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=OPS=OPS_VALUE
Environment=HOST_SITE=/opt/tehnet-software/releases/engine-active-20261018/host-site
Environment=PROVIDER_ID=PROVIDER_VALUE
Environment=LAB_STATE_READ=0
Environment=SOFTWARE_REFRESH_BUDGET_FILE=OPS_VALUE/metadata/network-budget.json
ExecStartPre=/usr/bin/unshare --mount --net /usr/bin/python3 BASE/deployment/qualification/check-refresh-uid.py
ExecStart=/usr/bin/unshare --mount --propagation private /usr/bin/python3 -m tools.provider_lab
TimeoutStartSec=900
TimeoutStopSec=30
KillMode=control-group
MemoryMax=900M
MemorySwapMax=0
CPUQuota=50%
TasksMax=96
OOMPolicy=stop
NoNewPrivileges=true
PrivateTmp=true
PrivateMounts=true
ProtectSystem=strict
ProtectHome=read-only
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX AF_NETLINK
ReadWritePaths=BASE/runs /run
InaccessiblePaths=/srv/tehnet-software
UMask=0077
StandardOutput=journal
StandardError=journal
'''.replace('BASE',str(BASE)).replace('OPS_VALUE',str(ops)).replace('PROVIDER_VALUE',provider)
    Path('/run/systemd/system',unit).write_text(text);subprocess.run(['systemctl','daemon-reload'],check=True)
    row={'provider':provider,'started_at':now(),'outcome':'running','profile_sha256':profile_sha};results['providers'].append(row);save(BASE/'results.json',results)
    process=subprocess.run(['systemctl','start',unit],capture_output=True,text=True)
    journal=subprocess.check_output(['journalctl','-u',unit,'--no-pager','-o','cat','-n','2200'],text=True);(meta/'qualification.log').write_text(journal)
    row.update({'finished_at':now(),'unit_start_exit':process.returncode,'network_budget':json.loads((meta/'network-budget.json').read_text())})
    try:
        if process.returncode:raise ValueError('Native laboratory unit failed; original qualification.log retained')
        proof=json.loads((meta/'offline-install-acceptance.json').read_text());lab=json.loads((meta/'lab-state.json').read_text())
        identity=validate_acceptance(profile,proof);assert identity==profile_sha
        assert lab['all_existing_container_fingerprints_preserved'] and lab['cgroup']['memory.swap.current']=='0' and 'noswap' in lab['tmpfs_options']
        downloads=json.loads((meta/'provider-downloads.json').read_text())['observations'];assert len(downloads)==6+len(profile['packages']) and all(d['complete_hash_verified'] for d in downloads)
        row.update({'outcome':'pass','complete_hash_verified_downloads':len(downloads),'packages':len(profile['packages']),'package_bytes':sum(p['size_bytes'] for p in profile['packages']),'functional_tools':proof['functional_tools'],'negative_checks':proof['negative_checks'],'install_evidence_sha256':hashlib.sha256((meta/'offline-install-acceptance.json').read_bytes()).hexdigest(),'qualified_profile_sha256':identity,'software_payload_disk_files':0})
    except (OSError,ValueError,KeyError,AssertionError) as error:row.update({'outcome':'failed','error':type(error).__name__+': '+str(error)[:300]})
    save(BASE/'results.json',results)
results.update({'status':'complete','finished_at':now()});save(BASE/'results.json',results)
