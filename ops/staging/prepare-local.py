"""Prepare ignored local secrets/dependencies without overwriting existing settings."""
from pathlib import Path
import hashlib,secrets,urllib.request
base=Path(__file__).resolve().parent
env=base/'.env'
if not env.exists():
    env.write_text(''.join(key+'='+secrets.token_urlsafe(32)+'\n' for key in ['WOO_DB_PASSWORD','WOO_DB_ROOT_PASSWORD','WP_ADMIN_PASSWORD','ERP_ADMIN_PASSWORD']),encoding='utf-8')
target=base/'.local';target.mkdir(exist_ok=True)
dependencies={
    'wp-cli.phar':('https://github.com/wp-cli/wp-cli/releases/download/v2.12.0/wp-cli-2.12.0.phar','ce34ddd838f7351d6759068d09793f26755463b4a4610a5a5c0a97b68220d85c'),
    'woocommerce.zip':('https://downloads.wordpress.org/plugin/woocommerce.11.1.1.zip','c5748c60a28c5d4b439109def3955c5a629f7cd66b919ae5aefa588bcaace710'),
}
for name,(url,expected) in dependencies.items():
    path=target/name
    if path.exists():data=path.read_bytes()
    else:
        with urllib.request.urlopen(url,timeout=60) as response:data=response.read(30000001)
    if len(data)>30000000 or hashlib.sha256(data).hexdigest()!=expected:raise RuntimeError('Dependency checksum mismatch: '+name)
    if not path.exists():path.write_bytes(data)
print('LOCAL_PREPARATION=READY; existing credentials preserved; dependency hashes verified')
