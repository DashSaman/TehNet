"""Publish only the offline guide/client code/small metadata under /software/."""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,shutil,signal,subprocess,tempfile
from datetime import datetime,timezone

FILES={'index.html':'text/html; charset=utf-8','profile.json':'application/json','offline_kit.py':'text/plain; charset=utf-8','acceptance.json':'application/json'}
MARKER='# TehNet dated offline guide v1'
BASE=Path(__file__).resolve().parents[1]/'deployment/nginx-engine.conf'

def command(*args):
    result=subprocess.run(args,capture_output=True,text=True,timeout=20)
    if result.returncode:raise RuntimeError('Command failed: '+repr(args)+'\n'+result.stdout+result.stderr)

def atomic(path,data):
    path=Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as out:
        name=Path(out.name);out.write(data);out.flush();os.fsync(out.fileno())
    try:name.chmod(0o644);os.replace(name,path)
    finally:name.unlink(missing_ok=True)

def routes(public):
    if not str(public).startswith('/opt/tehnet-software/public/') or any(c in str(public) for c in ' \n\r\t;{}'):raise ValueError('Unapproved public code directory')
    lines=[MARKER]
    for name,kind in FILES.items():
        url='/software/offline/'+('' if name=='index.html' else name)
        mapping=('root '+str(public)+';\n    try_files /index.html =404;' if name=='index.html' else 'alias '+str(public/name)+';')
        lines.append('''location = URL {
    MAPPING
    types { }
    default_type TYPE;
    limit_except GET { deny all; }
    access_log off;
    error_log /dev/null crit;
    add_header Cache-Control "no-store" always;
    add_header X-Robots-Tag "noindex, nofollow" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer" always;
    add_header Content-Security-Policy "default-src 'none'; style-src 'self'; script-src 'self'; font-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'" always;
}'''.replace('URL',url).replace('MAPPING',mapping).replace('TYPE','"'+kind+'"'))
    return '\n'+'\n'.join(lines)+'\n'

def validate_source(source):
    source=Path(source)
    if {p.name for p in source.iterdir()}!=set(FILES):raise ValueError('Exactly four public code/metadata files required')
    for name in FILES:
        path=source/name
        if path.is_symlink() or not path.is_file() or not 1<=path.stat().st_size<=2*1024**2:raise ValueError('Invalid public code/metadata file')
    profile=json.loads((source/'profile.json').read_text())
    proof=json.loads((source/'acceptance.json').read_text())
    if profile.get('accepted') is not True or profile.get('id')!='noble-devtools-amd64' or proof.get('offline_install_pass') is not True:raise ValueError('Real acceptance required before publication')
    if proof.get('profile_sha256')!=hashlib.sha256((source/'profile.json').read_bytes()).hexdigest():raise ValueError('Accepted profile proof mismatch')
    return {name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in FILES}

def publish(source,snippet,public,backup,*,run=command,check=lambda:None,previous_public=None):
    """Caller holds the existing engine lock. No other site file is written."""
    source,snippet,public,backup=map(Path,(source,snippet,public,backup))
    hashes=validate_source(source);old=snippet.read_bytes()
    expected=BASE.read_bytes().replace(b'\r\n',b'\n')+(routes(Path(previous_public)).encode() if previous_public is not None else b'')
    if old!=expected:raise ValueError('Owned snippet differs from reviewed baseline')
    if public.exists() or backup.exists():raise ValueError('Use new immutable public and backup directories')
    candidate=BASE.read_bytes().replace(b'\r\n',b'\n')+routes(public).encode()
    backup.mkdir(parents=True,mode=0o700);(backup/'nginx-software.before').write_bytes(old)
    (backup/'public-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    if not public.parent.exists():public.parent.mkdir(mode=0o755);public.parent.chmod(0o755)
    public.mkdir(mode=0o755);public.chmod(0o755)
    for name in FILES:shutil.copyfile(source/name,public/name);(public/name).chmod(0o644)
    # Nginx syntax test includes the active sites before any reload. A failed
    # test/reload/post-check restores bytes and verifies the rollback reload.
    try:
        atomic(snippet,candidate);run('nginx','-t');run('systemctl','reload','nginx');check()
    except BaseException as failure:
        atomic(snippet,old)
        try:run('nginx','-t');run('systemctl','reload','nginx')
        except BaseException as rollback:raise RuntimeError('Publication failed AND rollback reload failed; inspect retained backup') from rollback
        raise RuntimeError('Publication failed; prior snippet restored and reload verified') from failure
    return {'published_files_sha256':hashes,'backup':str(backup),'owned_snippet_only':True,'container_restart':False,'software_payload_files':0}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True);args=parser.parse_args()
    if os.geteuid()!=0:raise SystemExit('Run locally as server operator')
    signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(SystemExit(143)))
    stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    with open('/run/lock/tehnet-software-engine.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        result=publish(args.source,'/etc/nginx/snippets/tehnet-software.conf','/opt/tehnet-software/public/offline-'+stamp,'/root/tehnet-backups/'+stamp+'-offline-guide')
    print(json.dumps(result))

if __name__=='__main__':main()
