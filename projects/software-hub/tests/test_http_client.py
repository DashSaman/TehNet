import hashlib
from pathlib import Path
import tempfile
import unittest
from app.http_client import GuardedClient,FetchRejected
from app.health import NetworkBudget
from app.models import SourceConfig,Artifact

BODY=b'\x00verified software fixture bytes\n'
def artifact():return Artifact(sha256=hashlib.sha256(BODY).hexdigest(),size_bytes=len(BODY),name='test',version='1',architecture='all',filename='fixture.bin')
class Reply:
    def __init__(self,body=BODY,status=200,headers=None):
        self.body=body;self.status=status;self.headers={'content-length':str(len(body)),**(headers or {})};self.position=0
    def getheader(self,name,default=None):return self.headers.get(name.lower(),default)
    def read1(self,count):
        data=self.body[self.position:self.position+count];self.position+=len(data);return data
    def close(self):pass
class Connection:
    sock=None
    def __init__(self,reply):self.reply=reply;self.calls=[];self.closed=False
    def request(self,*args,**kwargs):self.calls.append((args,kwargs))
    def getresponse(self):return self.reply
    def close(self):self.closed=True

class FetchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.now=1000000.
        self.budget=NetworkBudget(self.root/'budget.sqlite',clock=lambda:self.now);self.budget.initialize()
        self.source=SourceConfig(id='fixture',provider='fixture',ecosystem='generic',base_url='https://mirror.example/kit/',allowed_hosts=('mirror.example',),routing_enabled=True,permission_state='approved',domestic_state='verified',approval_evidence='test fixture, not a production provider')
    def client(self,reply):
        self.connection=Connection(reply)
        return GuardedClient(self.budget,resolver=lambda *args:['93.184.216.34'],connection_factory=lambda *a:self.connection)
    def test_full_stream_requires_exact_hash_and_size_without_publish(self):
        path=self.root/'file';r=self.client(Reply()).verify_remote(self.source,'fixture.bin',artifact())
        self.assertFalse(path.exists());self.assertTrue(r.full_hash_verified)
        self.assertEqual(r.state,'present_verified');self.assertTrue(self.connection.closed)
    def test_bad_hash_size_oversize_html_and_encoding_rejected_without_files(self):
        for reply in [Reply(b'bad'),Reply(BODY+b'extra'),Reply(b'<html>error</html>'),Reply(BODY,headers={'content-encoding':'gzip'}),Reply(b'x'*len(BODY))]:
            with self.subTest(reply=reply):
                self.now+=301
                path=self.root/'rejected'
                with self.assertRaises(FetchRejected):self.client(reply).verify_remote(self.source,'fixture.bin',artifact())
                self.assertFalse(path.exists());self.assertEqual(list(self.root.glob('.fetch-*')),[])
    def test_redirect_denied_without_following_or_credential_forwarding(self):
        with self.assertRaises(FetchRejected):self.client(Reply(status=302,headers={'location':'https://evil.invalid/'})).verify_remote(self.source,'fixture.bin',artifact())
        self.assertEqual(len(self.connection.calls),1)
        headers=self.connection.calls[0][1]['headers']
        self.assertNotIn('Authorization',headers);self.assertNotIn('Cookie',headers)
    def test_disabled_source_and_maintenance_do_no_network_work(self):
        client=self.client(Reply())
        with self.assertRaises(FetchRejected):client.verify_remote(self.source.model_copy(update={'routing_enabled':False}),'fixture.bin',artifact())
        self.assertEqual(self.connection.calls,[])
        client.mode='MAINTENANCE'
        with self.assertRaises(FetchRejected):client.verify_remote(self.source,'fixture.bin',artifact())
    def test_sample_hash_never_counts_as_full_and_range_ignored_is_capped(self):
        reply=Reply(b'x'*10000)
        result=self.client(reply).probe(self.source,'fixture.bin',artifact())
        self.assertFalse(result.full_hash_verified);self.assertEqual(result.observation.body_bytes,4096)
        self.assertEqual(reply.position,4096);self.assertEqual(result.state,'present_unverified')
    def test_range_mismatch_and_retryable_status_are_unknown_not_absent(self):
        for reply in [Reply(status=206,headers={'content-range':'bytes 1-30/32'}),Reply(status=403),Reply(status=429,headers={'retry-after':'120'}),Reply(status=503)]:
            self.now+=301
            self.assertEqual(self.client(reply).probe(self.source,'fixture.bin',artifact()).state,'unknown')
        self.now+=301
        self.assertEqual(self.client(Reply(status=404)).probe(self.source,'fixture.bin',artifact()).state,'absent')
    def test_hostile_numeric_headers_are_rejected_without_unbounded_integer_parse(self):
        result=self.client(Reply(headers={'content-length':'9'*10000})).probe(self.source,'fixture.bin',artifact())
        self.assertEqual(result.state,'unknown')
