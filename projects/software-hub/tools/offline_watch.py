"""Finite read-only observation of the accepted offline refresh operation."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile,uuid
from tools.refresh_transport import save

ROOT=Path(__file__).resolve().parents[1]
PRODUCER=Path('/opt/tehnet-software/operations/offline-refresh-20261018')
REFRESH_STATE=PRODUCER.with_name('offline-refresh-state')
SEED=PRODUCER.with_name('offline-devtools-20261018')
WATCH_TIMER='tehnet-software-offline-watch.timer'

def stamp(value):return datetime.fromisoformat(value)

def assess_operation(state,now,active):
    reasons=[];accepted=stamp(state['accepted_at']);checked=stamp(state['checked_at'])
    if state.get('failed_at') and stamp(state['failed_at'])>accepted:reasons.append('unresolved_refresh_failure')
    if now-checked>timedelta(hours=7):reasons.append('scheduled_check_overdue')
    if now-accepted>timedelta(hours=20):reasons.append('accepted_publication_overdue')
    running=state.get('stage') in {'signed_discovery','candidate_signature_chain','clean_offline_install','qualified','publishing'}
    if running and (not active or now-checked>timedelta(minutes=25)):reasons.append('stalled_refresh_stage')
    if accepted>now+timedelta(minutes=5) or checked>now+timedelta(minutes=5):reasons.append('future_operation_time')
    return reasons

def assess_window(start,samples,now):
    if now<start:raise ValueError('Server clock moved behind monitor start')
    end=start+timedelta(hours=48);times=[stamp(x['checked_at']) for x in samples]
    if any(t<start or t>now for t in times) or times!=sorted(times):raise ValueError('Server clock/sample order changed')
    observed=[stamp(x['checked_at']) for x in samples if x['outcome']!='deferred']
    capped=[start]+[min(t,end) for t in observed]+[min(now,end)]
    gaps=[(b-a).total_seconds() for a,b in zip(capped,capped[1:])]
    publications={x['profile_sha256'] for x in samples if x.get('profile_sha256') and x.get('accepted_at') and start<stamp(x['accepted_at'])<=min(stamp(x['checked_at']),end) and x['outcome']=='healthy'}
    failed=sum(x['outcome']=='error' for x in samples);limitations=[]
    if max(gaps,default=0)>4500:limitations.append('observation_gap')
    if not publications:limitations.append('no_new_publication')
    if not samples or samples[-1]['outcome']!='healthy':limitations.append('last_sample_not_healthy')
    phase='observing'
    if now>=end:phase='completed_incomplete' if limitations else ('completed_with_incidents' if failed else 'completed_pass')
    return {'phase':phase,'started_at':start.isoformat(),'deadline':end.isoformat(),'elapsed_hours':round((now-start).total_seconds()/3600,4),
            'samples':len(samples),'failed_samples':failed,'new_publications':len(publications),'maximum_observation_gap_seconds':max(gaps,default=0),'limitations':limitations}

def command(*args,timeout=15):
    result=subprocess.run(args,capture_output=True,timeout=timeout)
    if len(result.stdout)+len(result.stderr)>2*1024**2:raise ValueError('Observation command output cap')
    if result.returncode:raise ValueError('Observation command failed: '+args[0]+'; see private service journal')
    return result.stdout

def properties(unit):
    raw=command('systemctl','show',unit,'-p','ActiveState','-p','UnitFileState','-p','Result','-p','ExecMainStatus','-p','Persistent','-p','LastTriggerUSec','-p','NextElapseUSecRealtime').decode()
    return dict(line.split('=',1) for line in raw.splitlines() if '=' in line)

def initialize(state,manifest,now):
    path=state/'config.json'
    if path.exists():raise FileExistsError('Monitor already initialized; original deadline preserved')
    source=json.loads(Path(manifest).read_text());protected={}
    for line in (SEED/'protected.before').read_text().splitlines():
        digest,name=line.split('  ',1)
        if not name.startswith('/srv/') and name!='/etc/nginx/snippets/tehnet-software.conf':protected[name]=digest
    config={'started_at':now.isoformat(),'deadline':(now+timedelta(hours=48)).isoformat(),'runtime_hashes':source['code_files_sha256'],
            'protected_hashes':protected,'containers':sorted((SEED/'containers.before').read_text().splitlines()),'active_image':'sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa'}
    save(path,config);return config

def capture_events(state,start):
    raw=command('journalctl','-u','tehnet-software-offline-refresh.service','--since',start.isoformat(),'--no-pager','-n','512','-o','json','--output-fields=__REALTIME_TIMESTAMP,MESSAGE',timeout=10)
    events=[]
    for line in raw.splitlines():
        entry=json.loads(line);message=entry.get('MESSAGE','')
        try:data=json.loads(message)
        except (ValueError,TypeError):continue
        if not isinstance(data,dict):continue
        item={k:data[k] for k in ['stage','run','profile_sha256','accepted_at','checked_at'] if k in data}
        item['journal_utc']=datetime.fromtimestamp(int(entry['__REALTIME_TIMESTAMP'])/1000000,timezone.utc).isoformat()
        events.append(item)
    save(state/'scheduled-events.json',{'events':events,'source':'native refresh service journal; host/credentials omitted','query_limit_lines':512})

def check_publication(state):
    from tools.offline_refresh import current_public,validate_acceptance
    from tools.offline_publication import FILES
    from tools.offline_kit import verified_release
    public,profile,proof=current_public('/etc/nginx/snippets/tehnet-software.conf')
    run=REFRESH_STATE/('run-'+public.name.removeprefix('auto-'));metadata=run/'metadata'
    candidate=json.loads((metadata/'profile-unaccepted.json').read_text());installed=json.loads((metadata/'offline-install-acceptance.json').read_text())
    identity=validate_acceptance(candidate,installed)
    if identity!=proof['qualified_candidate_sha256'] or profile!={**candidate,'accepted':True,'acceptance_scope':proof['scope']}:raise ValueError('Published candidate differs from exact installed evidence')
    lab=json.loads((metadata/'lab-state.json').read_text())
    if lab['cgroup']['memory.swap.current']!='0' or 'noswap' not in lab['tmpfs_options'] or not lab['all_existing_container_fingerprints_preserved']:raise ValueError('Acceptance isolation evidence failed')
    with tempfile.TemporaryDirectory(prefix='tehnet-watch-signatures-',dir='/run') as temp:
        for release in profile['releases']:
            signed=Path(temp)/(release['suite']+'.InRelease');signed.write_text(release['inrelease'])
            checked=verified_release(signed,Path('/usr/share/keyrings/ubuntu-archive-keyring.gpg'))
            if checked['inrelease_sha256']!=release['inrelease_sha256']:raise ValueError('Original signed release hash changed')
    for name in FILES:
        url='https://tehnet.ir/software/offline/'+('' if name=='index.html' else name)
        actual=command('curl','--silent','--show-error','--fail','--noproxy','*','--resolve','tehnet.ir:443:127.0.0.1','--max-time','4','--max-filesize','2097152',url,timeout=6)
        if actual!=(public/name).read_bytes():raise ValueError('Origin bytes mismatch: '+name)
    command(sys.executable,str(ROOT/'tools/verify_live.py'),'--origin','--expect-downloads','--allow-configured-access',timeout=40)
    digest=proof['profile_sha256'];archive=state/'publications'/digest
    if not archive.exists():
        archive.mkdir(parents=True,mode=0o700)
        for name in ['profile.json','acceptance.json']:shutil.copyfile(public/name,archive/name)
        for name in ['offline-install-acceptance.json','lab-state.json','fresh-signed-metadata.json','network-budget.json','publication.json']:
            path=metadata/name
            if not path.is_file() or path.stat().st_size>2*1024**2:raise ValueError('Accepted metadata file cap')
            shutil.copyfile(path,archive/name)
    return {'profile_sha256':digest,'accepted_at':proof['tested_at_utc'],'packages':len(profile['packages']),
            'signature_and_exact_install_binding':True,'main_private_origin_checks':True,'swap_bytes':0,'accepted_run':run.name}

def collect(state,config,now):
    import fcntl
    sample={'checked_at':now.isoformat(),'outcome':'healthy','errors':[]}
    with open('/run/lock/tehnet-software-engine.lock','a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return {**sample,'outcome':'deferred','reason':'existing worker/publication lock held'}
        try:
            timer=properties('tehnet-software-offline-refresh.timer');service=properties('tehnet-software-offline-refresh.service')
            status=json.loads((REFRESH_STATE/'status.json').read_text());sample.update({'refresh_timer':timer,'refresh_service':service,'refresh_stage':status['stage']})
            if timer.get('ActiveState')!='active' or timer.get('UnitFileState')!='enabled' or timer.get('Persistent')!='yes':raise ValueError('Persistent refresh timer is not enabled/active')
            if service.get('Result') not in {'success',''}:sample['errors'].append('refresh_unit_failure')
            sample['errors']+=assess_operation(status,now,service.get('ActiveState') in {'active','activating','deactivating'})
            sample.update(check_publication(state))
            for name,digest in config['runtime_hashes'].items():
                if hashlib.sha256((PRODUCER/name).read_bytes()).hexdigest()!=digest:raise ValueError('Producer immutable source changed')
            for name,digest in config['protected_hashes'].items():
                if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:raise ValueError('Protected site/research configuration changed')
            containers=sorted(command('docker','ps','-a','--no-trunc','--format','{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}').decode().splitlines())
            if containers!=config['containers']:raise ValueError('Existing container fingerprints changed')
            runtime=command('docker','inspect','-f','{{.Image}}|{{.State.Health.Status}}|{{.HostConfig.ReadonlyRootfs}}','tehnet-software').decode().strip()
            if runtime!=config['active_image']+'|healthy|true':raise ValueError('Existing web engine health/image changed')
            for root in [Path('/opt/tehnet-software')]:
                count=0
                for path in root.rglob('*'):
                    count+=1
                    if count>50000:raise ValueError('Software tree scan cap')
                    if path.is_file() and (path.suffix in {'.deb','.apk','.iso','.xz'} or path.name.startswith(('ubuntu-base-','alpine-minirootfs-'))):raise ValueError('Catalog payload found on website disk')
            sample.update({'producer_hashes_preserved':True,'site_research_containers_preserved':True,'catalog_payload_files_in_scanned_opt_tree':0,'private_engine_state':'inaccessible; not read','preexisting_app_wheels':'preserved as application build code; not catalog payloads'})
        except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as error:
            sample['errors'].append(type(error).__name__+': '+str(error)[:300])
        if sample['errors']:sample['outcome']='error'
    return sample

def main():
    import fcntl
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--state',type=Path,required=True);parser.add_argument('--initialize',type=Path,metavar='TESTED_SOURCE_MANIFEST');args=parser.parse_args()
    state=args.state;state.mkdir(mode=0o700,parents=True,exist_ok=True)
    with open('/run/lock/tehnet-software-offline-watch.lock','a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise SystemExit(75)
        now=datetime.now(timezone.utc)
        if args.initialize:initialize(state,args.initialize,now)
        config=json.loads((state/'config.json').read_text());start=stamp(config['started_at'])
        if (state/'completed.json').exists():print((state/'completed.json').read_text());return
        files=sorted(state.glob('sample-*.json'))
        if len(files)>=128:raise ValueError('Finite monitor sample cap reached; deadline must not be reset')
        samples=[json.loads(path.read_text()) for path in files]
        assess_window(start,samples,now) # Reject backwards time before collecting.
        sample=collect(state,config,now)
        try:capture_events(state,start)
        except (OSError,ValueError,subprocess.TimeoutExpired) as error:sample['errors'].append('journal_capture: '+type(error).__name__);sample['outcome']='error'
        save(state/('sample-'+now.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json'),sample)
        summary=assess_window(start,samples+[sample],now);latest={**summary,'latest':sample}
        save(state/'latest.json',latest)
        if summary['phase'].startswith('completed_'):
            save(state/'completed.json',latest)
            command('systemctl','stop',WATCH_TIMER)
        print(json.dumps(latest))
        if sample['outcome']=='error' or summary['phase']=='completed_incomplete':raise SystemExit(1)

if __name__=='__main__':main()
