"""Provision the existing theme's OFL fonts into ignored local runtime storage."""
from pathlib import Path
import hashlib,json,urllib.request
base=Path(__file__).resolve().parent
target=base/'.local/fonts';target.mkdir(parents=True,exist_ok=True)
source='https://raw.githubusercontent.com/rastikerdar/vazirmatn/v33.003/'
hashes={}
for weight in ['Regular','Medium','SemiBold','ExtraBold']:
    name='Vazirmatn-'+weight+'.woff2'
    with urllib.request.urlopen(source+'fonts/webfonts/'+name,timeout=30) as response:data=response.read(500001)
    if not data.startswith(b'wOF2') or len(data)>500000:raise RuntimeError('Invalid font download')
    (target/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
with urllib.request.urlopen(source+'OFL.txt',timeout=30) as response:(target/'OFL.txt').write_bytes(response.read(20000))
(base.parent.parent/'qa/store-2026-10-15/font-runtime.json').write_text(json.dumps({'source':source,'license':'SIL OFL 1.1','sha256':hashes},indent=2))
print('LOCAL_FONTS=READY; binary font files remain outside Git')
