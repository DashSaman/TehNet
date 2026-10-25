"""Operator-only encrypted metadata recovery. No software payloads; no active overwrite."""
import argparse,hashlib,io,json,os,re,sqlite3,subprocess,tarfile,tempfile,threading
from contextlib import closing
from pathlib import Path
from .auth import AuthStore,SCHEMA as AUTH_SQL
from .db import MIGRATION,initialize
from .external_storage import ExternalRegistry,SCHEMA as EXTERNAL_SQL
from .health import NetworkBudget,SCHEMA as BUDGET_SQL
from .models import Artifact,SourceConfig
from .netguard import canonical_target
from .storage import safe_path,open_regular,FILENAME

STATE_FILES=('data/catalog.sqlite','metadata/public/external.sqlite','metadata/restricted/external.sqlite','auth/auth.sqlite','ops/network.sqlite')
CONFIG_FILES=('configuration/compose.yaml','configuration/nginx-software.conf')
MAX_MEMBER=64*1024**2;MAX_TOTAL=256*1024**2
class RecoveryRejected(ValueError):pass

def unique_json(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise RecoveryRejected('Duplicate JSON field')
        result[k]=v
    return result

def validate_manifest(value):
    if not isinstance(value,dict) or set(value)!={'format','image','files'} or type(value['format'])!=int or value['format']!=1 or not re.fullmatch(r'sha256:[a-f0-9]{64}',str(value['image'])):raise RecoveryRejected('Unsupported backup manifest')
    records=value['files']
    if not isinstance(records,list) or not 5<=len(records)<=7:raise RecoveryRejected('Invalid member count')
    seen={};total=0
    for row in records:
        if not isinstance(row,dict) or set(row)!={'path','size','sha256'}:raise RecoveryRejected('Invalid member metadata')
        name=row['path'];size=row['size']
        if name not in STATE_FILES+CONFIG_FILES or name in seen or type(size)!=int or not 0<size<=MAX_MEMBER or not re.fullmatch('[a-f0-9]{64}',str(row['sha256'])):raise RecoveryRejected('Invalid path, size or hash')
        seen[name]=row;total+=size
    if not set(STATE_FILES)<=set(seen) or total>MAX_TOTAL:raise RecoveryRejected('Incomplete or oversized backup')
    return seen

def structure(db):
    return sorted((kind,name,' '.join((sql or '').split())) for kind,name,sql in db.execute("SELECT type,name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"))

def validate_state(root):
    root=safe_path(root)
    try:
        for name in STATE_FILES:
            path=safe_path(root/name)
            with open_regular(path) as source:
                if os.fstat(source.fileno()).st_size>MAX_MEMBER:raise RecoveryRejected('State cap exceeded')
            with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as db,closing(sqlite3.connect(':memory:')) as expected:
                sql=MIGRATION.read_text(encoding='utf-8') if name.startswith('data/') else AUTH_SQL if name.startswith('auth/') else BUDGET_SQL if name.startswith('ops/') else EXTERNAL_SQL
                expected.executescript(sql)
                if db.execute('PRAGMA user_version').fetchone()!=(1,) or structure(db)!=structure(expected) or db.execute('PRAGMA integrity_check').fetchone()!=('ok',) or db.execute('PRAGMA foreign_key_check').fetchall():raise RecoveryRejected('Schema or database integrity failed')
                if name.startswith('data/'):
                    if db.execute('SELECT version,sha256 FROM schema_migrations').fetchall()!=[(1,hashlib.sha256(sql.encode()).hexdigest())]:raise RecoveryRejected('Research migration mismatch')
                elif name.startswith('auth/'):
                    AuthStore._check(db)
                    from argon2 import extract_parameters,Type
                    for (hashed,) in db.execute('SELECT hash FROM credential'):
                        params=extract_parameters(hashed)
                        if params.type!=Type.ID or params.version!=19 or params.memory_cost>65536 or params.time_cost>3 or params.parallelism>4 or params.salt_len<16 or params.hash_len<32:raise RecoveryRejected('Unsupported password hash parameters')
                elif name.startswith('ops/'):NetworkBudget._check(db)
                else:
                    visibility='public' if '/public/' in name else 'restricted'
                    ExternalRegistry(root/'metadata'/visibility,visibility=visibility)._check(db)
                    for digest,raw,policy,path,url,verified,provenance in db.execute('SELECT * FROM external'):
                        item=Artifact.model_validate_json(raw);source=SourceConfig.model_validate_json(policy)
                        if item.sha256!=digest or item.visibility!=visibility or not FILENAME.fullmatch(item.filename) or not provenance or item.size_bytes>512*1024**2:raise RecoveryRejected('External metadata semantics failed')
                        if canonical_target(source.base_url,path,set(source.allowed_hosts))[1]!=url or not source.routing_enabled or (visibility=='public' and source.visibility!='public'):raise RecoveryRejected('External source policy mismatch')
        return {'verified':True,'state_files':len(STATE_FILES),'payload_files':0}
    except Exception as exc:
        if isinstance(exc,RecoveryRejected):raise
        raise RecoveryRejected('State validation failed') from None

def gpg(home):
    home=safe_path(home)
    if not home.is_dir() or (os.name=='posix' and home.stat().st_mode&0o077):raise RecoveryRejected('Protected GPG home required')
    return ['gpg','--no-options','--homedir',str(home),'--batch','--no-tty']

def valid_decryption_status(status,code):
    lines=status.splitlines()
    if code!=0 or len(status)>65536 or b'[GNUPG:] DECRYPTION_OKAY' not in lines or b'[GNUPG:] GOODMDC' not in lines:return False
    details=[line.split()[2:] for line in lines if line.startswith(b'[GNUPG:] DECRYPTION_INFO ')]
    if len(details)!=1 or len(details[0]) not in [2,3,4]:return False
    info=details[0];mdc,cipher=info[:2];aead=info[2] if len(info)>2 else b'0'
    # GnuPG DETAILS: ignore MDC method when AEAD is nonzero. OCB=2, AES256=9.
    return cipher==b'9' and ((aead==b'0' and mdc==b'2') or aead==b'2') and (len(info)<4 or info[3]==b'0')

def backup_state(root,destination,key_home,recipient,image,*,quiesced=False,configuration=None):
    root=safe_path(root);destination=safe_path(destination)
    if not quiesced or not re.fullmatch('[A-Fa-f0-9]{40}|[A-Fa-f0-9]{64}',recipient):raise RecoveryRejected('Writer freeze and full recipient fingerprint required')
    if destination==root or destination.is_relative_to(root):raise RecoveryRejected('Backup must be outside active state')
    validate_state(root);configuration=configuration or {}
    if set(configuration)-set(CONFIG_FILES):raise RecoveryRejected('Unknown configuration file')
    command=gpg(key_home)+['--trust-model','always','--recipient',recipient,'--cipher-algo','AES256','--compress-algo','none','--encrypt']
    created=False;process=None;timer=None
    try:
        with tempfile.TemporaryDirectory(prefix='engine-metadata-',dir=destination.parent) as temporary:
            stage=Path(temporary);files={}
            for name in STATE_FILES:
                target=stage/name;target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                with closing(sqlite3.connect((root/name).as_uri()+'?mode=ro',uri=True)) as source,closing(sqlite3.connect(target)) as output:source.backup(output)
                target.chmod(0o600);files[name]=target
            validate_state(stage)
            for name,path in configuration.items():
                with open_regular(path) as source:raw=source.read(MAX_MEMBER+1)
                if len(raw)>MAX_MEMBER:raise RecoveryRejected('Configuration cap exceeded')
                target=stage/name;target.parent.mkdir(exist_ok=True,mode=0o700);target.write_bytes(raw);target.chmod(0o600);files[name]=target
            manifest={'format':1,'image':image,'files':[{'path':name,'size':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for name,path in files.items()]}
            validate_manifest(manifest)
            descriptor=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);created=True
            with os.fdopen(descriptor,'wb') as output,tempfile.TemporaryFile() as errors:
                process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=output,stderr=errors)
                timer=threading.Timer(60,process.kill);timer.daemon=True;timer.start()
                with tarfile.open(fileobj=process.stdin,mode='w|') as archive:
                    raw=json.dumps(manifest).encode();member=tarfile.TarInfo('manifest.json');member.size=len(raw);member.mode=0o600;archive.addfile(member,io.BytesIO(raw))
                    for name,path in files.items():
                        member=tarfile.TarInfo(name);member.size=path.stat().st_size;member.mode=0o600
                        with path.open('rb') as source:archive.addfile(member,source)
                process.stdin.close()
                if process.wait(timeout=60)!=0:raise RecoveryRejected('Encryption failed')
                output.flush();os.fsync(output.fileno())
        return {'encrypted':True,'state_files':5,'payload_files':0,'bytes':destination.stat().st_size,'cipher_sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}
    except BaseException:
        if process and process.poll() is None:process.kill();process.wait()
        if created:destination.unlink(missing_ok=True)
        raise RecoveryRejected('Encrypted backup failed; no accepted output') from None
    finally:
        if timer:timer.cancel()

def restore_state(bundle,staging,key_home,*,expected_sha256):
    root=safe_path(staging);bundle=safe_path(bundle)
    if root.is_relative_to(Path('/srv/tehnet-software').absolute()):raise RecoveryRejected('Restore staging must be outside active production state')
    if root.exists() or not root.parent.is_dir():raise RecoveryRejected('New staging directory required; never overwrite active state')
    if not re.fullmatch('[a-f0-9]{64}',str(expected_sha256)):raise RecoveryRejected('Independently trusted ciphertext SHA256 required')
    command=gpg(key_home)+['--pinentry-mode','error','--status-fd','2','--decrypt']
    root.mkdir(mode=0o700);process=None;timer=None
    try:
        with open_regular(bundle) as encrypted,tempfile.TemporaryFile() as errors:
            if os.fstat(encrypted.fileno()).st_size>MAX_TOTAL+1024**2:raise RecoveryRejected('Ciphertext cap exceeded')
            digest=hashlib.sha256()
            while block:=encrypted.read(65536):digest.update(block)
            if digest.hexdigest()!=expected_sha256:raise RecoveryRejected('Trusted ciphertext digest mismatch')
            encrypted.seek(0)
            process=subprocess.Popen(command,stdin=encrypted,stdout=subprocess.PIPE,stderr=errors)
            timer=threading.Timer(60,process.kill);timer.daemon=True;timer.start()
            with tarfile.open(fileobj=process.stdout,mode='r|') as archive:
                first=archive.next()
                if first is None or first.name!='manifest.json' or not first.isfile() or first.size>16384:raise RecoveryRejected('Bounded manifest must be first')
                manifest=json.load(archive.extractfile(first),object_pairs_hook=unique_json);records=validate_manifest(manifest);seen=set()
                for member in archive:
                    if member is first:continue
                    if not member.isfile() or member.name not in records or member.name in seen or member.size!=records[member.name]['size']:raise RecoveryRejected('Unexpected backup member')
                    target=root/member.name;target.parent.mkdir(mode=0o700,parents=True,exist_ok=True);digest=hashlib.sha256();count=0
                    with archive.extractfile(member) as source,target.open('xb') as output:
                        while block:=source.read(65536):count+=len(block);digest.update(block);output.write(block)
                        output.flush();os.fsync(output.fileno())
                    target.chmod(0o600)
                    if count!=member.size or digest.hexdigest()!=records[member.name]['sha256']:raise RecoveryRejected('Member hash failed')
                    seen.add(member.name)
            drained=0
            while block:=process.stdout.read(65536):
                drained+=len(block)
                if drained>1024**2:raise RecoveryRejected('Unexpected trailing plaintext')
            process.stdout.close();code=process.wait(timeout=60);errors.seek(0);status=errors.read(65537)
            # --store packets and plaintext can have exit 0: require actual authenticated AES256 decryption.
            if seen!=set(records) or not valid_decryption_status(status,code):raise RecoveryRejected('Authenticated encryption/completeness required')
        result=validate_state(root)
        auth=AuthStore(root/'auth/auth.sqlite');auth.revoke_all();auth.reset_lockout()
        with closing(sqlite3.connect(root/'ops/network.sqlite')) as db:
            db.execute('UPDATE host SET token=NULL,lease_until=0');db.execute('DELETE FROM full_worker');db.commit()
        result.update({'image':manifest['image'],'staging_only':True,'sessions_invalidated':True})
        (root/'RESTORE_VERIFIED.json').write_text(json.dumps(result)+'\n',encoding='utf-8')
        return result
    except BaseException:
        if process and process.poll() is None:process.kill();process.wait()
        if process and process.stdout:process.stdout.close()
        (root/'RESTORE_REJECTED').write_text('Never activate this directory.\n')
        raise RecoveryRejected('Restore rejected; active state was not modified') from None
    finally:
        if timer:timer.cancel()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['backup','restore','validate'])
    parser.add_argument('--root',type=Path);parser.add_argument('--destination',type=Path);parser.add_argument('--bundle',type=Path);parser.add_argument('--staging',type=Path)
    parser.add_argument('--key-home',type=Path);parser.add_argument('--recipient');parser.add_argument('--image');parser.add_argument('--quiesced',action='store_true');parser.add_argument('--expected-sha256')
    parser.add_argument('--compose',type=Path);parser.add_argument('--nginx-snippet',type=Path);args=parser.parse_args()
    if args.command=='validate':result=validate_state(args.root)
    elif args.command=='restore':result=restore_state(args.bundle,args.staging,args.key_home,expected_sha256=args.expected_sha256)
    else:
        config={k:v for k,v in zip(CONFIG_FILES,[args.compose,args.nginx_snippet]) if v is not None}
        result=backup_state(args.root,args.destination,args.key_home,args.recipient,args.image,quiesced=args.quiesced,configuration=config)
    print(json.dumps(result))
if __name__=='__main__':main()
