"""Measured live delivery checks; remote software is hashed in RAM, never saved."""
import argparse,contextlib,hashlib,importlib.util,io,json,sys,tempfile,threading,time
from datetime import datetime,timezone
from pathlib import Path
from app.models import SourceConfig,Artifact,ValidatedTarget
from app.netguard import validate_target,canonical_target
from app.http_client import PinnedHTTPSConnection,GuardedClient,abort
from app.health import NetworkBudget
from tools.mirror_operations import load_manifest

def request(host,path,method='GET',headers=None,*,origin=False,cap=1500000):
    target=validate_target('https://'+host,path.lstrip('/'),{host}) if not origin else ValidatedTarget(url='https://tehnet.ir'+path,hostname='tehnet.ir',connected_ip='127.0.0.1',port=443)
    if origin and host!='tehnet.ir':raise ValueError('Origin override is only for our own TLS host')
    c=PinnedHTTPSConnection(target,5);timer=threading.Timer(10,abort,args=(c,));timer.daemon=True;timer.start()
    try:
        c.request(method,path,headers={'Accept-Encoding':'identity','User-Agent':'TehNet-Delivery-Acceptance/1',**(headers or {})})
        r=c.getresponse();raw=bytearray()
        while method!='HEAD':
            chunk=r.read1(min(65536,cap-len(raw)+1))
            if not chunk:break
            raw.extend(chunk)
            if len(raw)>cap:raise ValueError('Acceptance response exceeded cap')
        return r.status,{k.lower():v for k,v in r.getheaders()},bytes(raw)
    finally:timer.cancel();c.close()

def verify(manifest,*,providers_only=False,origin=False):
    entries=load_manifest(manifest);report={'tested_at_utc':datetime.now(timezone.utc).isoformat(),'vantage':'origin-loopback-valid-TLS' if origin else 'independent-public-TLS','providers_only':providers_only,'payload_files_written':0,'items':[]}
    if not providers_only:
        spec=importlib.util.spec_from_file_location('verify_live',Path(__file__).with_name('verify_live.py'));module=importlib.util.module_from_spec(spec)
        old=sys.argv;sys.argv=['verify_live','--expect-downloads']+(['--origin'] if origin else [])
        try:
            with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(module)
        finally:sys.argv=old
        report['site_checks']=module.report['checks']
        code,_,raw=request('tehnet.ir','/software/v1/artifacts',origin=origin);data=json.loads(raw)
        assert code==200 and data['total']==len(entries) and {r['sha256'] for r in data['items']}=={e['artifact']['sha256'] for e in entries}
        for path,want in [('/software/access/',503),('/software/private/known',404),('/software/private/unknown',404)]:
            code,h,_=request('tehnet.ir',path,origin=origin);assert code==want and 'no-store' in h['cache-control']
    with tempfile.TemporaryDirectory(prefix='tehnet-verification-metadata-') as temporary:
        budget=NetworkBudget(Path(temporary)/'network.sqlite');budget.initialize();client=GuardedClient(budget)
        for e in entries:
            source=SourceConfig.model_validate(e['source']);item=Artifact.model_validate(e['artifact']);host,url=canonical_target(source.base_url,e['relative_path'],set(source.allowed_hosts));path=url.split(host,1)[1]
            if not providers_only:
                local='/software/download/'+item.sha256+'/'+item.filename
                for method in ['GET','HEAD']:
                    code,h,body=request('tehnet.ir',local,method,{'Range':'bytes=0-15','If-None-Match':'*'},origin=origin)
                    assert code==307 and h.get('location')==url and 'no-store' in h.get('cache-control','') and len(body)<2000
            start=time.monotonic();result=client.verify_remote(source,e['relative_path'],item)
            assert result.full_hash_verified and result.observation.body_bytes==item.size_bytes
            code,h,_=request(host,path,'HEAD');assert code==200 and h.get('content-length')==str(item.size_bytes)
            code,r,prefix=request(host,path,'GET',{'Range':'bytes=0-15'},cap=16)
            assert code==206 and r.get('content-range')==f'bytes 0-15/{item.size_bytes}' and len(prefix)==16
            conditional,_,_=request(host,path,'GET',{'If-None-Match':'*'},cap=16)
            report['items'].append({'filename':item.filename,'sha256':item.sha256,'bytes':item.size_bytes,'full_hash_verified':True,'tls_verified':True,'provider':host,'head':200,'range':206,'conditional':conditional,'tehnet_redirect_verified':not providers_only,'elapsed_seconds':round(time.monotonic()-start,3)})
            time.sleep(1.05)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,default=Path(__file__).resolve().parents[1]/'catalog/public-downloads.json');p.add_argument('--providers-only',action='store_true');p.add_argument('--origin',action='store_true');p.add_argument('--report',type=Path)
    args=p.parse_args();report=verify(args.manifest,providers_only=args.providers_only,origin=args.origin)
    if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
