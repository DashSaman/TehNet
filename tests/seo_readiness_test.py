import importlib.util,json,unittest,hashlib
from pathlib import Path
s=importlib.util.spec_from_file_location("collector","tools/seo_readiness_20261108.py")
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Readiness(unittest.TestCase):
 def test_policy_stays_disabled(self):
  p=json.loads(Path("seo/readiness-2026-11-08/index-policy.json").read_text())
  self.assertEqual(p["activation"],"DISABLED_NEEDS_OWNER_APPROVAL");self.assertEqual(p["production_mutations"],0)
  self.assertIn("/checkout/",p["exceptions"]);self.assertIn("/my-account/",p["exceptions"])
 def test_header_parser_preserves_multiple_directives(self):
  p=m.Head();p.feed('<meta name="robots" content="noindex,nofollow"><meta name="googlebot" content="nosnippet"><link rel="canonical" href="https://tehnet.ir/"><h1>x</h1>')
  self.assertEqual(len(p.robots),2);self.assertEqual(p.h1,1);self.assertEqual(p.canonicals,["https://tehnet.ir/"])
 def test_redirect_rejects_external_and_plaintext(self):
  for u in ("https://example.invalid/","http://tehnet.ir/"):
   with self.assertRaises(ValueError):m.SafeRedirect().redirect_request(None,None,302,"",{},u)
 def test_exact_bodies_and_existing_request(self):
  p=Path("content/service-readiness-2026-11-08");manifest=json.loads((p/"manifest.json").read_text())
  self.assertEqual([x["id"] for x in manifest["targets"]],[8,29]);self.assertFalse(manifest["indexability_changed"])
  for x in manifest["targets"]:
   self.assertEqual(hashlib.sha256((p/x["content_file"]).read_bytes()).hexdigest(),x["content_sha256"])
   self.assertEqual(x["change_fields"],["post_content"])
  catalog=(p/"services.html").read_text()
  for a in ("#firewall-acceptance","#monitoring-acceptance","[tn_service_request]"):self.assertIn(a,catalog)
  hub=(p/"network-tehran.html").read_text()
  self.assertIn("general-network#service-request",hub);self.assertIn("https://mytel.one/services/",hub)
if __name__=="__main__":unittest.main(verbosity=2)
