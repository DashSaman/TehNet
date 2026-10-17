from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from contextlib import closing
from pathlib import Path
import socket
import ssl
import threading
import time
import tempfile
import hashlib
import unittest
from unittest.mock import patch
from app.http_client import PinnedHTTPSConnection,GuardedClient,FetchRejected
from app.health import NetworkBudget
from app.models import ValidatedTarget,ProbeBudget,SourceConfig,Artifact

FIXTURE=Path(__file__).resolve().parents[1]/'fixtures/tls'

class TLSTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.names=[];cls.hosts=[]
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path=='/slow':
                    try:
                        self.wfile.write(b'HTTP/1.1 200 OK\r\nX-Slow: ');self.wfile.flush()
                        for _ in range(15):time.sleep(.2);self.wfile.write(b'x');self.wfile.flush()
                    except (OSError,ssl.SSLError):pass
                    return
                cls.hosts.append(self.headers['Host']);self.send_response(200);self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'OK')
            def log_message(self,*args):pass
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(FIXTURE/'server.pem',FIXTURE/'server.key')
        context.set_servername_callback(lambda sock,name,ctx:cls.names.append(name))
        cls.server.socket=context.wrap_socket(cls.server.socket,server_side=True)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=2)
    def connection(self,name='mirror.test',context=None):
        target=ValidatedTarget(url='https://'+name+'/',hostname=name,connected_ip='127.0.0.1',port=self.server.server_port)
        return PinnedHTTPSConnection(target,2,context=context or ssl.create_default_context(cafile=FIXTURE/'ca.pem'))
    def test_real_tls_uses_numeric_connection_and_original_host_sni(self):
        original=socket.getaddrinfo;lookups=[]
        def checked(host,*args,**kwargs):
            lookups.append(host);self.assertEqual(host,'127.0.0.1');return original(host,*args,**kwargs)
        with patch('socket.getaddrinfo',side_effect=checked),closing(self.connection()) as connection:
            connection.request('GET','/');response=connection.getresponse();self.assertEqual(response.read(),b'OK')
        self.assertEqual(lookups,['127.0.0.1']);self.assertEqual(self.names[-1],'mirror.test')
        self.assertEqual(self.hosts[-1],'mirror.test:'+str(self.server.server_port))
    def test_wrong_hostname_cannot_be_accepted(self):
        with closing(self.connection(name='wrong.test')) as connection:
            with self.assertRaises(ssl.SSLCertVerificationError):connection.connect()
    def test_untrusted_ca_cannot_be_accepted(self):
        with closing(self.connection(context=ssl.create_default_context())) as connection:
            with self.assertRaises(ssl.SSLCertVerificationError):connection.connect()
    def test_context_that_disables_tls_verification_is_rejected(self):
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT);context.check_hostname=False;context.verify_mode=ssl.CERT_NONE
        with self.assertRaises(ValueError):self.connection(context=context)
    def guarded(self,root):
        budget=NetworkBudget(root/'budget.sqlite',ProbeBudget(timeout_seconds=1));budget.initialize()
        # Test-only mapping to the controlled loopback TLS server. Production uses the checked IP unchanged.
        def fixture_transport(target,timeout):
            mapped=target.model_copy(update={'connected_ip':'127.0.0.1','port':self.server.server_port})
            return PinnedHTTPSConnection(mapped,timeout,context=ssl.create_default_context(cafile=FIXTURE/'ca.pem'))
        source=SourceConfig(id='tls-test',provider='test-only',ecosystem='test',base_url='https://mirror.test/',allowed_hosts=('mirror.test',),routing_enabled=True,permission_state='approved',domestic_state='verified',approval_evidence='isolated TLS fixture only')
        item=Artifact(sha256=hashlib.sha256(b'OK').hexdigest(),size_bytes=2,name='fixture',version='1',architecture='all',filename='fixture.bin')
        return GuardedClient(budget,resolver=lambda *a:['93.184.216.34'],connection_factory=fixture_transport),source,item
    def test_full_verification_over_real_tls_fixture(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);client,source,item=self.guarded(root)
            result=client.verify_remote(source,'fixture',item)
            self.assertTrue(result.full_hash_verified);self.assertFalse((root/'out').exists())
    def test_deadline_interrupts_trickled_tls_headers(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);client,source,item=self.guarded(root);started=time.monotonic()
            with self.assertRaises(FetchRejected):client.verify_remote(source,'slow',item)
            self.assertLess(time.monotonic()-started,2.5);self.assertFalse((root/'out').exists())
