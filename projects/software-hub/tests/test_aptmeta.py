from datetime import datetime,timezone,timedelta
import hashlib,lzma,unittest
from tools.offline_kit import parse_release,verified_index_records,validate_package

NOW=datetime(2026,10,18,16,tzinfo=timezone.utc)
TEXT=b'Package: jq\nVersion: 1.7.1-1\nArchitecture: amd64\nFilename: pool/main/j/jq/jq_1.7.1-1_amd64.deb\nSize: 5\nSHA256: '+hashlib.sha256(b'hello').hexdigest().encode()+b'\n\n'
def release(date='Sun, 18 Oct 2026 15:00:00 UTC',extra=''):
    compressed=lzma.compress(TEXT)
    return 'Origin: Ubuntu\nLabel: Ubuntu\nSuite: noble-updates\nCodename: noble\nDate: '+date+'\n'+extra+'SHA256:\n '+hashlib.sha256(TEXT).hexdigest()+' '+str(len(TEXT))+' main/binary-amd64/Packages\n '+hashlib.sha256(compressed).hexdigest()+' '+str(len(compressed))+' main/binary-amd64/Packages.xz\n'

class AptMetadataTests(unittest.TestCase):
    def test_valid_release_date_suite_and_exact_index_chain(self):
        meta=parse_release(release(),now=NOW)
        records=verified_index_records(lzma.compress(TEXT),meta,'main/binary-amd64/Packages.xz')
        self.assertEqual(records[0]['Package'],'jq')
        self.assertEqual(validate_package(records[0])['sha256'],hashlib.sha256(b'hello').hexdigest())
    def test_expired_future_stale_wrong_origin_and_signed_date_rollback_refused(self):
        for text in [release(extra='Valid-Until: Sun, 18 Oct 2026 15:30:00 UTC\n'),release(date='Mon, 19 Oct 2026 15:00:00 UTC'),release(date='Thu, 15 Oct 2026 15:00:00 UTC'),release().replace('Origin: Ubuntu','Origin: other')]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):parse_release(text,now=NOW)
        with self.assertRaisesRegex(ValueError,'rollback'):parse_release(release(),now=NOW,minimum_date=NOW)
    def test_altered_index_and_xz_bomb_refused(self):
        with self.assertRaises(ValueError):verified_index_records(lzma.compress(TEXT+b'bad'),parse_release(release(),now=NOW),'main/binary-amd64/Packages.xz')
        with self.assertRaisesRegex(ValueError,'expansion'):verified_index_records(lzma.compress(TEXT),parse_release(release(),now=NOW),'main/binary-amd64/Packages.xz',expanded_cap=20)
    def test_path_duplicate_field_and_package_metadata_conflicts_refused(self):
        record={'Package':'jq','Version':'1.7.1-1','Architecture':'amd64','Filename':'pool/../../etc/passwd','SHA256':'a'*64,'Size':'5'}
        with self.assertRaises(ValueError):validate_package(record)
        with self.assertRaises(ValueError):parse_release(release()+'Suite: noble-security\n',now=NOW)
    def test_original_ubuntu_style_trailing_empty_xz_stream_is_authenticated_and_bounded(self):
        compressed=lzma.compress(TEXT)+lzma.compress(b'');meta=parse_release(release(),now=NOW)
        meta['indices']['main/binary-amd64/Packages.xz']={'sha256':hashlib.sha256(compressed).hexdigest(),'size':len(compressed)}
        self.assertEqual(len(verified_index_records(compressed,meta,'main/binary-amd64/Packages.xz')),1)
        with self.assertRaisesRegex(ValueError,'expansion'):verified_index_records(compressed,meta,'main/binary-amd64/Packages.xz',expanded_cap=20)
