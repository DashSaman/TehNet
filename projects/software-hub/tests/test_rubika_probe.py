import contextlib,hashlib,io,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools.rubika_probe import read_token,set_token,probe,endpoint,ProbeRejected,main,FIXTURE,Transport as RealTransport

TOKEN='TEST_ONLY_not_a_real_rubika_token_123456'
class Transport:
    def __init__(self,upload='https://upload.rubika.ir/test?secret=private',download='https://download.rubika.ir/test?secret=private'):
        self.calls=[];self.upload=upload;self.download=download
    def request(self,url,method='POST',body=b'',headers=None,allowed_hosts=()):
        self.calls.append((url,method,body))
        if url.endswith('/getMe'):data={'bot':{'bot_id':'PRIVATE-BOT'}}
        elif url.endswith('/requestSendFile'):data={'upload_url':self.upload}
        elif url.endswith('/getFile'):data={'download_url':self.download}
        elif method=='POST':
            assert FIXTURE in body;data={'file_id':'PRIVATE-FILE'}
        elif method=='HEAD':return 200,{'content-length':str(len(FIXTURE))},b''
        elif headers and 'Range' in headers:return 206,{'content-range':f'bytes 0-15/{len(FIXTURE)}'},FIXTURE[:16]
        else:return 200,{},FIXTURE
        return 200,{},json.dumps({'status':'OK','data':data}).encode()

class RubikaProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'token';self.path.parent.chmod(0o700)
    def test_hidden_setup_roundtrip_and_mismatch_preserves_previous_secret(self):
        set_token(self.path,TOKEN,TOKEN);self.assertEqual(read_token(self.path),TOKEN)
        with self.assertRaises(ProbeRejected):set_token(self.path,TOKEN,'mismatch')
        self.assertEqual(read_token(self.path),TOKEN)
        if os.name=='posix':self.assertEqual(self.path.stat().st_mode&0o777,0o600)
    def test_noninteractive_setup_is_refused_before_prompt_or_file(self):
        with patch('sys.stdin.isatty',return_value=False),patch('tools.rubika_probe.getpass.getpass',side_effect=AssertionError('must not prompt')):
            self.assertEqual(main(['set-token','--token-file',str(self.path)]),2)
        self.assertFalse(self.path.exists())
    def test_unsafe_endpoint_is_rejected_before_network(self):
        for url in ['http://upload.rubika.ir/file','https://user:pw@upload.rubika.ir/file','https://upload.rubika.ir:444/file','https://evil.invalid/file','https://upload.rubika.ir/file#secret','https://upload.rubika.ir/x\r\nHeader:bad']:
            with self.assertRaises(ProbeRejected):endpoint(url,{'upload.rubika.ir'})
    def test_unknown_returned_upload_host_stops_before_any_upload(self):
        t=Transport(upload='https://evil.invalid/private?bearer=secret')
        report,private=probe(TOKEN,t,upload_hosts=set(),download_hosts=set(),roundtrip=True)
        self.assertEqual(report['state'],'UPLOAD_HOST_REVIEW_REQUIRED');self.assertEqual(len(t.calls),2)
        self.assertNotIn('bearer',json.dumps(report));self.assertNotIn(TOKEN,json.dumps(report));self.assertEqual(private,{})
    def test_in_memory_roundtrip_checks_hash_head_range_without_public_identity_or_links(self):
        t=Transport()
        with patch('tempfile.mkstemp',side_effect=AssertionError('payload file')):
            report,private=probe(TOKEN,t,upload_hosts={'upload.rubika.ir'},download_hosts={'download.rubika.ir'},roundtrip=True)
        self.assertEqual(report['state'],'FIXTURE_ROUNDTRIP_PASS');self.assertTrue(report['range_verified'])
        public=json.dumps(report)
        for secret in [TOKEN,'PRIVATE-BOT','PRIVATE-FILE','?secret=private']:self.assertNotIn(secret,public)
        self.assertEqual(private['file_id'],'PRIVATE-FILE');self.assertEqual(report['sha256'],hashlib.sha256(FIXTURE).hexdigest())
    def test_private_or_symlink_token_file_is_not_followed(self):
        set_token(self.path,TOKEN,TOKEN)
        if os.name=='posix':
            self.path.chmod(0o644)
            with self.assertRaises(ProbeRejected):read_token(self.path)
            self.path.chmod(0o600)
            alias=self.path.parent/'alias';alias.symlink_to(self.path)
            with self.assertRaises(ProbeRejected):read_token(alias)
    def test_retention_recheck_reuses_private_identity_without_upload_or_message(self):
        t=Transport();old={'file_id':'PRIVATE-FILE','created_at_utc':'2026-10-17T00:00:00+00:00'}
        report,private=probe(TOKEN,t,upload_hosts=set(),download_hosts={'download.rubika.ir'},roundtrip=True,existing=old)
        self.assertEqual(private,old);self.assertEqual(report['created_at_utc'],old['created_at_utc'])
        self.assertFalse(any('/requestSendFile' in url or '/sendMessage' in url or '/sendFile' in url for url,_,_ in t.calls))
    def test_invalid_retention_record_never_silently_creates_new_upload(self):
        for record in [{},{'file_id':'PRIVATE-FILE','created_at_utc':'not-a-date'}]:
            t=Transport()
            with self.assertRaises(ProbeRejected):probe(TOKEN,t,upload_hosts={'upload.rubika.ir'},download_hosts={'download.rubika.ir'},roundtrip=True,existing=record)
            self.assertFalse(any('/requestSendFile' in url for url,_,_ in t.calls))
    def test_cli_suppresses_untrusted_exception_text_containing_secret(self):
        set_token(self.path,TOKEN,TOKEN);out=io.StringIO();err=io.StringIO()
        with patch('tools.rubika_probe.probe',side_effect=RuntimeError(TOKEN+' private-url')),contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            self.assertEqual(main(['check','--token-file',str(self.path)]),2)
        self.assertNotIn(TOKEN,out.getvalue()+err.getvalue());self.assertNotIn('private-url',out.getvalue()+err.getvalue())
    def test_transport_rejects_internal_dns_before_connection(self):
        with patch('tools.rubika_probe.validate_target',side_effect=ValueError('private DNS')),patch('tools.rubika_probe.PinnedHTTPSConnection') as connection:
            with self.assertRaises(ProbeRejected):RealTransport().request('https://upload.rubika.ir/file',allowed_hosts={'upload.rubika.ir'})
            connection.assert_not_called()
    def test_transport_does_not_follow_redirect_or_read_oversized_body(self):
        class Reply:
            status=302
            def close(self):pass
            def getheader(self,k,d=None):return d
            def getheaders(self):return []
            def read1(self,n):return b'x'*n
        class Connection:
            sock=None
            def request(self,*a,**k):pass
            def getresponse(self):return Reply()
            def close(self):pass
        for code in [302,200]:
            Reply.status=code
            with patch('tools.rubika_probe.validate_target',return_value=object()),patch('tools.rubika_probe.PinnedHTTPSConnection',return_value=Connection()):
                with self.assertRaises(ProbeRejected):RealTransport().request('https://upload.rubika.ir/file',allowed_hosts={'upload.rubika.ir'})
    def test_token_setup_rejects_private_directory_elsewhere_in_repository(self):
        repo=self.path.parent/'fixture-repository';(repo/'.git').mkdir(parents=True)
        with self.assertRaises(Exception):set_token(repo/'private/token',TOKEN,TOKEN)
        self.assertFalse((repo/'private/token').exists())
    def test_host_discovery_redacts_normalized_token_and_private_file_id(self):
        token='ABCDEF1234567890'
        t=Transport(upload='https://'+token+'.rubika.ir/test')
        report,_=probe(token,t,upload_hosts=set(),download_hosts=set(),roundtrip=True)
        self.assertNotIn(token.lower(),json.dumps(report).lower())
        t=Transport(download='https://'+token+'.PRIVATE-FILE.rubika.ir/test')
        report,_=probe(token,t,upload_hosts={'upload.rubika.ir'},download_hosts=set(),roundtrip=True)
        for secret in [token,'PRIVATE-FILE']:self.assertNotIn(secret.lower(),json.dumps(report).lower())
