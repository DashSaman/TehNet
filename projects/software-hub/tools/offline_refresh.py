"""Signed clean-install-gated server refresh. No catalog payload on disk."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,hashlib,html,json,os,re,shutil,signal,subprocess,time,uuid
from contextlib import contextmanager
from tools.refresh_transport import save
from tools.offline_kit import validate_profile,parse_release

ROOT=Path(__file__).resolve().parents[1]
ATTEMPT_BYTES=192*1024**2

@contextmanager
def refresh_lock():
    import fcntl
    with open('/run/lock/tehnet-software-offline-refresh.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield
def canonical(data):return (json.dumps(data,indent=2)+'\n').encode()
def should_refresh(state,now):
    stamp=state.get('accepted_at')
    return stamp is None or now-datetime.fromisoformat(stamp)>=timedelta(hours=12)
def reserve_attempt(path,now):
    path=Path(path);state=json.loads(path.read_text()) if path.exists() else {}
    if state.get('day','')>now.date().isoformat():raise ValueError('Server clock moved behind durable budget day')
    if state.get('day')!=now.date().isoformat():state={'day':now.date().isoformat(),'attempts':0,'reserved_bytes':0}
    if state['attempts']>=2 or state['reserved_bytes']+ATTEMPT_BYTES>2*ATTEMPT_BYTES:raise ValueError('Daily automatic refresh budget exhausted')
    state['attempts']+=1;state['reserved_bytes']+=ATTEMPT_BYTES;save(path,state)

def raw_save(path,data):
    path=Path(path);temporary=path.with_suffix('.tmp')
    with temporary.open('wb') as out:out.write(data);out.flush();os.fsync(out.fileno())
    os.replace(temporary,path)
    if os.name=='posix':
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(directory)
        finally:os.close(directory)

def reconcile_pending(status,snippet,*,check,reload):
    if not status.get('pending'):return status
    pending=status['pending'];snippet=Path(snippet);old=Path(pending['before_file']).read_bytes()
    if hashlib.sha256(old).hexdigest()!=pending['old_sha256']:raise ValueError('Pending rollback evidence changed')
    digest=hashlib.sha256(snippet.read_bytes()).hexdigest()
    if digest not in {pending['old_sha256'],pending['new_sha256']}:raise ValueError('Unexpected concurrent snippet; recovery refused')
    if digest==pending['old_sha256']:
        reload()
        if pending.get('previous_public'):check(pending['previous_public'])
        return {**status,'stage':'recovered_previous_publication','pending':None}
    try:
        reload();check(pending['public'])
    except BaseException as failure:
        raw_save(snippet,old);reload()
        if pending.get('previous_public'):check(pending['previous_public'])
        raise ValueError('Incomplete publication failed live checks; previous snippet restored') from failure
    return {**status,'stage':'recovered_publication','pending':None}

RUN_NAME=re.compile(r'run-\d{8}-\d{6}-[a-f0-9]{8}')
def prune_runs(root,protected,limit=12):
    root=Path(root).resolve();runs=[]
    for path in root.iterdir():
        if not RUN_NAME.fullmatch(path.name) or path.is_symlink() or not path.is_dir() or not (path/'auto-owned.json').is_file():continue
        if json.loads((path/'auto-owned.json').read_text()).get('owner')=='tehnet-offline-refresh':runs.append(path)
    protected={protected} if isinstance(protected,str) else set(protected or [])
    keep=protected.intersection(p.name for p in runs)
    keep.update(p.name for p in sorted(runs,reverse=True) if p.name not in keep and len(keep)<limit)
    for path in runs:
        if path.name in keep:continue
        if path.resolve().parent!=root:raise ValueError('Retention path escaped owned state')
        shutil.rmtree(path)

def prune_public_and_backups(active,public_root=Path('/opt/tehnet-software/public'),backup_root=Path('/root/tehnet-backups')):
    from tools.offline_publication import validate_source
    public_root,backup_root=Path(public_root).resolve(),Path(backup_root).resolve()
    backups=sorted([p for p in backup_root.iterdir() if re.fullmatch(r'\d{8}-\d{6}-[a-f0-9]{8}-offline-auto',p.name) and p.is_dir() and not p.is_symlink()],reverse=True)
    protected={Path(active).resolve()}
    for path in backups:
        if {p.name for p in path.iterdir()}!={'nginx-software.before','public-sha256.json'}:continue
        if path in backups[:3]:
            before=(path/'nginx-software.before').read_bytes();match=re.search(rb'root (/opt/tehnet-software/public/[a-zA-Z0-9_-]+);',before)
            if match:protected.add(Path(match[1].decode()).resolve())
        else:
            if path.resolve().parent!=backup_root:raise ValueError('Backup retention escape')
            shutil.rmtree(path)
    releases=sorted([p for p in public_root.iterdir() if re.fullmatch(r'auto-\d{8}-\d{6}-[a-f0-9]{8}',p.name) and p.is_dir() and not p.is_symlink()],reverse=True)
    protected.update(releases[:3])
    for path in releases:
        if path.resolve() in protected:continue
        validate_source(path)
        if path.resolve().parent!=public_root:raise ValueError('Public retention escape')
        shutil.rmtree(path)

def validate_acceptance(profile,evidence):
    validate_profile(profile,require_accepted=False)
    expected=hashlib.sha256(canonical(profile)).hexdigest()
    checks=evidence.get('negative_checks',{})
    negatives={'corrupt_required_archive','missing_required_archive','forged_signed_metadata','newer_nonseed_dependency'}
    if (evidence.get('qualified_profile_sha256')!=expected or evidence.get('installed_packages')!=len(profile['packages']) or
        set(evidence.get('functional_tools',[]))!={'git','curl','jq','python','pip','wget','rsync','ssh'} or not evidence.get('external_connect_refused') or
        evidence.get('offline_lists_before')!=0 or len(evidence.get('copyrights',[]))!=len(profile['packages']) or
        any(not checks.get(name,{}).get('dpkg_unchanged') or checks[name].get('exit',0)==0 for name in negatives) or
        checks.get('clean_offline_install',{}).get('exit')!=0 or checks['clean_offline_install'].get('dpkg_audit')!='empty'):
        raise ValueError('Missing or foreign clean-install acceptance proof')
    return expected

def render_guide(profile):
    template=(ROOT/'deployment/public-offline/index.html').read_text(encoding='utf-8')
    count=len(profile['packages']);digits=str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹');persian=str(count).translate(digits)
    template=template.replace('۱۸ اکتبر ۲۰۲۶',html.escape(profile['generated_at_utc'][:10])).replace('۵۸',persian)
    template=template.replace('حدود ۳۲ مگابایت نرم‌افزار',str(sum(p['size_bytes'] for p in profile['packages']))+' bytes نرم‌افزار')
    template=template.replace('نیاز به آزمون و انتشار تازه دارد','به‌روزرسانی خودکار فقط پس از امضا و نصب آزمایشی موفق منتشر می‌شود؛ در اختلال منبع، دریافت قدیمی متوقف می‌ماند')
    start=template.index('<details class="guide"><summary><strong>فهرست ')
    end=template.index('</details>',start)+len('</details>')
    package_list='<details class="guide"><summary><strong>فهرست '+persian+' بسته و وابستگی</strong><span>نسخه‌ها و منبع مستقیم +</span></summary><ul dir="ltr">'
    package_list+=''.join('<li><a href="https://mirror.arvancloud.ir/ubuntu/'+html.escape(p['relative_path'],quote=True)+'" rel="noopener noreferrer">'+html.escape(p['package'])+'</a> · '+html.escape(p['version'])+'</li>' for p in profile['packages'])+'</ul></details>'
    template=template[:start]+package_list+template[end:]
    template=template.replace('پروفایل تاریخ‌دار','پروفایل با به‌روزرسانی خودکار ·')
    return template

def stage_command(args,log,env):
    """Bound complete diagnostics without writing unbounded child stdout."""
    import threading
    process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,start_new_session=True)
    def kill():
        try:os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    timer=threading.Timer(600,kill);timer.daemon=True;timer.start();size=0
    try:
        with Path(log).open('wb') as out:
            while True:
                data=process.stdout.read1(16384)
                if not data:break
                size+=len(data)
                if size>2*1024**2:kill();raise ValueError('Stage log cap exceeded')
                out.write(data)
        if process.wait()!=0:raise ValueError('Stage failed: '+Path(log).name+'\n'+Path(log).read_text(errors='replace')[-4000:])
    finally:
        timer.cancel()
        if process.poll() is None:kill();process.wait()
        process.stdout.close()

def current_public(snippet):
    from tools.offline_publication import BASE,routes,validate_source
    raw=Path(snippet).read_bytes();match=re.search(rb'root (/opt/tehnet-software/public/[a-zA-Z0-9_-]+);',raw)
    if not match:raise ValueError('Existing exact guide root missing')
    public=Path(match[1].decode())
    if raw!=BASE.read_bytes().replace(b'\r\n',b'\n')+routes(public).encode():raise ValueError('Unexpected owned proxy snippet')
    validate_source(public)
    return public,json.loads((public/'profile.json').read_text()),json.loads((public/'acceptance.json').read_text())

def live_check(public):
    from tools.offline_publication import FILES
    for name in FILES:
        url='https://tehnet.ir/software/offline/'+('' if name=='index.html' else name)
        for attempt in range(20):
            actual=subprocess.run(['curl','--silent','--show-error','--noproxy','*','--resolve','tehnet.ir:443:127.0.0.1','--max-time','10',url],capture_output=True)
            if actual.returncode==0 and actual.stdout==(Path(public)/name).read_bytes():break
            time.sleep(.25)
        else:raise ValueError('Published origin bytes mismatch: '+name)
    result=subprocess.run(['python3',str(ROOT/'tools/verify_live.py'),'--origin','--expect-downloads','--allow-configured-access'],capture_output=True,text=True,timeout=90)
    if result.returncode:raise ValueError('Main/private acceptance failed: '+result.stdout+result.stderr)

def run(state_root,seed,host_site,*,force=False,dry_run=False):
    import fcntl
    from tools.offline_publication import publish
    state_root,seed=Path(state_root),Path(seed)
    state_root.mkdir(mode=0o700,parents=True,exist_ok=True)
    snippet=Path('/etc/nginx/snippets/tehnet-software.conf')
    with refresh_lock(),open('/run/lock/tehnet-software-engine.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        status_path=state_root/'status.json';status=json.loads(status_path.read_text()) if status_path.exists() else {}
        from tools.offline_publication import command,BASE,routes
        def reload():command('nginx','-t');command('systemctl','reload','nginx')
        try:status=reconcile_pending(status,snippet,check=live_check,reload=reload)
        except BaseException as failure:
            status.update({'stage':'recovery_failed','result':str(failure)[:5000]});save(status_path,status);raise
        now=datetime.now(timezone.utc);public,previous,previous_proof=current_public(snippet)
        initial_snippet=snippet.read_bytes()
        protected_runs={status.get('run'),'run-'+public.name.removeprefix('auto-')}
        prune_runs(state_root,protected_runs);prune_public_and_backups(public)
        # The pending transaction is reconciled against actual origin bytes first.
        status['accepted_at']=previous_proof['tested_at_utc']
        if not force and not should_refresh(status,now):
            status.update({'checked_at':now.isoformat(),'stage':'not_due','result':'previous accepted release retained'});save(status_path,status);return status
        available=int(re.search(r'MemAvailable:\s+(\d+)',Path('/proc/meminfo').read_text())[1])*1024
        if available<1200*1024**2:raise ValueError('Insufficient available RAM for bounded lab')
        reserve_attempt(state_root/'daily-budget.json',now)
        directory=state_root/('run-'+now.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]);directory.mkdir(mode=0o700)
        save(directory/'auto-owned.json',{'owner':'tehnet-offline-refresh'})
        metadata=directory/'metadata';metadata.mkdir()
        for name in ['app','tools','deployment']:(directory/name).symlink_to(ROOT/name,target_is_directory=True)
        for name in ['SHA256SUMS','SHA256SUMS.gpg']:shutil.copyfile(seed/'metadata'/name,metadata/name)
        shutil.copyfile(ROOT/'deployment/qualification/devtools-smoke.py',directory/'devtools-smoke.py')
        (metadata/'previous-profile.json').write_bytes(canonical(previous))
        save(metadata/'network-budget.json',{'limit':ATTEMPT_BYTES,'used':0,'requests':0})
        containers=subprocess.check_output(['docker','ps','-a','--no-trunc','--format','{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}'])
        (directory/'containers.before').write_bytes(containers)
        protected=[]
        for line in (seed/'protected.before').read_text().splitlines():
            _,name=line.split('  ',1)
            if name.startswith('/srv/'):continue # service cannot read private engine DBs
            protected.append(hashlib.sha256(Path(name).read_bytes()).hexdigest()+'  '+name)
        (directory/'protected.before').write_text('\n'.join(protected)+'\n')
        # Keep the existing download worker free during the RAM-only laboratory.
        # Publication reacquires the shared lock and rejects a concurrent change.
        fcntl.flock(lock,fcntl.LOCK_UN)
        env={**os.environ,'OPS':str(directory),'HOST_SITE':str(host_site),'PYTHONPATH':str(ROOT)+':'+str(host_site),'PYTHONDONTWRITEBYTECODE':'1','SOFTWARE_REFRESH_BUDGET_FILE':str(metadata/'network-budget.json'),'LAB_STATE_READ':'0'}
        def stage(name):
            status.update({'checked_at':datetime.now(timezone.utc).isoformat(),'stage':name,'run':directory.name,'result':'in_progress'})
            save(status_path,status);save(metadata/(name+'.json'),status);print(json.dumps({'stage':name,'run':directory.name}),flush=True)
        try:
            stage('signed_discovery')
            stage_command(['unshare','--mount','--propagation','private','bash',str(ROOT/'deployment/qualification/discover-devtools.sh')],metadata/'discovery.log',env)
            stage('candidate_signature_chain')
            stage_command(['python3','-m','tools.build_devtools_profile',str(directory),str(ROOT/'deployment/client/offline-install.sh')],metadata/'builder.log',env)
            candidate=json.loads((metadata/'profile-unaccepted.json').read_text());validate_profile(candidate,require_accepted=False)
            if len(candidate['packages'])>200 or sum(p['size_bytes'] for p in candidate['packages'])>128*1024**2:raise ValueError('Candidate reviewed bounds exceeded')
            stage('clean_offline_install')
            stage_command(['unshare','--mount','--propagation','private','bash',str(ROOT/'deployment/qualification/run-devtools-lab.sh')],metadata/'qualification.log',env)
            acceptance=json.loads((metadata/'offline-install-acceptance.json').read_text());identity=validate_acceptance(candidate,acceptance)
            lab=json.loads((metadata/'lab-state.json').read_text())
            if lab['cgroup']['memory.swap.current']!='0' or 'noswap' not in lab['tmpfs_options'] or not lab['all_existing_container_fingerprints_preserved']:raise ValueError('Lab isolation proof failed')
            # Recheck time and signed identity at the final publication boundary.
            from tools.offline_kit import verified_release
            for release in candidate['releases']:
                signed=metadata/('final-'+release['suite']+'.InRelease');signed.write_text(release['inrelease'])
                checked=verified_release(signed,Path('/usr/share/keyrings/ubuntu-archive-keyring.gpg'),minimum_date=datetime.fromisoformat(next(r['date'] for r in previous['releases'] if r['suite']==release['suite'])))
                if checked['inrelease_sha256']!=release['inrelease_sha256'] or (release['suite']!='noble' and datetime.now(timezone.utc)-checked['date']>timedelta(hours=24)):raise ValueError('Candidate too old/changed at publication')
            stage('qualified')
            candidate['accepted']=True;candidate['acceptance_scope']='Automatic clean signed Ubuntu Base24.04.5 amd64; no-network native APT +8 functional tests; not bootedVM/Iran/PyPI acceptance.'
            ready=directory/'public-ready';ready.mkdir()
            (ready/'profile.json').write_bytes(canonical(candidate));(ready/'offline_kit.py').write_bytes((ROOT/'tools/offline_kit.py').read_bytes())
            proof={'tested_at_utc':datetime.now(timezone.utc).isoformat(),'offline_install_pass':True,'profile_sha256':hashlib.sha256((ready/'profile.json').read_bytes()).hexdigest(),'client_code_sha256':hashlib.sha256((ready/'offline_kit.py').read_bytes()).hexdigest(),'qualified_candidate_sha256':identity,'packages':len(candidate['packages']),'package_bytes':sum(p['size_bytes'] for p in candidate['packages']),'functional_tools':acceptance['functional_tools'],'negative_checks':acceptance['negative_checks'],'baseline':candidate['baseline'],'automatic_refresh':True,'refresh_check_hours':6,'refresh_after_hours':12,'publication_max_metadata_age_hours':24,'scope':candidate['acceptance_scope'],'software_payload_disk_files':0,'memory_swap_bytes':0}
            save(ready/'acceptance.json',proof);(ready/'index.html').write_text(render_guide(candidate),encoding='utf-8')
            if dry_run:
                status.update({'stage':'qualified_dry_run','result':'PASS; publication intentionally not performed'});save(status_path,status);return status
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            if snippet.read_bytes()!=initial_snippet:raise ValueError('Owned snippet changed during qualification; publication refused')
            stamp=directory.name.removeprefix('run-');destination=Path('/opt/tehnet-software/public')/('auto-'+stamp);backup=Path('/root/tehnet-backups')/(stamp+'-offline-auto')
            before=metadata/'nginx.before';raw_save(before,snippet.read_bytes())
            status['pending']={'before_file':str(before),'old_sha256':hashlib.sha256(before.read_bytes()).hexdigest(),'new_sha256':hashlib.sha256(BASE.read_bytes().replace(b'\r\n',b'\n')+routes(destination).encode()).hexdigest(),'public':str(destination),'previous_public':str(public)}
            stage('publishing')
            result=publish(ready,snippet,destination,backup,previous_public=public,check=lambda:live_check(destination))
            status.update({'stage':'published','result':'PASS','pending':None,'accepted_at':proof['tested_at_utc'],'profile_sha256':proof['profile_sha256'],'publication':result,'run':directory.name});save(metadata/'publication.json',result);save(status_path,status)
            try:prune_runs(state_root,{directory.name,'run-'+public.name.removeprefix('auto-')});prune_public_and_backups(destination)
            except (OSError,ValueError) as warning:
                status['retention_warning']=str(warning)[:1000];save(status_path,status)
            return status
        except BaseException as failure:
            status.update({'stage':'failed','result':type(failure).__name__+': '+str(failure)[:5000],'failed_at':datetime.now(timezone.utc).isoformat(),'last_failure':type(failure).__name__})
            save(status_path,status);save(metadata/'failure.json',status);raise

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--state',type=Path,required=True);parser.add_argument('--seed',type=Path,required=True);parser.add_argument('--host-site',type=Path,required=True);parser.add_argument('--force',action='store_true');parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(SystemExit(143)))
    try:print(json.dumps(run(args.state,args.seed,args.host_site,force=args.force,dry_run=args.dry_run)))
    except BlockingIOError:raise SystemExit(75)
    except BaseException as failure:
        status_path=args.state/'status.json'
        if args.state.is_dir():
            status=json.loads(status_path.read_text()) if status_path.exists() else {}
            if status.get('stage') not in {'failed','recovery_failed'}:
                status.update({'stage':'preflight_failed','checked_at':datetime.now(timezone.utc).isoformat(),'result':type(failure).__name__+': '+str(failure)[:5000]});save(status_path,status)
        raise
if __name__=='__main__':main()
