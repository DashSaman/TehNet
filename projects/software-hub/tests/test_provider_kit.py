from pathlib import Path
from unittest.mock import patch
import unittest
from app.provider_kit import mapped_url,validated_target,selected_transport,kit,bounded_download,request_deadline
from tools.provider_lab import render_lab

class ProviderKitTests(unittest.TestCase):
    def test_copied_old_qualification_cannot_prepare_new_profile_or_failed_source(self):
        from app import provider_kit
        self.assertTrue(hasattr(provider_kit,'require_current_qualification'),'Client must require exact current requalification before payload I/O')
        receipt={'profile_sha256':'a'*64,'providers':[{'provider':'arvan','profile_sha256':'a'*64}]}
        with self.assertRaises(ValueError):provider_kit.require_current_qualification('b'*64,'arvan',receipt)
        with self.assertRaises(ValueError):provider_kit.require_current_qualification('a'*64,'liara',receipt)
        receipt['providers'][0]['install_evidence_sha256']='b'*64
        provider_kit.require_current_qualification('a'*64,'arvan',receipt)

    def test_security_packages_stay_on_selected_liara_security_service(self):
        profile={'packages':[{'relative_path':'pool/main/x/x.deb','suite':'noble-security'}]}
        self.assertEqual(mapped_url(profile,'liara',kit.MIRROR+'pool/main/x/x.deb'),'https://linux-mirror.liara.ir/repository/ubuntu-security/pool/main/x/x.deb')
        self.assertEqual(mapped_url(profile,'liara',kit.MIRROR+'dists/noble-updates/main/binary-amd64/by-hash/SHA256/'+'a'*64),'https://linux-mirror.liara.ir/repository/ubuntu/dists/noble-updates/main/binary-amd64/by-hash/SHA256/'+'a'*64)

    def test_unlisted_archive_arbitrary_url_and_traversal_are_rejected(self):
        for url in ['https://evil.example/pool/x.deb',kit.MIRROR+'pool/main/x/missing.deb',kit.MIRROR+'../private',kit.MIRROR+'dists/noble/main/binary-amd64/by-hash/SHA256/'+'a'*64+'?secret=1']:
            with self.assertRaises(ValueError):mapped_url({'packages':[]},'linuxmirrors',url)

    def test_dns_pins_refuse_drift_and_mixed_private_addresses(self):
        url='https://repo.linuxmirrors.ir/ubuntu/pool/main/x/x.deb'
        self.assertEqual(validated_target('linuxmirrors',url,addresses=['65.109.176.185'])[1],'65.109.176.185')
        for addresses in [['1.1.1.1'],['65.109.176.185','127.0.0.1'],[]]:
            with self.assertRaises(ValueError):validated_target('linuxmirrors',url,addresses=addresses)

    def test_nonapproved_choices_fail_before_any_download(self):
        with patch('app.provider_kit.QUALIFIED_SOURCES',()):
            with patch.object(kit,'validate_profile'):
                with self.assertRaises(ValueError):
                    with selected_transport({'packages':[]},'linuxmirrors'):pass

    def test_selected_provider_uses_original_hash_verifier_and_restores_globals(self):
        profile={'packages':[{'relative_path':'pool/main/x/x.deb','suite':'noble'}]}
        original_validator=kit.validated_mirror_target
        with patch.object(kit,'validate_profile'),patch.object(kit,'download') as original:
            with selected_transport(profile,'hamravesh',allow_candidate=True):
                kit.download(kit.MIRROR+'pool/main/x/x.deb',Path('fixture'),10,'a'*64)
            original.assert_called_once_with('https://repo.hmirror.ir/ubuntu/pool/main/x/x.deb',Path('fixture'),10,'a'*64)
        self.assertIs(kit.validated_mirror_target,original_validator)

    def test_provider_lab_preserves_ram_isolation_and_all_negative_install_cases(self):
        root=Path(__file__).resolve().parents[1]
        lab=render_lab((root/'deployment/qualification/run-devtools-lab.sh').read_text())
        for fragment in ['mount -t tmpfs -o noswap','unshare --net --pid','offline-corrupted-dependency','offline-missing-dependency','offline-forged-signature','offline-newer-dependency','offline-clean-install','selected_transport','provider-downloads.json']:
            self.assertIn(fragment,lab)
        with self.assertRaises(ValueError):render_lab('unreviewed shell')

    def test_size_aware_deadline_allows_large_index_but_is_finite(self):
        self.assertEqual(request_deadline(15037908),240)
        self.assertEqual(request_deadline(1),30)
        self.assertEqual(request_deadline(128*1024**2),300)

    def test_slow_source_reader_requires_complete_exact_bytes_and_refuses_redirect(self):
        import hashlib
        from tempfile import TemporaryDirectory
        from urllib.parse import urlsplit
        class Connection:
            sock=None
            def __init__(self,body,status=200):self.body=body;self.status=status
            def request(self,*args,**kwargs):pass
            def getresponse(self):return self
            def getheader(self,name,default=None):return str(len(self.body)) if name=='Content-Length' else default
            def read1(self,size):raw=self.body;self.body=b'';return raw
            def close(self):pass
        url='https://repo.linuxmirrors.ir/ubuntu/pool/main/x/x.deb'
        with TemporaryDirectory() as temp,patch('app.provider_kit.validated_target',return_value=(urlsplit(url),'65.109.176.185')):
            good=b'correct';digest=hashlib.sha256(good).hexdigest()
            bounded_download('linuxmirrors',url,Path(temp)/'good',len(good),digest,connection_factory=lambda *a:Connection(good))
            for label,body,status in [('corrupt',b'corrupt',200),('redirect',good,307)]:
                with self.assertRaises(ValueError):bounded_download('linuxmirrors',url,Path(temp)/label,len(good),digest,connection_factory=lambda *a:Connection(body,status))

if __name__=='__main__':unittest.main()
