import hashlib,json,socket,ssl,subprocess,sys,tempfile,threading,time,unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
from unittest.mock import patch
from tools.offline_kit import validated_mirror_target,validate_profile,download,prepare

class OfflineKitPolicyTests(unittest.TestCase):
    def test_only_reviewed_public_mirror_https_targets(self):
        url='https://mirror.arvancloud.ir/ubuntu/pool/main/j/jq/jq_1.7_amd64.deb'
        self.assertEqual(validated_mirror_target(url,addresses=['185.143.233.132'])[1],'185.143.233.132')
        for bad in ['http://mirror.arvancloud.ir/ubuntu/file','https://user:secret@mirror.arvancloud.ir/ubuntu/file','https://mirror.arvancloud.ir:444/ubuntu/file','https://other.example/ubuntu/file',url+'?token=secret','https://mirror.arvancloud.ir/ubuntu/../etc/passwd']:
            with self.subTest(url=bad):
                with self.assertRaises(ValueError):validated_mirror_target(bad,addresses=['185.143.233.132'])
        for addresses in [['127.0.0.1'],['185.143.233.132','10.0.0.1'],['8.8.8.8']]:
            with self.subTest(addresses=addresses):
                with self.assertRaises(ValueError):validated_mirror_target(url,addresses=addresses)
    def test_missing_unaccepted_or_unbounded_profile_never_prepares(self):
        for profile in [{},{'format':1,'id':'other','accepted':True},{'format':1,'id':'noble-devtools-amd64','accepted':False}]:
            with self.subTest(profile=profile):
                with self.assertRaises(ValueError):validate_profile(profile)
    def test_actual_cli_reaches_output_preflight_without_name_error_or_network(self):
        root=Path(__file__).resolve().parents[1]
        profile=json.loads((root/'profiles/noble-devtools-amd64/manifest.json').read_text());profile['accepted']=True
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'accepted.json';path.write_text(json.dumps(profile))
            result=subprocess.run([sys.executable,str(root/'tools/offline_kit.py'),'prepare','--manifest',str(path),'--output',str(Path(temporary)/'absent/kit')],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(result.returncode,0)
            self.assertNotIn('NameError',result.stderr)
            self.assertIn('new kit directory',result.stderr)
    def test_website_software_tree_is_refused_before_metadata_or_payload_work(self):
        root=Path(__file__).resolve().parents[1]
        profile=json.loads((root/'profiles/noble-devtools-amd64/manifest.json').read_text());profile['accepted']=True
        with tempfile.TemporaryDirectory() as temporary,patch.object(Path,'resolve',return_value=Path('/opt/tehnet-software/private/kit')),patch('tools.offline_kit.verified_release',side_effect=AssertionError('Reached metadata work')):
            with self.assertRaisesRegex(ValueError,'website'):prepare(profile,Path(temporary)/'kit')
    def test_total_deadline_aborts_real_tls_connection_close_trickle(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200);self.send_header('Content-Length','40');self.send_header('Connection','close');self.end_headers()
                try:
                    for _ in range(40):self.wfile.write(b'x');self.wfile.flush();time.sleep(.04)
                except (OSError,ssl.SSLError):pass
            def log_message(self,*args):pass
        fixtures=Path(__file__).resolve().parents[1]/'fixtures/tls'
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(fixtures/'server.pem',fixtures/'server.key')
        client_context=ssl.create_default_context(cafile=fixtures/'ca.pem')
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.socket=context.wrap_socket(server.socket,server_side=True)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        timer=threading.Timer;connect=socket.create_connection
        try:
            with tempfile.TemporaryDirectory() as temp,patch('tools.offline_kit.validated_mirror_target',return_value=(urlsplit('https://mirror.test/fixture'),'127.0.0.1')),patch('tools.offline_kit.ssl.create_default_context',return_value=client_context),patch('tools.offline_kit.socket.create_connection',side_effect=lambda address,timeout:connect(('127.0.0.1',server.server_port),timeout=timeout)),patch('tools.offline_kit.threading.Timer',side_effect=lambda seconds,callback:timer(.25,callback)):
                start=time.monotonic()
                with self.assertRaises((OSError,ValueError)):download('https://mirror.test/fixture',Path(temp)/'fixture',40,hashlib.sha256(b'x'*40).hexdigest())
                self.assertLess(time.monotonic()-start,.9)
        finally:server.shutdown();server.server_close();thread.join(timeout=2)
