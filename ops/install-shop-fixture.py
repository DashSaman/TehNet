"""Install only the synthetic hidden product in the already verified private clone."""
from pathlib import Path
from html.parser import HTMLParser
import io,json,shlex,subprocess,tarfile
root=Path(__file__).resolve().parents[1]
class Parts(HTMLParser):
    value=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'data-model-parts' in a:self.value=json.loads(a['data-model-parts'])
p=Parts();p.feed((root/'../../outputs/tehnet-parts-demo/index.html').resolve().read_text(encoding='utf-8'))
files={'model.glb':(root/'../../outputs/tehnet-parts-demo/educational-cable.glb').resolve().read_bytes(),'parts.json':json.dumps(p.value).encode(),'fixture.php':(root/'tests/shop-future-product.php').read_bytes()}
bundle=io.BytesIO()
with tarfile.open(fileobj=bundle,mode='w:gz')as archive:
    for name,data in files.items():info=tarfile.TarInfo(name);info.size=len(data);archive.addfile(info,io.BytesIO(data))
remote=r'''
import pathlib,json,subprocess,tarfile,io,sys,os
base=pathlib.Path('/root/tehnet-ux-preview-20261016');state=json.loads((base/'state.json').read_text());web=state['web_container']
obj=json.loads(subprocess.check_output(['docker','inspect',web]))[0];assert obj['Id']==state['web_id'] and obj['Name']=='/tehnet-ux-preview-wordpress'
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz')as a:
 for m in a:
  assert m.name in ['model.glb','parts.json','fixture.php'];p=base/('fixture-'+m.name);p.write_bytes(a.extractfile(m).read());os.chmod(p,0o600)
  target={'model.glb':'tn-ux-model.glb','parts.json':'tn-ux-parts.json','fixture.php':'tn-ux-fixture.php'}[m.name]
  subprocess.run(['docker','cp',str(p),web+':/tmp/'+target],check=True,capture_output=True)
r=subprocess.run(['docker','exec',web,'php','/tmp/wp-cli.phar','--allow-root','--path=/var/www/html','--user=AmirrezaGol','eval-file','/tmp/tn-ux-fixture.php'],capture_output=True)
if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))
print(r.stdout.decode())
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(remote)],input=bundle.getvalue(),capture_output=True,timeout=120)
if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))
result=json.loads(r.stdout);(root/'qa/shop-ux-2026-10-16/future-product.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('SYNTHETIC_FUTURE_PRODUCT_READY; native3D+5parts; source IDs absent; sale/HTTP/mail closed')
