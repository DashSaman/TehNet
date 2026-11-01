import importlib.util
from pathlib import Path
import contextlib,hashlib,io,json,os,subprocess,sys,tempfile,unittest
from unittest import mock

SOURCE=Path(__file__).resolve().parents[1]/'tools/publication_guard.py'
spec=importlib.util.spec_from_file_location('guard',SOURCE);guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
class PublicationGuardTests(unittest.TestCase):
    def run_guard(self,root):
        output=io.StringIO()
        with mock.patch.object(sys,'argv',['guard','--root',str(root)]),contextlib.redirect_stdout(output):
            result=guard.main()
        return result,json.loads(output.getvalue())
    def tracked_fixture(self,root,name='note.txt'):
        (root/'.publication-policy.json').write_text('{}',encoding='utf-8')
        (root/name).write_text('ordinary public text',encoding='utf-8')
        subprocess.run(['git','init','-q',str(root)],capture_output=True,check=True)
        subprocess.run(['git','-C',str(root),'add','.'],capture_output=True,check=True)
    def test_missing_tracked_file_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix='guard-coverage-')as directory:
            root=Path(directory);self.tracked_fixture(root);(root/'note.txt').unlink()
            result,receipt=self.run_guard(root)
            self.assertTrue(result);self.assertEqual(receipt['status'],'FAIL')
            self.assertEqual(receipt['tracked_files'],2);self.assertEqual(receipt['checked_tracked_files'],1)
            self.assertIn({'path':'note.txt','category':'unreadable-tracked-file'},receipt['issues'])
    def test_unreadable_file_does_not_disclose_exception_text(self):
        with tempfile.TemporaryDirectory(prefix='guard-coverage-')as directory:
            root=Path(directory);self.tracked_fixture(root);original=Path.read_bytes
            def read(path):
                if path.name=='note.txt':raise PermissionError('synthetic-private-exception-fragment')
                return original(path)
            with mock.patch.object(Path,'read_bytes',read):result,receipt=self.run_guard(root)
            self.assertTrue(result);self.assertEqual(receipt['checked_tracked_files'],1)
            self.assertNotIn('synthetic-private-exception-fragment',json.dumps(receipt))
            self.assertIn({'path':'note.txt','category':'unreadable-tracked-file'},receipt['issues'])
    @unittest.skipUnless(os.name=='nt','Actual Windows extended-path behavior')
    def test_windows_long_tracked_path_is_read_and_scanned(self):
        with tempfile.TemporaryDirectory(prefix='guard-coverage-')as directory:
            root=Path(directory);self.tracked_fixture(root)
            extended=Path('\\\\?\\'+str(root.resolve()));deep=extended
            while len(str(deep/'proof.txt'))<=285:deep=deep/('segment-'+'x'*42)
            deep.mkdir(parents=True);file=deep/'proof.txt'
            try:
                file.write_text('ghp_'+'Z'*36,encoding='utf-8')
                subprocess.run(['git','-c','core.longpaths=true','-C',str(root),'add','.'],capture_output=True,check=True)
                result,receipt=self.run_guard(root)
                self.assertTrue(result);self.assertEqual(receipt['tracked_files'],3)
                self.assertEqual(receipt['checked_tracked_files'],3)
                self.assertIn('credential-format',[row['category']for row in receipt['issues']])
            finally:
                file.unlink(missing_ok=True)
                while deep!=extended:parent=deep.parent;deep.rmdir();deep=parent
    def test_secret_is_reported_without_its_value(self):
        secret='ghp_'+'X'*36
        rows=guard.inspect('file.txt',secret.encode(),{})
        self.assertTrue(rows);self.assertNotIn(secret,json.dumps(rows))
    def test_known_address_matches_even_inside_a_url_or_port(self):
        value='192.0.2.72'
        rows=guard.inspect('receipt.json',('https://'+value+':8443/').encode(),{},[value])
        self.assertEqual(rows[0]['category'],'known-sensitive-value');self.assertNotIn(value,json.dumps(rows))
    def test_private_types_and_prefixes_are_rejected(self):
        self.assertTrue(guard.inspect('backups/state.json',b'{}',{'private_prefixes':['backups/']}))
        self.assertTrue(guard.inspect('export.sql',b'-- local only',{}))
        self.assertTrue(guard.inspect('nested/.env',b'',{}))
    def test_personal_path_and_url_credentials_are_rejected(self):
        self.assertTrue(guard.inspect('test.js',('C:'+chr(92)+'Users'+chr(92)+'operator'+chr(92)+'module').encode(),{}))
        self.assertTrue(guard.inspect('test.js',('https://'+'account:secret'+'@example.invalid').encode(),{}))
    def test_disposable_key_exception_requires_exact_bytes_and_reason(self):
        raw=b'-----BEGIN '+b'PRIVATE KEY-----\nexample-only\n';path='fixture.key'
        cfg={'public_test_keys':{path:{'sha256':hashlib.sha256(raw).hexdigest(),'reason':'isolated public test identity'}}}
        self.assertEqual(guard.inspect(path,raw,cfg),[])
        self.assertTrue(guard.inspect(path,raw+b'changed',cfg))
        self.assertTrue(guard.inspect('other.key',raw,cfg))
    def test_operator_addresses_and_documentation_examples_are_distinct(self):
        cfg={'operator_documents':['runbook.md']}
        self.assertTrue(guard.inspect('runbook.md',b'Origin: 93.184.216.34',cfg))
        self.assertEqual(guard.inspect('runbook.md',b'Origin example: 192.0.2.10',cfg),[])
        self.assertEqual(guard.inspect('runbook.md',b'Origin example: 2001:db8::10',cfg),[])
    def test_approved_content_is_narrow_and_invalidated_by_any_change(self):
        raw=b'CREATE TABLE example (id INTEGER);';path='migrations/001.sql'
        cfg={'approved_content':{path:{'sha256':hashlib.sha256(raw).hexdigest(),'categories':['private-file-type'],'reason':'public schema, no data'}}}
        self.assertEqual(guard.inspect(path,raw,cfg),[])
        self.assertTrue(guard.inspect(path,raw+b'-- modified',cfg))
    def test_only_line_endings_are_normalized_for_content_exceptions(self):
        self.assertEqual(guard.content_digest(b'first\r\nsecond\r\n'),guard.content_digest(b'first\nsecond\n'))
        self.assertNotEqual(guard.content_digest(b'first\n'),guard.content_digest(b'first \n'))
    def test_password_in_plain_prose_is_detected_without_disclosure(self):
        value='NeverAReal'+'Account!142'
        text=('Password for staged accounts'+': '+value+'.').encode()
        rows=guard.inspect('handoff.md',text,{})
        self.assertTrue(rows);self.assertEqual(rows[0]['category'],'prose-password');self.assertNotIn(value,json.dumps(rows))
        self.assertEqual(guard.inspect('guide.md',b'Password: <owner-private-configuration>',{}),[])
if __name__=='__main__':unittest.main()
