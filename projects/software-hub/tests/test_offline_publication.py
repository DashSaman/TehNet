import hashlib,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

@unittest.skipUnless(os.name=='posix','Linux operator uses flock')
class OfflinePublicationTests(unittest.TestCase):
    def fixture(self,temp):
        from tools import offline_publication as op
        root=Path(temp);source=root/'source';source.mkdir()
        profile=b'{"accepted":true,"id":"noble-devtools-amd64"}'
        for name in op.FILES:(source/name).write_text('public code')
        (source/'profile.json').write_bytes(profile)
        (source/'acceptance.json').write_text(json.dumps({'offline_install_pass':True,'profile_sha256':hashlib.sha256(profile).hexdigest()}))
        snippet=root/'software.conf';snippet.write_bytes(op.BASE.read_bytes().replace(b'\r\n',b'\n'))
        return source,snippet,root/'public',root/'backup'
    def test_rejects_payload_extra_unaccepted_or_proof_mismatch_before_write(self):
        from tools import offline_publication as op
        with tempfile.TemporaryDirectory() as temp:
            source,*_=self.fixture(temp)
            extra=source/'file.deb';extra.write_bytes(b'payload')
            with self.assertRaises(ValueError):op.validate_source(source)
            extra.unlink();(source/'acceptance.json').write_text('{"offline_install_pass":false}')
            with self.assertRaises(ValueError):op.validate_source(source)
    def test_failed_reload_and_failed_postcheck_restore_exact_original_and_verify_reload(self):
        from tools import offline_publication as op
        for failure in ['reload','postcheck']:
            with self.subTest(failure=failure),tempfile.TemporaryDirectory() as temp:
                source,snippet,public,backup=self.fixture(temp);old=snippet.read_bytes();calls=[]
                def run(*args):
                    calls.append(args)
                    if failure=='reload' and len(calls)==2:raise RuntimeError('injected reload failure')
                def check():raise RuntimeError('injected postcheck failure')
                with patch.object(op,'routes',return_value='\n# reviewed test routes\n'):
                    with self.assertRaisesRegex(RuntimeError,'prior snippet restored and reload verified'):op.publish(source,snippet,public,backup,run=run,check=check)
                self.assertEqual(snippet.read_bytes(),old)
                self.assertEqual(calls[-2:],[('nginx','-t'),('systemctl','reload','nginx')])
                self.assertEqual((backup/'nginx-software.before').read_bytes(),old)
    def test_exact_routes_never_serve_parent_or_payload_paths(self):
        from tools import offline_publication as op
        routes=op.routes(Path('/opt/tehnet-software/public/offline-test'))
        self.assertEqual(routes.count('location = '),4)
        self.assertNotIn('location /',routes)
        self.assertIn('no-store',routes);self.assertIn('limit_except GET',routes)
        with self.assertRaises(ValueError):op.routes(Path('/var/www'))
    def test_update_requires_exact_prior_owned_routes_and_backs_them_up(self):
        from tools import offline_publication as op
        with tempfile.TemporaryDirectory() as temp:
            source,snippet,public,backup=self.fixture(temp)
            previous=Path('/opt/tehnet-software/public/offline-previous')
            old=op.BASE.read_bytes().replace(b'\r\n',b'\n')+op.routes(previous).encode();snippet.write_bytes(old)
            original_routes=op.routes
            with patch.object(op,'routes',side_effect=lambda path:original_routes(path) if path==previous else '\n# new exact test routes\n'):
                result=op.publish(source,snippet,public,backup,run=lambda *args:None,previous_public=previous)
            self.assertEqual((backup/'nginx-software.before').read_bytes(),old)
            self.assertEqual(snippet.read_bytes(),op.BASE.read_bytes().replace(b'\r\n',b'\n')+b'\n# new exact test routes\n')
            self.assertEqual(result['software_payload_files'],0)
