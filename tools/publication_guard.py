#!/usr/bin/env python3
"""Check tracked public files. Diagnostics never include matched values.

This bounded guard complements a dedicated secret scanner and manual review;
it does not certify Git history, screenshots, archives or hosted PR caches.
"""
from pathlib import Path
import argparse,hashlib,ipaddress,json,os,re,subprocess,sys

PRIVATE_KEY=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')
SECRET=re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{32,}|AKIA[0-9A-Z]{16})\b')
LOCAL_PATH=re.compile(rb'[A-Za-z]:[/\\]+Users[/\\]+[^\s/\\"<>]+[/\\]',re.I)
USERINFO=re.compile(rb"https?://[^\s/:\"'<>]+:[^\s/@\"'<>]+@",re.I)
IP=re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])|(?<![\w:])(?:[a-fA-F0-9]{0,4}:){2,}[a-fA-F0-9:]{0,39}(?![\w:])')
CONTEXT=re.compile(r'origin|\bVPS\b|\bSSH\b|سرور|\bAAAA\b|پنل',re.I)
PROSE_PASSWORD=re.compile(r'(?i)\bpassword(?:\s+for\s+[^:\r\n]{1,70})?\s*:\s*([^\s<>]+)')
EXAMPLES=[ipaddress.ip_network(n)for n in ['192.0.2.0/24','198.51.100.0/24','203.0.113.0/24','2001:db8::/32']]
def content_digest(data):return hashlib.sha256(data.replace(b'\r\n',b'\n')).hexdigest()

def inspect(path,data,config,denied=()):
    issues=[]
    def report(category,offset=0):issues.append({'path':path,'line':data[:offset].count(b'\n')+1,'category':category})
    if any(path.startswith(prefix)for prefix in config.get('private_prefixes',[])):report('private-evidence-path')
    if Path(path).name in ['.env','id_rsa','id_ed25519','wp-config.php'] or Path(path).suffix.lower()in ['.sql','.sqlite','.sqlite3','.db','.p12','.pfx']:report('private-file-type')
    for rule,category in [(SECRET,'credential-format'),(LOCAL_PATH,'personal-workstation-path'),(USERINFO,'embedded-url-credentials')]:
        for m in rule.finditer(data):report(category,m.start())
    if PRIVATE_KEY.search(data):
        fixture=config.get('public_test_keys',{}).get(path)
        if not fixture or content_digest(data)!=fixture.get('sha256')or not fixture.get('reason'):report('private-key-material')
    for value in denied:
        if not value:continue
        for m in re.finditer(re.escape(value.encode()),data):report('known-sensitive-value',m.start())
    if path.endswith(('.md','.txt','.html')):
        text=data.decode('utf-8',errors='replace')
        for m in PROSE_PASSWORD.finditer(text):
            value=m.group(1).strip('`\"\'.,;')
            if len(value)>=8 and not any(word in value.lower()for word in ['example','placeholder','fixture','redact','getenv'])and not value.startswith(('$','[')):
                issues.append({'path':path,'line':text[:m.start()].count('\n')+1,'category':'prose-password'})
    if path in config.get('operator_documents',[]):
        text=data.decode('utf-8',errors='replace')
        for number,line in enumerate(text.splitlines(),1):
            if not CONTEXT.search(line):continue
            for m in IP.finditer(line):
                try:addr=ipaddress.ip_address(m.group())
                except ValueError:continue
                if addr.is_global and not any(addr.version==net.version and addr in net for net in EXAMPLES):issues.append({'path':path,'line':number,'category':'literal-operator-address'})
    approved=config.get('approved_content',{}).get(path,{})
    if approved.get('sha256')==content_digest(data)and approved.get('reason'):
        issues=[row for row in issues if row['category']not in approved.get('categories',[])]
    return issues

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.cwd())
    parser.add_argument('--deny-values-file',type=Path,help='Private JSON list outside the repository; never printed')
    args=parser.parse_args();root=args.root.resolve()
    io_root=root
    if os.name=='nt'and not str(root).startswith('\\\\?\\'):
        io_root=Path('\\\\?\\UNC\\'+str(root)[2:]if str(root).startswith('\\\\')else'\\\\?\\'+str(root))
    config=json.loads((io_root/'.publication-policy.json').read_text(encoding='utf-8'))
    denied=json.loads(args.deny_values_file.read_text(encoding='utf-8'))if args.deny_values_file else []
    if not isinstance(denied,list)or any(not isinstance(v,str)for v in denied):raise ValueError('Expected private string list')
    paths=subprocess.check_output(['git','-c','core.longpaths=true','-C',str(root),'ls-files','-z']).decode().split('\0')[:-1]
    issues=[];checked=0
    for path in paths:
        try:data=(io_root/path).read_bytes()
        except OSError:
            issues.append({'path':path,'category':'unreadable-tracked-file'})
            continue
        checked+=1;issues.extend(inspect(path,data,config,denied))
    print(json.dumps({'tracked_files':len(paths),'checked_tracked_files':checked,'issues':issues,'status':'PASS'if not issues else'FAIL'},ensure_ascii=False))
    return bool(issues)
if __name__=='__main__':sys.exit(main())
