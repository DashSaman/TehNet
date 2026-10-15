"""Install the authorized TehNet-only daily backup; never prunes existing backup files."""
from pathlib import Path
import base64,hashlib,json,shlex,subprocess
root=Path(__file__).resolve().parents[1]
files={'/opt/tehnet/bin/store-backup.sh':root/'ops/store-backup.sh','/etc/systemd/system/tehnet-store-backup.service':root/'ops/systemd/tehnet-store-backup.service','/etc/systemd/system/tehnet-store-backup.timer':root/'ops/systemd/tehnet-store-backup.timer'}
payload={name:{'content':base64.b64encode(path.read_text(encoding='utf-8').encode()).decode(),'sha256':hashlib.sha256(path.read_text(encoding='utf-8').encode()).hexdigest()} for name,path in files.items()}
script=r'''
import sys,pathlib,json,base64,hashlib,subprocess,os,datetime,re
os.umask(0o077);files=json.load(sys.stdin)
def run(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=600)
 if p.returncode:raise RuntimeError(p.stderr[:1500])
 return p.stdout
assert run(['id','-u']).strip()=='0'
assert run(['docker','port','tehnet-wordpress','80/tcp']).strip()=='127.0.0.1:18082'
assert 'NTPSynchronized=yes' in run(['timedatectl','show','-p','NTPSynchronized'])
cron=subprocess.run(['crontab','-l'],capture_output=True,text=True).stdout
assert not any('tehnet' in line.lower() and re.search(r'backup|dump',line,re.I) for line in cron.splitlines() if not line.lstrip().startswith('#')),'Existing TehNet cron backup; review duplicate before adding a timer'
for path in pathlib.Path('/etc/cron.d').glob('*'):
 if path.is_file():assert not any('tehnet' in line.lower() and re.search(r'backup|dump',line,re.I) for line in path.read_text(errors='replace').splitlines() if not line.lstrip().startswith('#')),'Existing TehNet cron.d backup'
archive=pathlib.Path('/root/tehnet-backups/scheduler-config-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S'));archive.mkdir()
for target,record in files.items():
 path=pathlib.Path(target);data=base64.b64decode(record['content']);assert hashlib.sha256(data).hexdigest()==record['sha256']
 if path.exists():(archive/path.name).write_bytes(path.read_bytes())
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);path.chmod(0o700 if target.endswith('.sh') else 0o644)
run(['bash','-n','/opt/tehnet/bin/store-backup.sh'])
run(['systemd-analyze','verify','/etc/systemd/system/tehnet-store-backup.service','/etc/systemd/system/tehnet-store-backup.timer'])
run(['systemctl','daemon-reload'])
run(['systemctl','start','tehnet-store-backup.service'])
service=run(['systemctl','show','tehnet-store-backup.service','-p','Result','-p','ExecMainStatus','-p','ExecMainCode'])
assert 'Result=success' in service and 'ExecMainStatus=0' in service
run(['systemctl','enable','--now','tehnet-store-backup.timer'])
timer=run(['systemctl','show','tehnet-store-backup.timer','-p','ActiveState','-p','NextElapseUSecRealtime','-p','LastTriggerUSec'])
assert 'ActiveState=active' in timer
backups=sorted(pathlib.Path('/root/tehnet-backups').glob('*-store-review'));latest=backups[-1]
assert (latest/'SHA256SUMS').is_file()
run(['bash','-c','cd '+shlex.quote(str(latest))+' && sha256sum -c SHA256SUMS'])
result={'status':'installed-and-tested','service':service.splitlines(),'timer':timer.splitlines(),'schedule':'03:40 Asia/Tehran daily, persistent after downtime','latest_backup':str(latest),'latest_sql_bytes':(latest/'tehnet.sql.gz').stat().st_size,'latest_files_bytes':(latest/'wordpress-files.tar.gz').stat().st_size,'checksum_verified':True,'retention_deletion_enabled':False,'minimum_free_bytes':3*1024**3,'offsite_transfer_configured':False,'previous_unit_config_backup':str(archive),'installed_file_sha256':{p:r['sha256'] for p,r in files.items()}}
print(json.dumps(result))
'''
script=script.replace('import sys,pathlib,json,base64,hashlib,subprocess,os,datetime,re','import sys,pathlib,json,base64,hashlib,subprocess,os,datetime,re,shlex')
compile(script,'native-backup-install','exec')
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(script)],input=json.dumps(payload).encode(),capture_output=True,timeout=660)
if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
result=json.loads(p.stdout);(root/'qa/store-2026-10-15/production-backup-timer.json').write_text(json.dumps(result,indent=2));print('DAILY_BACKUP_INSTALLED=PASSED; manual execution and checksums passed; daily 03:40 Asia/Tehran; no pruning or offsite transfer')
