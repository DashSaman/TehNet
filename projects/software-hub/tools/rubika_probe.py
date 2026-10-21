"""Owner-only Rubika capability probe; no website route or software-payload files."""
import argparse,getpass,hashlib,hmac,ipaddress,json,os,re,secrets,sys,threading,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,unquote,quote
from app.storage import safe_path,open_regular
from app.netguard import validate_target
from app.http_client import PinnedHTTPSConnection,abort

FIXTURE=(b'TehNet public storage capability fixture; no user data.\n'*80)[:4096]
API='botapi.rubika.ir'
DEFAULT_TOKEN=Path('/root/.config/tehnet-software-rubika/token')
class ProbeRejected(ValueError):pass

def protected(path,*,existing=False):
    path=safe_path(path)
    project=Path(__file__).resolve().parents[1]
    if path.is_relative_to(project) or path.is_relative_to(Path('/srv/tehnet-software').absolute()) or any((parent/'.git').exists() for parent in path.parents):raise ProbeRejected('Secret must remain outside repository and website state')
    if os.name=='posix':
        for p in [path.parent]+([path] if existing else []):
            info=p.stat()
            if info.st_uid!=os.getuid() or info.st_mode&0o077:raise ProbeRejected('Owner-only secret path required')
    return path

def validate_token(token):
    if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9:_-]{16,256}',token):raise ProbeRejected('Invalid token format')
    return token

def read_token(path):
    try:
        path=protected(path,existing=True)
        with open_regular(path) as f:raw=f.read(258)
        return validate_token(raw.decode('ascii').strip())
    except Exception:raise ProbeRejected('Protected token is unavailable or invalid') from None

def private_write(path,raw):
    path=safe_path(path);path.parent.mkdir(mode=0o700,parents=True,exist_ok=True);protected(path,existing=path.exists())
    temp=path.parent/('.secret-'+secrets.token_hex(12))
    try:
        fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(temp,path)
    finally:temp.unlink(missing_ok=True)

def set_token(path,token,confirmation):
    validate_token(token)
    if not hmac.compare_digest(token.encode(),confirmation.encode()):raise ProbeRejected('Token confirmation mismatch')
    private_write(path,token.encode()+b'\n')

def endpoint(url,allowed_hosts):
    try:
        p=urlsplit(url)
        if len(url)>4096 or any(ord(c)<33 or ord(c)>126 for c in url) or '\\' in url or any(ord(c)<32 for c in unquote(url)):raise ValueError()
        if p.scheme!='https' or p.username is not None or p.password is not None or p.port not in [None,443] or p.fragment or p.hostname not in allowed_hosts:raise ValueError()
        if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{0,252}',p.hostname or '') or not p.path.startswith('/'):raise ValueError()
        try:ipaddress.ip_address(p.hostname)
        except ValueError:pass
        else:raise ValueError()
        return p.hostname,p.path+('?' +p.query if p.query else '')
    except Exception:raise ProbeRejected('Unapproved HTTPS endpoint') from None

class Transport:
    def request(self,url,method='POST',body=b'',headers=None,allowed_hosts=()):
        connection=None;timer=None;reply=None
        try:
            host,path=endpoint(url,set(allowed_hosts))
            if len(body)>65536 or method not in ['POST','GET','HEAD']:raise ProbeRejected('Bounded probe only')
            target=validate_target('https://'+host,'capability-probe',{host},timeout_seconds=5)
            connection=PinnedHTTPSConnection(target,5)
            timer=threading.Timer(10,abort,args=(connection,));timer.daemon=True;timer.start()
            connection.request(method,path,body=body,headers={'Accept-Encoding':'identity','User-Agent':'TehNet-Rubika-Capability/1',**(headers or {})})
            reply=connection.getresponse()
            if reply.status not in [200,206]:raise ProbeRejected('Provider HTTP response rejected')
            if reply.getheader('Content-Encoding','identity').lower() not in ['','identity']:raise ProbeRejected('Encoded response rejected')
            raw=bytearray()
            while method!='HEAD':
                chunk=reply.read1(min(65536-len(raw)+1,65536))
                if not chunk:break
                raw.extend(chunk)
                if len(raw)>65536:raise ProbeRejected('Provider response exceeds cap')
            return reply.status,{k.lower():v for k,v in reply.getheaders() if k.lower() in ['content-length','content-range','accept-ranges']},bytes(raw)
        except Exception:raise ProbeRejected('Provider request rejected; endpoints and credentials omitted') from None
        finally:
            if timer:timer.cancel()
            if reply:reply.close()
            if connection:connection.close()

def api(token,method,fields,transport):
    if method not in ['getMe','requestSendFile','getFile']:raise ProbeRejected('Unsupported API method')
    _,_,raw=transport.request('https://'+API+'/v3/'+quote(validate_token(token),safe='')+'/'+method,body=json.dumps(fields).encode(),headers={'Content-Type':'application/json'},allowed_hosts={API})
    try:
        value=json.loads(raw)
        if not isinstance(value,dict) or value.get('status')!='OK' or not isinstance(value.get('data'),dict):raise ValueError()
        return value['data']
    except Exception:raise ProbeRejected('Provider JSON/status rejected') from None

def returned_host(url):
    # Discovery never grants permission or opens the returned endpoint.
    try:
        host=urlsplit(url).hostname
        endpoint(url,{host})
        return host
    except Exception:raise ProbeRejected('Invalid returned endpoint') from None

def redacted_host(host,*private_values):
    for value in private_values:host=re.sub(re.escape(value),'REDACTED',host,flags=re.IGNORECASE)
    return host

def probe(token,transport,*,upload_hosts,download_hosts,roundtrip=False,existing=None):
    if existing is not None:
        try:
            if not isinstance(existing,dict) or set(existing)!={'file_id','created_at_utc'} or not re.fullmatch(r'[A-Za-z0-9:_-]{1,512}',existing['file_id']):raise ValueError()
            created_at=datetime.fromisoformat(existing['created_at_utc'])
            if created_at.tzinfo is None or created_at>datetime.now(timezone.utc):raise ValueError()
        except Exception:raise ProbeRejected('Invalid retained fixture record; no replacement upload') from None
    api(token,'getMe',{},transport)
    report={'state':'AUTHENTICATED_API_PASS','production_backend_enabled':False,'payload_files_written':0}
    if not roundtrip:return report,{}
    created=datetime.now(timezone.utc).isoformat()
    if existing is not None:
        file_id=existing['file_id'];created=existing['created_at_utc']
        if not re.fullmatch(r'[A-Za-z0-9:_-]{1,512}',file_id):raise ProbeRejected('Invalid private fixture identity')
    else:
        upload=api(token,'requestSendFile',{'type':'File'},transport)['upload_url'];host=returned_host(upload)
        if host not in upload_hosts:return {**report,'state':'UPLOAD_HOST_REVIEW_REQUIRED','upload_host':redacted_host(host,token)},{}
        endpoint(upload,upload_hosts)
        boundary='TehNetProbe'+secrets.token_hex(12)
        body=('--'+boundary+'\r\nContent-Disposition: form-data; name="file"; filename="tehnet-public-probe.txt"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()+FIXTURE+('\r\n--'+boundary+'--\r\n').encode()
        _,_,raw=transport.request(upload,body=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary},allowed_hosts=upload_hosts)
        try:
            value=json.loads(raw)
            if value.get('status')!='OK':raise ValueError()
            file_id=value['data']['file_id']
            if not re.fullmatch(r'[A-Za-z0-9:_-]{1,512}',file_id):raise ValueError()
        except Exception:raise ProbeRejected('Upload result rejected') from None
    private={'file_id':file_id,'created_at_utc':created}
    download=api(token,'getFile',{'file_id':file_id},transport)['download_url'];host=returned_host(download)
    if host not in download_hosts:return {**report,'state':'DOWNLOAD_HOST_REVIEW_REQUIRED','download_host':redacted_host(host,token,file_id)},private
    endpoint(download,download_hosts)
    status,_,raw=transport.request(download,method='GET',allowed_hosts=download_hosts)
    if status!=200 or len(raw)!=len(FIXTURE) or not hmac.compare_digest(hashlib.sha256(raw).digest(),hashlib.sha256(FIXTURE).digest()):raise ProbeRejected('Fixture byte/hash verification failed')
    head,h,_=transport.request(download,method='HEAD',allowed_hosts=download_hosts)
    ranged,r,raw_range=transport.request(download,method='GET',headers={'Range':'bytes=0-15'},allowed_hosts=download_hosts)
    return {**report,'state':'FIXTURE_ROUNDTRIP_PASS','sha256':hashlib.sha256(FIXTURE).hexdigest(),'bytes':len(FIXTURE),'head_verified':head==200 and h.get('content-length')==str(len(FIXTURE)),'range_verified':ranged==206 and r.get('content-range')==f'bytes 0-15/{len(FIXTURE)}' and raw_range==FIXTURE[:16],'created_at_utc':created,'checked_at_utc':datetime.now(timezone.utc).isoformat()},private

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['set-token','check','roundtrip','recheck']);p.add_argument('--token-file',type=Path,default=DEFAULT_TOKEN)
    p.add_argument('--upload-host',action='append',default=[]);p.add_argument('--download-host',action='append',default=[])
    args=p.parse_args(argv)
    try:
        if args.command=='set-token':
            if not sys.stdin.isatty() or not sys.stdout.isatty():raise ProbeRejected('Use an interactive administrator terminal; no pipes or token arguments')
            if os.name!='posix' or os.getuid()!=0:raise ProbeRejected('Run setup as the Linux server administrator')
            set_token(args.token_file,getpass.getpass('Official bot token (hidden): '),getpass.getpass('Confirm token (hidden): '))
            print('Token saved privately. Rubika website backend remains disabled.');return 0
        token=read_token(args.token_file);record=args.token_file.parent/'fixture-record.json';existing=None
        if args.command=='recheck':
            protected(record,existing=True)
            with open_regular(record) as f:existing=json.loads(f.read(4097))
        report,private=probe(token,Transport(),upload_hosts=set(args.upload_host),download_hosts=set(args.download_host),roundtrip=args.command!='check',existing=existing)
        if private:private_write(record,json.dumps(private).encode()+b'\n')
        print(json.dumps(report));return 0 if report['state'] in ['AUTHENTICATED_API_PASS','FIXTURE_ROUNDTRIP_PASS'] else 3
    except Exception:
        print('Rubika probe/setup rejected; no credentials, private identity or endpoint logged.',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
