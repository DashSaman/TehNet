"""Prepare the signed TehNet kit from one explicitly selected qualified source.

The sibling offline_kit.py must match the hash printed by the TehNet guide.
No fallback,proxy,server payload storage or arbitrary mirror URL is supported.
"""
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit
import argparse,hashlib,http.client,ipaddress,json,math,queue,re,socket,ssl,threading,time
try:
    import offline_kit as kit
except ModuleNotFoundError:
    from tools import offline_kit as kit

QUALIFIED_SOURCES=('arvan', 'linuxmirrors', 'liara', 'hamravesh')
POLICIES={
    'arvan':{'base':'https://mirror.arvancloud.ir/ubuntu/','security':'https://mirror.arvancloud.ir/ubuntu/','networks':['185.143.233.0/24']},
    'linuxmirrors':{'base':'https://repo.linuxmirrors.ir/ubuntu/','security':'https://repo.linuxmirrors.ir/ubuntu/','networks':['65.109.176.185/32']},
    'liara':{'base':'https://linux-mirror.liara.ir/repository/ubuntu/','security':'https://linux-mirror.liara.ir/repository/ubuntu-security/','networks':['185.208.181.182/32']},
    'hamravesh':{'base':'https://repo.hmirror.ir/ubuntu/','security':'https://repo.hmirror.ir/ubuntu/','networks':['62.220.126.214/32']},
}

def mapped_url(profile,source,url):
    if source not in POLICIES or not url.startswith(kit.MIRROR):raise ValueError('Unapproved source/canonical URL')
    relative=url[len(kit.MIRROR):];suite=None
    match=re.fullmatch(r'dists/(noble|noble-updates|noble-security)/(main|universe)/binary-amd64/by-hash/SHA256/[a-f0-9]{64}',relative)
    if match:suite=match[1]
    else:
        packages=[p for p in profile['packages'] if p['relative_path']==relative]
        if len(packages)!=1 or not re.fullmatch(r'pool/(main|universe)/[A-Za-z0-9+_.~/-]+\.deb',relative) or '..' in relative.split('/'):raise ValueError('Archive not in exact profile')
        suite=packages[0]['suite']
    if suite not in kit.SUITES:raise ValueError('Unsupported suite')
    return POLICIES[source]['security' if suite=='noble-security' else 'base']+relative

def validated_target(source,url,*,addresses=None):
    policy=POLICIES[source];parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.port not in {None,443} or parsed.username or parsed.password or parsed.query or parsed.fragment or not any(url.startswith(policy[k]) for k in ['base','security']) or '..' in parsed.path.split('/') or '\\' in url:raise ValueError('Unapproved fixed provider target')
    if addresses is None:
        result=queue.Queue(maxsize=1)
        def resolve():
            try:result.put([row[4][0] for row in socket.getaddrinfo(parsed.hostname,443,type=socket.SOCK_STREAM)])
            except OSError:result.put([])
        threading.Thread(target=resolve,daemon=True).start()
        try:addresses=result.get(timeout=5)
        except queue.Empty:raise ValueError('Provider DNS deadline') from None
    ips=[ipaddress.ip_address(value) for value in addresses]
    if not ips or any(not value.is_global for value in ips):raise ValueError('Non-public/mixed provider DNS')
    networks=[ipaddress.ip_network(value) for value in policy['networks']]
    eligible=sorted(str(value) for value in ips if any(value in network for network in networks))
    if not eligible:raise ValueError('Provider outside reviewed address pins')
    return parsed,eligible[0]

def request_deadline(size):return min(300,max(30,10+math.ceil(size/65536)))

def bounded_download(source,url,destination,size,digest,*,connection_factory=None):
    """Size-aware absolute deadline; timer shuts down the socket,not file buffers."""
    if not kit.SHA.fullmatch(digest) or not 0<size<=128*1024**2:raise ValueError('Download identity bounds')
    parsed,ip=validated_target(source,url);deadline=request_deadline(size);expired=threading.Event()
    class Pinned(http.client.HTTPSConnection):
        def connect(self):
            self.sock=socket.create_connection((ip,443),timeout=10)
            self.sock=self._context.wrap_socket(self.sock,server_hostname=self.host)
            if ipaddress.ip_address(self.sock.getpeername()[0])!=ipaddress.ip_address(ip):raise ValueError('Pinned provider peer changed')
    connection=connection_factory(parsed,ip,deadline) if connection_factory else Pinned(parsed.hostname,timeout=10,context=ssl.create_default_context())
    def abort():
        expired.set()
        if connection.sock:
            try:connection.sock.shutdown(socket.SHUT_RDWR)
            except OSError:pass
    timer=threading.Timer(deadline,abort);timer.daemon=True;timer.start();actual=hashlib.sha256();count=0
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    try:
        connection.request('GET',parsed.path,headers={'Accept-Encoding':'identity','User-Agent':'TehNet-Qualified-Provider-Kit/1'})
        response=connection.getresponse()
        if response.status!=200 or response.getheader('Content-Encoding','identity')!='identity':raise ValueError('Provider redirect/status/encoding refused')
        if response.getheader('Content-Length') not in {None,str(size)}:raise ValueError('Provider size header mismatch')
        with destination.open('xb') as output:
            while True:
                chunk=response.read1(65536)
                if expired.is_set():raise TimeoutError('Provider absolute request deadline')
                if not chunk:break
                count+=len(chunk)
                if count>size:raise ValueError('Provider body size mismatch')
                output.write(chunk);actual.update(chunk)
        if count!=size or actual.hexdigest()!=digest:raise ValueError('Provider full SHA256/size mismatch')
        destination.chmod(0o644)
    except Exception:
        if expired.is_set():raise TimeoutError('Provider absolute request deadline') from None
        raise
    finally:timer.cancel();connection.close()

@contextmanager
def selected_transport(profile,source,*,allow_candidate=False,observations=None):
    if source not in POLICIES or (source not in QUALIFIED_SOURCES and not allow_candidate):raise ValueError('Provider has no accepted real installation')
    kit.validate_profile(profile)
    original_download,original_validator=kit.download,kit.validated_mirror_target
    def download(url,destination,size,digest):
        target=mapped_url(profile,source,url);started=time.monotonic()
        observation={'url':target,'size_bytes':size,'expected_sha256':digest,'complete_hash_verified':False}
        if observations is not None:observations.append(observation)
        try:
            result=bounded_download(source,target,destination,size,digest) if source=='linuxmirrors' else original_download(target,destination,size,digest)
            observation['complete_hash_verified']=True
            return result
        except BaseException as error:
            observation['error']=type(error).__name__+': '+str(error)[:200]
            raise
        finally:observation['elapsed_seconds']=round(time.monotonic()-started,3)
    kit.validated_mirror_target=lambda url,**kwargs:validated_target(source,url,**kwargs)
    kit.download=download
    try:yield
    finally:kit.download,kit.validated_mirror_target=original_download,original_validator

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider',choices=QUALIFIED_SOURCES,required=True)
    parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.manifest.stat().st_size>2*1024**2:raise ValueError('Profile metadata cap')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate profile field')
            result[key]=value
        return result
    profile=json.loads(args.manifest.read_text(encoding='utf-8'),object_pairs_hook=unique)
    with selected_transport(profile,args.provider):result=kit.prepare(profile,args.output)
    result.update({'selected_provider':args.provider,'automatic_fallback':False})
    print(json.dumps(result))

if __name__=='__main__':main()
