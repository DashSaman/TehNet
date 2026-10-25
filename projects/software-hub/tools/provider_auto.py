"""One durable, bounded real provider qualification per accepted profile/source."""
from pathlib import Path
from datetime import datetime,timezone
from contextlib import contextmanager
import argparse,hashlib,json,os,re,shutil,subprocess
from tools.refresh_transport import save

ROOT=Path(__file__).resolve().parents[1]
PROVIDERS=('arvan','linuxmirrors','liara','hamravesh')
ATTEMPT_BYTES=192*1024**2
NEGATIVES=('corrupt_required_archive','missing_required_archive','forged_signed_metadata','newer_nonseed_dependency')

def now():return datetime.now(timezone.utc).isoformat()

def new_generation(digest):
    if not re.fullmatch('[a-f0-9]{64}',digest):raise ValueError('Exact profile SHA required')
    return {'format':1,'profile_sha256':digest,'created_at':now(),'providers':{p:{'provider':p,'outcome':'pending'} for p in PROVIDERS}}

def next_provider(state):
    return next((p for p in PROVIDERS if state['providers'][p]['outcome'] in {'pending','deferred','budget_deferred'}),None)

def recover_interrupted(state):
    for row in state['providers'].values():
        if row['outcome']=='running':row.update({'outcome':'interrupted','finished_at':now(),'error_category':'interrupted_no_replay'})

def reserve(path,at,digest,provider):
    if not re.fullmatch('[a-f0-9]{64}',digest) or provider not in PROVIDERS:raise ValueError('Fixed provider/profile required')
    path=Path(path);day=at.astimezone(timezone.utc).date().isoformat()
    state=json.loads(path.read_text()) if path.exists() else {'day':day,'attempts':0,'reserved_bytes':0,'intents':{},'days':{}}
    if state['day']>day:raise ValueError('Clock behind durable provider budget day')
    key=digest+':'+provider
    if key in state['intents']:raise ValueError('Provider/profile intent already charged; no replay')
    if state['day']!=day:
        state['days'][state['day']]={'attempts':state['attempts'],'reserved_bytes':state['reserved_bytes']}
        state.update({'day':day,'attempts':0,'reserved_bytes':0})
    if state['attempts']>=8 or state['reserved_bytes']+ATTEMPT_BYTES>8*ATTEMPT_BYTES:raise ValueError('Daily provider budget exhausted')
    state['attempts']+=1;state['reserved_bytes']+=ATTEMPT_BYTES
    state['intents'][key]={'reserved_at':at.isoformat(),'reserved_bytes':ATTEMPT_BYTES}
    save(path,state)

def receipt(state):
    fields={'provider','outcome','started_at','finished_at','accepted_at','qualified_profile_sha256','packages','package_bytes','functional_tools','negative_checks','install_evidence_sha256','complete_hash_verified_downloads','error_category'}
    return {'format':1,'automatic':True,'updated_at':now(),'profile_sha256':state['profile_sha256'],'providers':[{k:v for k,v in state['providers'][p].items() if k in fields} for p in PROVIDERS]}

def lab_unit(runtime,ops,provider,host_site):
    return (ROOT/'deployment/systemd/tehnet-software-provider-lab@.service').read_text().replace('@RUNTIME@',str(runtime)).replace('@HOST_SITE@',str(host_site))

@contextmanager
def lock(path):
    import fcntl
    with open(path,'a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield

def current():
    from tools.offline_refresh import current_public
    from tools.offline_kit import validate_profile
    with lock('/run/lock/tehnet-software-engine.lock'):
        public,profile,proof=current_public('/etc/nginx/snippets/tehnet-software.conf')
        if Path('/opt/tehnet-software/public/current').resolve()!=public.resolve():raise ValueError('Publication pointer not reconciled')
        raw=(public/'profile.json').read_bytes();digest=hashlib.sha256(raw).hexdigest()
        validate_profile(profile)
        if proof['profile_sha256']!=digest:raise ValueError('Canonical public acceptance mismatch')
        return digest,raw

def activate(state,path):
    # Pointer changes before canonical publication: any old receipt fails web/client
    # identity checks even between timer ticks. Never move the pointer here.
    with lock('/run/lock/tehnet-software-engine.lock'):
        raw=(Path('/opt/tehnet-software/public/current')/'profile.json').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=state['profile_sha256']:return False
        from tools.offline_publication import atomic
        atomic(path,(json.dumps(receipt(state),indent=2)+'\n').encode())
        return True

def qualify(ops,profile,digest,provider):
    from tools.offline_refresh import validate_acceptance
    meta=ops/'metadata';unit='tehnet-software-provider-lab@'+digest+'-'+provider+'.service'
    process=subprocess.run(['systemctl','start',unit],capture_output=True,text=True,timeout=1235)
    journal=subprocess.check_output(['journalctl','-u',unit,'--no-pager','-o','cat','-n','2200'],timeout=20)
    if len(journal)>2*1024**2:raise ValueError('Qualification journal cap')
    (meta/'qualification.log').write_bytes(journal)
    if process.returncode:raise ValueError('Native lab failed; original qualification.log retained')
    proof_raw=(meta/'offline-install-acceptance.json').read_bytes();proof=json.loads(proof_raw)
    lab=json.loads((meta/'lab-state.json').read_text());downloads=json.loads((meta/'provider-downloads.json').read_text())
    identity=validate_acceptance(profile,proof)
    if identity!=digest or downloads['provider']!=provider:raise ValueError('Foreign profile/provider proof')
    observations=downloads['observations']
    if len(observations)!=len(profile['packages'])+6 or not all(d['complete_hash_verified'] for d in observations):raise ValueError('Incomplete full-byte download evidence')
    if not lab['all_existing_container_fingerprints_preserved'] or not lab['nginx_and_selected_protected_files_preserved'] or lab['cgroup']['memory.swap.current']!='0' or 'noswap' not in lab['tmpfs_options'] or 'oom_kill 0' not in lab['cgroup']['memory.events']:raise ValueError('Isolation/preservation evidence failed')
    return {'outcome':'pass','accepted_at':now(),'qualified_profile_sha256':identity,'packages':len(profile['packages']),'package_bytes':sum(p['size_bytes'] for p in profile['packages']),'complete_hash_verified_downloads':len(observations),'functional_tools':proof['functional_tools'],'negative_checks':proof['negative_checks'],'install_evidence_sha256':hashlib.sha256(proof_raw).hexdigest()}

def protected_snapshot(seed,snippet):
    protected={}
    for line in (Path(seed)/'protected.before').read_text().splitlines():
        _,name=line.split('  ',1)
        if not name.startswith('/srv/'):protected[name]=hashlib.sha256(Path(name).read_bytes()).hexdigest()
    protected[str(snippet)]=hashlib.sha256(Path(snippet).read_bytes()).hexdigest()
    return protected

def prepare(ops,raw,provider,seed,host_site):
    ops.mkdir(mode=0o700);meta=ops/'metadata';meta.mkdir()
    for name in ['app','tools','deployment']:(ops/name).symlink_to(ROOT/name,target_is_directory=True)
    for name in ['SHA256SUMS','SHA256SUMS.gpg']:shutil.copyfile(seed/'metadata'/name,meta/name)
    (meta/'profile-unaccepted.json').write_bytes(raw)
    shutil.copyfile(ROOT/'deployment/qualification/devtools-smoke.py',ops/'devtools-smoke.py')
    save(meta/'network-budget.json',{'limit':ATTEMPT_BYTES,'used':0,'requests':0})
    protected=protected_snapshot(seed,Path('/etc/nginx/snippets/tehnet-software.conf'))
    (ops/'protected.before').write_text(''.join(h+'  '+n+'\n' for n,h in protected.items()))
    (ops/'containers.before').write_bytes(subprocess.check_output(['docker','ps','-a','--no-trunc','--format','{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}']))
    (ops/'lab.env').write_text('PROVIDER_ID='+provider+'\nSOFTWARE_REFRESH_BUDGET_FILE='+str(meta/'network-budget.json')+'\n')

def run(state_root,public_receipts,seed,host_site):
    state_root=Path(state_root);state_root.mkdir(mode=0o700,parents=True,exist_ok=True);(state_root/'runs').mkdir(exist_ok=True)
    with lock('/run/lock/tehnet-software-provider-auto.lock'):
        digest,raw=current();profile=json.loads(raw)
        path=state_root/(digest+'.json');state=json.loads(path.read_text()) if path.exists() else new_generation(digest)
        recover_interrupted(state);save(path,state)
        if not activate(state,public_receipts):return {'stage':'superseded','profile_sha256':digest}
        for provider in PROVIDERS:
            if state['providers'][provider]['outcome'] not in {'pending','deferred','budget_deferred'}:continue
            if current()[0]!=digest:return {'stage':'superseded','profile_sha256':digest}
            active=subprocess.check_output(['systemctl','list-units','--all','--state=active,activating','--plain','--no-legend','tehnet-software-provider-lab@*.service'],text=True,timeout=15)
            if active.strip():return {'stage':'previous_lab_deferred','profile_sha256':digest}
            try:
                with lock('/run/lock/tehnet-software-offline-refresh.lock'):
                    available=int(re.search(r'MemAvailable:\s+(\d+)',Path('/proc/meminfo').read_text())[1])*1024
                    if available<1200*1024**2:return {'stage':'resource_deferred','profile_sha256':digest}
                    try:reserve(state_root/'daily-budget.json',datetime.now(timezone.utc),digest,provider)
                    except ValueError as error:
                        if 'already charged' in str(error):
                            state['providers'][provider].update({'outcome':'interrupted','finished_at':now(),'error_category':'charged_intent_no_replay'});save(path,state);activate(state,public_receipts);continue
                        return {'stage':'budget_deferred','profile_sha256':digest,'reason':str(error)}
                    row={'provider':provider,'outcome':'running','started_at':now()};state['providers'][provider]=row;save(path,state);activate(state,public_receipts)
                    ops=state_root/'runs'/(digest+'-'+provider)
                    try:
                        prepare(ops,raw,provider,Path(seed),host_site)
                    except (OSError,ValueError,KeyError,subprocess.SubprocessError) as error:
                        row.update({'outcome':'failed','error_category':'native_qualification_failed','error':type(error).__name__+': '+str(error)[:2000]})
                # The independently managed child owns this lock during all I/O,
                # including if this dispatcher dies. A startup conflict consumes
                # its already durable reservation and cannot qualify a source.
                if row['outcome']=='running':
                    try:row.update(qualify(ops,profile,digest,provider))
                    except (OSError,ValueError,KeyError,subprocess.SubprocessError) as error:
                        row.update({'outcome':'failed','error_category':'native_qualification_failed','error':type(error).__name__+': '+str(error)[:2000]})
                row['finished_at']=now();save(path,state)
                if not activate(state,public_receipts):return {'stage':'superseded','profile_sha256':digest}
            except BlockingIOError:return {'stage':'producer_deferred','profile_sha256':digest}
        return {'stage':'complete','profile_sha256':digest,'providers':{p:r['outcome'] for p,r in state['providers'].items()}}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',type=Path,required=True);parser.add_argument('--receipts',type=Path,required=True)
    parser.add_argument('--seed',type=Path,required=True);parser.add_argument('--host-site',type=Path,required=True);args=parser.parse_args()
    try:result=run(args.state,args.receipts,args.seed,args.host_site)
    except BlockingIOError:raise SystemExit(75)
    except Exception as error:
        if args.state.is_dir():save(args.state/'latest.json',{'stage':'preflight_failed','checked_at':now(),'error':type(error).__name__+': '+str(error)[:2000]})
        raise
    save(args.state/'latest.json',{**result,'checked_at':now()});print(json.dumps(result))

if __name__=='__main__':main()
