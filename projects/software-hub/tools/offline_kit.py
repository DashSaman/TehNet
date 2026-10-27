"""Dated Ubuntu devtools kit. Package payloads belong on mirrors or the user's disk."""
from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path,PurePosixPath
import argparse,hashlib,http.client,ipaddress,json,lzma,os,queue,re,socket,ssl,subprocess,tempfile,threading,time
from urllib.parse import urlsplit,unquote

SUITES={'noble','noble-updates','noble-security'}
ARCHIVE_KEYS={'790BC7277767219C42C86F933B4FE6ACC0B21F32','F6ECB3762474EDA9D21B7022871920D1991BC93C'}
SHA=re.compile(r'^[a-f0-9]{64}$')
INSTALLER_SHA256='910af90a0cb21c0cba7918f2ae57241239f35cd9a281a6050d4ae4fab3de2f3b'
SEEDS={'git','curl','jq','python3.12-minimal','python3-pip','wget','rsync','openssh-client','ca-certificates'}
MIRROR='https://mirror.arvancloud.ir/ubuntu/'

def validated_mirror_target(url,*,addresses=None):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname!='mirror.arvancloud.ir' or parsed.port not in {None,443} or parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.path.startswith('/ubuntu/') or '..' in PurePosixPath(unquote(parsed.path)).parts or '\\' in parsed.path:raise ValueError('Unapproved mirror target')
    if addresses is None:
        result=queue.Queue(maxsize=1)
        def resolve():
            try:result.put([r[4][0] for r in socket.getaddrinfo(parsed.hostname,443,type=socket.SOCK_STREAM)])
            except OSError:result.put([])
        threading.Thread(target=resolve,daemon=True).start()
        try:addresses=result.get(timeout=5)
        except queue.Empty:raise ValueError('DNS deadline') from None
    ips=[ipaddress.ip_address(x) for x in addresses]
    if not ips or any(not x.is_global for x in ips):raise ValueError('Non-public/mixed mirror DNS')
    eligible=[str(x) for x in ips if x.version==4 and x in ipaddress.ip_network('185.143.233.0/24')]
    if not eligible:raise ValueError('Mirror outside reviewed allocation')
    return parsed,eligible[0]

def download(url,destination,size,digest):
    parsed,ip=validated_mirror_target(url);destination=Path(destination)
    if not SHA.fullmatch(digest) or not 0<size<=128*1024**2:raise ValueError('Download identity bounds')
    active=[None]
    class Pinned(http.client.HTTPSConnection):
        def connect(self):
            self.sock=socket.create_connection((ip,443),timeout=10)
            active[0]=self.sock
            self.sock=self._context.wrap_socket(self.sock,server_hostname=self.host,do_handshake_on_connect=False)
            active[0]=self.sock;self.sock.do_handshake()
            if ipaddress.ip_address(self.sock.getpeername()[0])!=ipaddress.ip_address(ip):raise ValueError('Pinned TLS peer changed')
    connection=Pinned(parsed.hostname,timeout=10,context=ssl.create_default_context())
    def abort():
        if active[0]:
            try:active[0].shutdown(socket.SHUT_RDWR)
            except OSError:pass
        connection.close()
    timer=threading.Timer(30,abort);timer.daemon=True;timer.start();total=0;actual=hashlib.sha256()
    destination.parent.mkdir(parents=True,exist_ok=True)
    try:
        connection.request('GET',parsed.path,headers={'Accept-Encoding':'identity','User-Agent':'TehNet-Ubuntu-Offline-Kit/1'})
        response=connection.getresponse()
        if response.status!=200 or response.getheader('Content-Encoding','identity')!='identity':raise ValueError('Mirror redirect/encoding/status refused')
        if response.getheader('Content-Length') not in {None,str(size)}:raise ValueError('Mirror size header mismatch')
        with destination.open('xb') as f:
            while True:
                chunk=response.read1(65536)
                if not chunk:break
                total+=len(chunk)
                if total>size:raise ValueError('Mirror response cap')
                actual.update(chunk);f.write(chunk)
        if total!=size or actual.hexdigest()!=digest:raise ValueError('Mirror full SHA256/size mismatch')
        destination.chmod(0o644)
    finally:
        timer.cancel();connection.close()
        if active[0]:active[0].close()

def validate_profile(profile,*,require_accepted=True):
    if not isinstance(profile,dict) or profile.get('format')!=1 or profile.get('id')!='noble-devtools-amd64' or profile.get('architecture')!='amd64' or profile.get('distribution')!='ubuntu24.04' or type(profile.get('accepted')) is not bool or (require_accepted and not profile['accepted']):raise ValueError('Unsupported/unaccepted offline profile')
    packages=profile.get('packages');seeds=profile.get('seeds');releases=profile.get('releases')
    if not isinstance(packages,list) or not 1<=len(packages)<=200 or not isinstance(seeds,list) or {x.get('package') for x in seeds}!=SEEDS or len(seeds)!=9:raise ValueError('Bounded exact profile required')
    if not isinstance(releases,list) or len(releases)!=3 or {r.get('suite') for r in releases}!=SUITES:raise ValueError('All signed Ubuntu suites required')
    seen=set();cache=set()
    for p in packages:
        record={'Package':p['package'],'Version':p['version'],'Architecture':p['architecture'],'Filename':p['relative_path'],'SHA256':p['sha256'],'Size':str(p['size_bytes'])}
        identity=validate_package(record);key=(identity['package'],identity['version'],identity['architecture'])
        if key in seen or p['cache_filename'] in cache or not re.fullmatch(r'[A-Za-z0-9+_.%:~-]+\.deb',p['cache_filename']) or p['filename']!=identity['filename'] or p['suite'] not in SUITES or not re.fullmatch(r'(main|universe)/binary-amd64/Packages\.xz',p['index']):raise ValueError('Conflicting/invalid profile package')
        seen.add(key);cache.add(p['cache_filename'])
    if sum(p['size_bytes'] for p in packages)>256*1024**2:raise ValueError('Profile total byte cap')
    if any(not any(p['package']==s['package'] and p['version']==s['version'] for p in packages) for s in seeds):raise ValueError('Seed closure absent')
    installer=profile.get('installer','')
    if not isinstance(installer,str) or hashlib.sha256(installer.encode()).hexdigest()!=INSTALLER_SHA256:raise ValueError('Unrecognized offline installer')
    return profile

def prepare(profile,output,*,keyring=Path('/usr/share/keyrings/ubuntu-archive-keyring.gpg'),require_accepted=True):
    validate_profile(profile,require_accepted=require_accepted)
    output=Path(output).absolute()
    if output.exists() or output.is_symlink() or not output.parent.is_dir():raise ValueError('Use a new kit directory under an existing parent')
    resolved=output.resolve()
    if any(resolved.is_relative_to(Path(x)) for x in ['/srv/tehnet-software','/opt/tehnet','/opt/tehnet-software','/var/www']):raise ValueError('Never prepare package files on the website')
    wanted={(p['package'],p['version'],p['architecture']) for p in profile['packages']}
    with tempfile.TemporaryDirectory(prefix='.tehnet-kit-',dir=output.parent) as temp:
        root=Path(temp);root.chmod(0o755);proven={};checked=[]
        for release in profile['releases']:
            suite=release['suite'];directory=root/'repo/dists'/suite;directory.mkdir(parents=True)
            signed=directory/'InRelease';signed.write_text(release['inrelease'],encoding='utf-8');signed.chmod(0o644)
            metadata=verified_release(signed,keyring)
            if metadata['suite']!=suite or metadata['inrelease_sha256']!=release['inrelease_sha256']:raise ValueError('Profile signed release identity mismatch')
            for path in ['main/binary-amd64/Packages.xz','universe/binary-amd64/Packages.xz']:
                pin=metadata['indices'][path];target=directory/path
                url=MIRROR+'dists/'+suite+'/'+path.rsplit('/',1)[0]+'/by-hash/SHA256/'+pin['sha256']
                download(url,target,pin['size'],pin['sha256'])
                for record in verified_index_records(target.read_bytes(),metadata,path,wanted=wanted):
                    item=validate_package(record);key=(item['package'],item['version'],item['architecture'],suite,path);proven[key]=item
                checked.append({'suite':suite,'index':path,'sha256':pin['sha256']});time.sleep(1.05)
        for p in profile['packages']:
            item=proven.get((p['package'],p['version'],p['architecture'],p['suite'],p['index']))
            if item is None or any(item[k]!=p[k] for k in ['sha256','size_bytes','relative_path','filename']):raise ValueError('Package absent/conflicting in authenticated index')
        for index,p in enumerate(profile['packages']):
            download(MIRROR+p['relative_path'],root/'archives'/p['cache_filename'],p['size_bytes'],p['sha256'])
            print(f"Verified {index+1}/{len(profile['packages'])}: {p['package']}",flush=True);time.sleep(1.05)
        (root/'packages.tsv').write_text(''.join('\t'.join(str(p[k]) for k in ['package','version','architecture','relative_path','sha256','size_bytes','cache_filename'])+'\n' for p in profile['packages']))
        (root/'seeds.txt').write_text(''.join(s['package']+'='+s['version']+'\n' for s in profile['seeds']))
        (root/'snapshot.txt').write_text(profile['generated_at_utc']+'\n')
        (root/'install.sh').write_text(profile['installer']);(root/'install.sh').chmod(0o755)
        (root/'profile.json').write_text(json.dumps(profile,indent=2)+'\n')
        for directory in root.rglob('*'):
            if directory.is_dir():directory.chmod(0o755)
        os.replace(root,output)
    return {'packages':len(profile['packages']),'package_bytes':sum(p['size_bytes'] for p in profile['packages']),'signed_indices':checked,'payload_location':'user-selected kit directory; external mirror originals','complete_hashes':True}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['prepare']);parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.manifest.stat().st_size>2*1024**2:raise ValueError('Profile metadata cap')
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result:raise ValueError('Duplicate profile field')
            result[k]=v
        return result
    profile=json.loads(args.manifest.read_text(encoding='utf-8'),object_pairs_hook=unique)
    print(json.dumps(prepare(profile,args.output)))

def fields(text):
    result={};last=None
    for line in text.splitlines():
        if not line:continue
        if line[0].isspace():
            if last is None:raise ValueError('Orphan metadata continuation')
            result[last]+='\n'+line.strip();continue
        if ':' not in line:raise ValueError('Malformed metadata field')
        name,value=line.split(':',1)
        if name in result:raise ValueError('Duplicate metadata field')
        result[name]=value.strip();last=name
    return result

def parse_release(text,*,now=None,minimum_date=None):
    if len(text.encode())>2*1024**2:raise ValueError('Release cap')
    item=fields(text);now=now or datetime.now(timezone.utc)
    suite=item.get('Suite')
    if item.get('Origin')!='Ubuntu' or item.get('Label')!='Ubuntu' or item.get('Codename')!='noble' or suite not in SUITES:raise ValueError('Unexpected Ubuntu suite/origin')
    date=parsedate_to_datetime(item['Date'])
    if date.tzinfo is None or now.tzinfo is None:raise ValueError('Timezone required')
    if date>now+timedelta(minutes=5):raise ValueError('Future signed Date')
    if suite!='noble' and now-date>timedelta(hours=48):raise ValueError('Stale mutable suite')
    if minimum_date is not None and date<minimum_date:raise ValueError('Signed Date rollback')
    until=parsedate_to_datetime(item['Valid-Until']) if 'Valid-Until' in item else None
    if until is not None and (until.tzinfo is None or until<now or until<date):raise ValueError('Expired/inconsistent Valid-Until')
    indices={}
    for line in item.get('SHA256','').splitlines():
        if not line:continue
        parts=line.split()
        if len(parts)!=3:raise ValueError('Malformed signed index identity')
        digest,size,path=parts
        if re.fullmatch(r'(main|universe)/binary-amd64/Packages(?:\.xz)?',path):
            if path in indices or not SHA.fullmatch(digest) or not size.isdigit() or not 0<int(size)<=256*1024**2:raise ValueError('Invalid signed index bounds')
            indices[path]={'sha256':digest,'size':int(size)}
    if not indices:raise ValueError('Required signed indices absent')
    return {'suite':suite,'date':date,'valid_until':until,'indices':indices}

def verified_release(path,keyring,*,now=None,minimum_date=None):
    path=Path(path);keyring=Path(keyring)
    if not path.is_file() or path.is_symlink() or not 1<=path.stat().st_size<=2*1024**2:raise ValueError('InRelease file/cap')
    result=subprocess.run(['gpgv','--keyring',str(keyring.resolve()),'--status-fd','2','--output','-',str(path.resolve())],capture_output=True,timeout=10)
    signers=re.findall(rb'\[GNUPG:\] VALIDSIG ([A-F0-9]{40}) ',result.stderr)
    if result.returncode or not any(s.decode() in ARCHIVE_KEYS for s in signers):raise ValueError('Ubuntu InRelease signature rejected')
    item=parse_release(result.stdout.decode('utf-8'),now=now,minimum_date=minimum_date)
    item.update({'inrelease_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'signers':[s.decode() for s in signers]})
    return item

def validate_package(record):
    name=record['Package'];version=record['Version'];arch=record['Architecture'];path=record['Filename'];digest=record['SHA256'];size=record['Size']
    if not re.fullmatch('[a-z0-9][a-z0-9+.-]{0,79}',name) or not re.fullmatch('[A-Za-z0-9.+:~_-]{1,160}',version) or arch not in {'amd64','all'}:raise ValueError('Invalid package identity')
    if not re.fullmatch(r'pool/(main|universe)/[A-Za-z0-9+_.~/-]+\.deb',path) or '..' in PurePosixPath(path).parts:raise ValueError('Package path rejected')
    if not SHA.fullmatch(digest) or not str(size).isdigit() or not 0<int(size)<=128*1024**2:raise ValueError('Package digest/size rejected')
    return {'package':name,'version':version,'architecture':arch,'relative_path':path,'filename':path.split('/')[-1],'sha256':digest,'size_bytes':int(size)}

def xz_chunks(data):
    cursor=0;pending=b'';streams=0
    while pending or cursor<len(data):
        if not pending:pending=data[cursor:cursor+65536];cursor+=len(pending)
        padding=0
        while pending.startswith(b'\0'):
            count=len(pending)-len(pending.lstrip(b'\0'));padding+=count;pending=pending[count:]
            if not pending and cursor<len(data):pending=data[cursor:cursor+65536];cursor+=len(pending)
        if padding%4:raise ValueError('Invalid XZ stream padding')
        if not pending:break
        streams+=1
        if streams>64:raise ValueError('XZ stream count cap')
        decoder=lzma.LZMADecompressor(memlimit=128*1024**2);incoming=pending;pending=b''
        try:
            while True:
                chunk=decoder.decompress(incoming,max_length=65536);incoming=b''
                if chunk:yield chunk
                if decoder.eof:pending=decoder.unused_data;break
                if decoder.needs_input:
                    if cursor==len(data):raise ValueError('Truncated XZ stream')
                    incoming=data[cursor:cursor+65536];cursor+=len(incoming)
        except lzma.LZMAError as exc:raise ValueError('Invalid XZ metadata') from exc
    if not streams:raise ValueError('Empty XZ metadata')

def verified_index_records(data,release,path,*,expanded_cap=256*1024**2,wanted=None):
    if path not in release['indices'] or not path.endswith('.xz'):raise ValueError('Unlisted index')
    pin=release['indices'][path];plain=release['indices'].get(path[:-3])
    if plain is None or len(data)!=pin['size'] or len(data)>64*1024**2 or hashlib.sha256(data).hexdigest()!=pin['sha256']:raise ValueError('Signed compressed index mismatch')
    total=0;digest=hashlib.sha256();buffer=b'';records=[]
    def collect(para):
        if not para:return
        if len(para)>128*1024:raise ValueError('Package paragraph cap')
        record=fields(para.decode('utf-8'));key=(record.get('Package'),record.get('Version'),record.get('Architecture'))
        if wanted is None or key in wanted:validate_package(record);records.append(record)
    for chunk in xz_chunks(data):
        total+=len(chunk);digest.update(chunk)
        if total>min(expanded_cap,plain['size']):raise ValueError('Index expansion cap')
        buffer+=chunk
        while b'\n\n' in buffer:
            para,buffer=buffer.split(b'\n\n',1);collect(para)
        if len(buffer)>128*1024:raise ValueError('Package paragraph cap')
    if buffer.strip():collect(buffer)
    if total!=plain['size'] or digest.hexdigest()!=plain['sha256']:raise ValueError('Signed expanded index mismatch')
    return records

if __name__=='__main__':main()
