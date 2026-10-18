"""Operator-only: native signed discovery metadata -> unaccepted dated profile.

Usage from the project root: python3 -m tools.build_devtools_profile OPS deployment/client/offline-install.sh
OPS/metadata must contain the actual discovery outputs. Never sets accepted=true.
"""
import json,sys,re,hashlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
from urllib.parse import unquote
O=Path(sys.argv[1]).resolve()
from tools.offline_kit import verified_release,validate_package
M=O/'metadata';data=json.loads((M/'dependency-discovery.json').read_text());releases={};public=[]
key=Path('/usr/share/keyrings/ubuntu-archive-keyring.gpg')
for f in sorted(M.glob('*_InRelease')):
 result=verified_release(f,key);suite=result['suite'];releases[suite]=result
 public.append({'suite':suite,'inrelease':f.read_text(),'inrelease_sha256':result['inrelease_sha256'],'date':result['date'].isoformat(),'valid_until':result['valid_until'].isoformat() if result['valid_until'] else None,'signers':result['signers']})
for index in data['indices']:
 suite,component=re.search(r'_dists_([^_]+)_(main|universe)_binary-amd64_Packages',index['file']).groups()
 signed=releases[suite]['indices'][component+'/binary-amd64/Packages']
 assert signed['sha256']==index['expanded_sha256'] and signed['size']==index['expanded_bytes']
packages=[]
for uri in data['native_uris']:
 filename=unquote(uri['url']).split('/')[-1];matches=data['signed_index_records'][filename]
 candidates=[]
 for match in matches:
  suite,component=re.search(r'_dists_([^_]+)_(main|universe)_binary-amd64_Packages',match['index']).groups()
  record=validate_package(match['record']);candidates.append((releases[suite]['date'],suite,component,record))
 _,suite,component,record=max(candidates,key=lambda x:x[0])
 assert unquote(uri['url'])=='https://mirror.arvancloud.ir/ubuntu/'+record['relative_path'] and uri['size']==record['size_bytes']
 record.update({'cache_filename':uri['filename'],'suite':suite,'index':component+'/binary-amd64/Packages.xz'})
 packages.append(record)
installer=Path(sys.argv[2]).read_text(encoding='utf-8')
profile={'format':1,'id':'noble-devtools-amd64','distribution':'ubuntu24.04','architecture':'amd64','accepted':False,'generated_at_utc':datetime.now(timezone.utc).isoformat(),'baseline':json.loads((M/'baseline.json').read_text()),'seeds':json.loads((M/'native-seeds.json').read_text()),'packages':packages,'releases':public,'installer':installer,'scope':'Eight tools plus CA TLS support; dependencies resolved against exact clean Ubuntu Base. Frozen dated kit,not general noble-core/VM/Iran acceptance.'}
assert len(packages)==58 and sum(x['size_bytes'] for x in packages)==32139756
(M/'profile-unaccepted.json').write_text(json.dumps(profile,indent=2)+'\n')
updates=next(x for x in public if x['suite']=='noble-updates');original=next(M.glob('*_noble-updates_InRelease'))
negative={}
for name,kwargs,raw in [('tampered-signature',{},original.read_text().replace('Origin: Ubuntu','Origin: forged',1)),('stale-valid-signature',{'now':releases['noble-updates']['date']+timedelta(hours=49)},original.read_text()),('signed-date-rollback',{'minimum_date':releases['noble-updates']['date']+timedelta(seconds=1)},original.read_text())]:
 f=M/('negative-'+name+'.InRelease');f.write_text(raw)
 try:verified_release(f,key,**kwargs)
 except ValueError as e:negative[name]=str(e)
 else:raise AssertionError('Negative signature policy accepted: '+name)
 f.unlink()
(M/'signed-chain-acceptance.json').write_text(json.dumps({'releases':[{k:v for k,v in r.items() if k!='inrelease'} for r in public],'native_index_hashes':data['indices'],'package_count':len(packages),'package_bytes':sum(x['size_bytes'] for x in packages),'negative_checks':negative,'payload_disk_files':0},indent=2)+'\n')
print(json.dumps(profile))
