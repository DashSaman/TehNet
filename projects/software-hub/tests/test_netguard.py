import unittest
from unittest.mock import patch
from app.netguard import validate_target,TargetRejected

class NetguardTests(unittest.TestCase):
    def target(self,base='https://mirror.example/ubuntu/',path='pool/main/file.deb',answers=('93.184.216.34',)):
        return validate_target(base,path,{'mirror.example'},resolver=lambda *args:answers)
    def test_target_pins_checked_ip_and_preserves_hostname(self):
        t=self.target();self.assertEqual(t.connected_ip,'93.184.216.34')
        self.assertEqual(t.hostname,'mirror.example');self.assertEqual(t.port,443)
        self.assertEqual(t.url,'https://mirror.example/ubuntu/pool/main/file.deb')
    def test_private_mixed_multicast_and_mapped_addresses_are_rejected(self):
        for answers in [('127.0.0.1',),('10.0.0.1',),('169.254.169.254',),('::1',),('::ffff:10.0.0.1',),('224.0.0.1',),('93.184.216.34','10.0.0.1')]:
            with self.subTest(answers=answers),self.assertRaises(TargetRejected):self.target(answers=answers)
    def test_url_credentials_hosts_ports_and_non_tls_are_rejected(self):
        for base in ['http://mirror.example/','https://user:pass@mirror.example/','https://evil.invalid/','https://mirror.example:444/','https://mirror.example./','https://mirror.example/?x=1','https://mirror.example/#x']:
            with self.subTest(base=base),self.assertRaises(TargetRejected):self.target(base=base)
    def test_relative_paths_cannot_escape_or_change_origin(self):
        for path in ['../secret','pool/../secret','/root','//evil.invalid/a','https://evil.invalid/a','a\\b','a\r\nHost: evil','%2e%2e/x','%252e%252e/x','pool/%2fsecret','a?x=1','a#x','a//b','%zz']:
            with self.subTest(path=path),self.assertRaises(TargetRejected):self.target(path=path)
    def test_empty_dns_and_resolver_failure_are_rejected(self):
        with self.assertRaises(TargetRejected):self.target(answers=())
        with self.assertRaises(TargetRejected):
            validate_target('https://mirror.example/','file',{'mirror.example'},resolver=lambda *a:(_ for _ in ()).throw(TimeoutError()))
    def test_proxy_environment_does_not_change_target(self):
        with patch.dict('os.environ',{'HTTPS_PROXY':'http://127.0.0.1:1','ALL_PROXY':'http://127.0.0.1:2'}):self.assertEqual(self.target().connected_ip,'93.184.216.34')
