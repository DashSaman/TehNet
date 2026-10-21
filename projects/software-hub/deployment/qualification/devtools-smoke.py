"""Functional checks inside the network-isolated disposable Ubuntu client."""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import fcntl,hashlib,json,os,socket,struct,subprocess,tempfile,threading

def run(*args,cwd=None):
    result=subprocess.run(args,cwd=cwd,stderr=subprocess.STDOUT,stdout=subprocess.PIPE,text=True)
    if result.returncode:raise AssertionError(str(args)+'\n'+result.stdout)
    return result.stdout.strip()
interfaces=[name for _,name in socket.if_nameindex()]
with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as check:
    active=[name for name in interfaces if struct.unpack('H',fcntl.ioctl(check.fileno(),0x8913,struct.pack('256s',name.encode()))[16:18])[0]&1]
assert active==['lo'],active
assert not any(line.split()[1]=='00000000' for line in Path('/proc/net/route').read_text().splitlines()[1:])
with socket.socket() as s:
    s.settimeout(1)
    try:s.connect(('1.1.1.1',443))
    except OSError:pass
    else:raise AssertionError('External network unexpectedly available')
with tempfile.TemporaryDirectory(prefix='offline-smoke-') as temp:
    root=Path(temp);fixture=root/'payload.txt';fixture.write_text('TehNet offline fixture\n')
    handler=partial(SimpleHTTPRequestHandler,directory=root)
    server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    url='http://127.0.0.1:'+str(server.server_port)+'/payload.txt'
    assert run('curl','--fail','--silent',url)=='TehNet offline fixture'
    assert run('wget','--quiet','-O','-',url)=='TehNet offline fixture'
    assert run('jq','-nr','{answer:42}.answer')=='42'
    assert run('python3.12','-c',r'''import json;print(json.loads('{"answer":42}')["answer"])''')=='42'
    pip=run('python3','-m','pip','--version');assert pip.startswith('pip ')
    repo=root/'git';run('git','init','--quiet',str(repo));(repo/'fixture.txt').write_text('offline commit\n')
    run('git','add','fixture.txt',cwd=repo)
    run('git','-c','user.name=Offline fixture','-c','user.email=offline@example.invalid','commit','--quiet','-m','offline fixture',cwd=repo)
    assert run('git','show','HEAD:fixture.txt',cwd=repo)=='offline commit'
    run('ssh-keygen','-q','-t','ed25519','-N','','-f',str(root/'fixture-key'))
    assert 'ED25519' in run('ssh-keygen','-lf',str(root/'fixture-key.pub'))
    destination=root/'copy';run('rsync','-a',str(repo)+'/',str(destination)+'/')
    assert (destination/'fixture.txt').read_bytes()==(repo/'fixture.txt').read_bytes()
    server.shutdown();server.server_close();thread.join(timeout=2)
    versions={name:run(*cmd) for name,cmd in {'git':['git','--version'],'curl':['curl','--version'],'jq':['jq','--version'],'python':['python3.12','--version'],'pip':['python3','-m','pip','--version'],'wget':['wget','--version'],'rsync':['rsync','--version'],'ssh':['ssh','-V']}.items()}
    profile=json.loads(Path('/kit/profile.json').read_text());copyrights=[]
    for package in profile['packages']:
        file=Path('/usr/share/doc')/package['package']/'copyright'
        if file.exists():
            raw=file.read_bytes();assert 0<len(raw)<2*1024**2
            copyrights.append({'package':package['package'],'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        else:raise AssertionError('Missing copyright for '+package['package'])
    print(json.dumps({'functional_tools':list(versions),'versions':versions,'installed_packages':len(profile['packages']),'copyrights':copyrights,'network_interfaces':interfaces,'external_connect_refused':True,'fixtures':'local HTTP fetch,JSON expression,Python calculation,pip version,Git commit/read,rsync copy,local Ed25519 key generation; all discarded with RAM root'}))
