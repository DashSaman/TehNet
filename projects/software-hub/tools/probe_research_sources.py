"""Bounded manual HTTPS metadata checks of the fixed, attributed research targets.

No routing approval, archive fetches, redirects, HTTP fallback or Iran claim.
Run on Linux with the reviewed runtime and Ubuntu archive keyring. Output is small
metadata; response bodies exist only in memory or /run for signature verification.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,http.client,json,re,ssl,tempfile,threading,time
from app.netguard import validate_target,TargetRejected
from app.http_client import PinnedHTTPSConnection,abort
from tools.offline_kit import verified_release

ROOT=Path(__file__).resolve().parents[1]

def research_targets():
    text=(ROOT/'research/upstream/Linux/MIRROR_SOURCES.yaml').read_text(encoding='utf-8')
    rows=[]
    for block in re.split(r'\n  - id: ',text)[1:]:
        identity=block.splitlines()[0].strip()
        values={key:re.search(r'^    '+key+r': (\S+)',block,re.M)[1] for key in ['base_url','ecosystem']}
        rows.append({'id':identity,**values})
    catalog=json.loads((ROOT/'catalog/research-sources.json').read_text())['sources']
    if len(rows)!=27 or {r['id'] for r in rows}!={r['id'] for r in catalog}:raise ValueError('Fixed research target identity mismatch')
    return rows

def fetch_metadata(url,limit):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.username or parsed.password or parsed.query or parsed.fragment:raise ValueError('HTTPS metadata target required')
    # Validate/pin the exact public host; root requests use a safe representative
    # path for the same connection. No redirect or user-controlled target exists.
    target=validate_target('https://'+parsed.hostname+'/',parsed.path.lstrip('/') or 'index.html',{parsed.hostname},timeout_seconds=4)
    connection=PinnedHTTPSConnection(target,6)
    timer=threading.Timer(8,abort,args=(connection,));timer.daemon=True;timer.start()
    try:
        connection.request('GET',parsed.path or '/',headers={'User-Agent':'TehNet-Research-Metadata-Check/1','Accept-Encoding':'identity'})
        reply=connection.getresponse()
        try:
            status=reply.status;body=bytearray()
            while len(body)<limit:
                chunk=reply.read1(min(16384,limit-len(body)))
                if not chunk:break
                body.extend(chunk)
            return {'status':status,'tls_verified':True,'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'body_is_prefix':len(body)==limit},bytes(body)
        finally:reply.close()
    finally:timer.cancel();connection.close()

def probe(row):
    started=time.monotonic();url=row['base_url'];url='https:'+url[5:] if url.startswith('http:') else url
    result={'id':row['id'],'checked_at':datetime.now(timezone.utc).isoformat(),'url':url,'http_upgraded_to_https':url!=row['base_url'],'state':'unavailable','installation_verified':False,'routing_enabled':False}
    try:
        response,_=fetch_metadata(url,65536);result['endpoint']=response
        status=response['status']
        result['state']='endpoint_reachable' if status==200 else ('restricted' if status in {401,403,429} else ('redirect' if 300<=status<400 else 'unavailable'))
        # Exact Ubuntu suite metadata is stronger than a reachable HTML portal,
        # but still is not an artifact hash/install/retention acceptance.
        if row['ecosystem']=='apt' and row['id']!='shatel-debian':
            signed_url=url.rstrip('/')+'/dists/noble-updates/InRelease'
            response,body=fetch_metadata(signed_url,524288);result['signed_metadata_response']=response
            if response['status']==200 and not response['body_is_prefix']:
                with tempfile.TemporaryDirectory(prefix='tehnet-source-signature-',dir='/run') as temp:
                    path=Path(temp)/'InRelease';path.write_bytes(body)
                    try:checked=verified_release(path,Path('/usr/share/keyrings/ubuntu-archive-keyring.gpg'))
                    except ValueError as error:
                        result.update({'state':'metadata_rejected','metadata_error':str(error)[:160]})
                        checked=None
                if checked:result.update({'state':'signed_metadata_verified','signed_suite':'noble-updates','signed_date':checked['date'].isoformat(),'inrelease_sha256':checked['inrelease_sha256'],'signers':checked['signers']})
    except (OSError,ssl.SSLError,http.client.HTTPException,ValueError,TimeoutError) as error:
        # A vantage-specific failure is never proof that a provider is offline.
        result['error_code']=str(error) if isinstance(error,TargetRejected) else type(error).__name__
    result['elapsed_seconds']=round(time.monotonic()-started,3)
    return result

def main():
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(probe,research_targets()))
    print(json.dumps({'schema':1,'checked_at':datetime.now(timezone.utc).isoformat(),'vantage':'current foreign VPS; not Iran','scope':'One bounded HTTPS endpoint GET and,for Ubuntu APT sources,one signed noble-updates InRelease; no packages,install or production routing approvals','maximum_requests':40,'maximum_response_body_bytes':5505024,'payloads_saved':0,'observations':rows},indent=2))

if __name__=='__main__':main()
