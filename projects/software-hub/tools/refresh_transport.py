"""Operator-only bounded fresh signed metadata; package downloads use the client."""
from pathlib import Path
import hashlib,http.client,ipaddress,json,os,socket,ssl,threading,time
from datetime import datetime,timezone
from tools.offline_kit import validated_mirror_target,verified_release,download,MIRROR

def save(path,data):
    path=Path(path);temporary=path.with_suffix('.tmp');raw=(json.dumps(data,indent=2)+'\n').encode()
    with temporary.open('wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
    os.replace(temporary,path)
    if os.name=='posix':
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(directory)
        finally:os.close(directory)

def reserve_request(path,body_cap):
    # A single service holds the global operation lock. Charge before I/O and
    # retain failed reservations. The daily ledger reserves this entire budget.
    path=Path(path);state=json.loads(path.read_text());amount=body_cap+65536
    if body_cap<=0 or state['used']+amount>state['limit'] or state['requests']>=256:raise ValueError('Refresh request budget exhausted')
    state['used']+=amount;state['requests']+=1;save(path,state)

def read_metadata(url,budget):
    parsed,ip=validated_mirror_target(url);cap=2*1024**2;reserve_request(budget,cap);active=[None]
    class Pinned(http.client.HTTPSConnection):
        def connect(self):
            self.sock=socket.create_connection((ip,443),timeout=10);active[0]=self.sock
            self.sock=self._context.wrap_socket(self.sock,server_hostname=self.host,do_handshake_on_connect=False);active[0]=self.sock;self.sock.do_handshake()
            if ipaddress.ip_address(self.sock.getpeername()[0])!=ipaddress.ip_address(ip):raise ValueError('Metadata peer mismatch')
    connection=Pinned(parsed.hostname,timeout=10,context=ssl.create_default_context())
    def abort():
        if active[0]:
            try:active[0].shutdown(socket.SHUT_RDWR)
            except OSError:pass
        connection.close()
    timer=threading.Timer(30,abort);timer.daemon=True;timer.start();body=bytearray()
    try:
        connection.request('GET',parsed.path,headers={'Accept-Encoding':'identity','User-Agent':'TehNet-Offline-Refresh/1'})
        response=connection.getresponse()
        if response.status!=200 or response.getheader('Content-Encoding','identity')!='identity':raise ValueError('Metadata status/redirect/encoding refused')
        length=response.getheader('Content-Length')
        if length is not None and (not length.isdigit() or not 0<int(length)<=cap):raise ValueError('Metadata length cap')
        while True:
            chunk=response.read1(min(65536,cap-len(body)+1))
            if not chunk:break
            body.extend(chunk)
            if len(body)>cap:raise ValueError('Metadata body cap')
        if not body or (length is not None and len(body)!=int(length)):raise ValueError('Metadata incomplete')
        return bytes(body)
    finally:
        timer.cancel();connection.close()
        if active[0]:active[0].close()

def populate_repo(root,metadata,budget,previous):
    """Fetch only exact Ubuntu suite names; native APT later reads file: offline."""
    root,metadata=Path(root),Path(metadata);old=json.loads(Path(previous).read_text());dates={r['suite']:datetime.fromisoformat(r['date']) for r in old['releases']}
    keyring=Path('/usr/share/keyrings/ubuntu-archive-keyring.gpg');records=[]
    for suite in ['noble','noble-updates','noble-security']:
        directory=root/'dists'/suite;directory.mkdir(parents=True)
        signed=directory/'InRelease';signed.write_bytes(read_metadata(MIRROR+'dists/'+suite+'/InRelease',budget));signed.chmod(0o644)
        release=verified_release(signed,keyring,minimum_date=dates[suite]);assert release['suite']==suite
        for component in ['main','universe']:
            path=component+'/binary-amd64/Packages.xz';pin=release['indices'][path];target=directory/path
            reserve_request(budget,pin['size']);download(MIRROR+'dists/'+suite+'/'+path.rsplit('/',1)[0]+'/by-hash/SHA256/'+pin['sha256'],target,pin['size'],pin['sha256']);time.sleep(1.05)
        records.append({'suite':suite,'date':release['date'].isoformat(),'inrelease_sha256':release['inrelease_sha256']})
    for directory in root.rglob('*'):
        if directory.is_dir():directory.chmod(0o755)
    root.chmod(0o755);save(metadata/'fresh-signed-metadata.json',records)

def install_budget_hook(path):
    from tools import offline_kit
    original=offline_kit.download
    def charged(url,destination,size,digest):
        reserve_request(path,size);return original(url,destination,size,digest)
    offline_kit.download=charged
