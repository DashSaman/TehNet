import importlib.util
from pathlib import Path
import hashlib,json,unittest

SOURCE=Path(__file__).resolve().parents[1]/'tools/publication_guard.py'
spec=importlib.util.spec_from_file_location('guard',SOURCE);guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
class PublicationGuardTests(unittest.TestCase):
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
