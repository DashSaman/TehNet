"""Regression gates for the approved TehNet visual refresh; standard library only."""
import pathlib,re,unittest,base64,html,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
THEME=ROOT/'site/themes/tehnet'
class RefreshTests(unittest.TestCase):
 def text(self,path):
  p=ROOT/path
  self.assertTrue(p.is_file(),f'Missing deliverable: {path}')
  return p.read_text()
 def test_design_tokens(self):
  s=self.text('site/themes/tehnet/assets/css/visual-refresh.css')
  for color in ['#080f18','#101c29','#79e7f7','#33c9ee']:
   self.assertIn(color,s)
  self.assertIn('prefers-reduced-motion',s)
 def test_accessible_navigation(self):
  s=self.text('site/themes/tehnet/header.php')
  self.assertIn('tn-menu-toggle',s);self.assertIn('aria-expanded="false"',s)
  self.assertIn('aria-controls="tn-main-menu"',s);self.assertIn('wp_head()',s)
  self.assertNotIn('onclick=',s)
 def test_native_profile(self):
  s=self.text('content/pages/amirreza-golavar.html')
  self.assertEqual(len(re.findall(r'<h1\b',s)),1)
  for value in ['امیررضا','گل‌آور','MyTel','رایان نیک تجهیز','چاپ پازل','فتوتایپ','۱۳۹۴','MTCNA']:
   self.assertIn(value,s)
  p=self.text('site/themes/tehnet/page-portfolio.php')
  self.assertIn('the_content()',p);self.assertIn('wp_footer()',p)
 def test_home_preserves_journeys(self):
  s=self.text('content/pages/home.html')
  for url in ['/learn/','/lab/','/services/','/shop/','/amirreza-golavar/']:
   self.assertIn(url,s)
  self.assertIn('network-art',s);self.assertEqual(len(re.findall(r'<h1\b',s)),1)
  self.assertIn('<!-- wp:columns',s)
 def test_public_privacy(self):
  paths=[ROOT/'content/pages/amirreza-golavar.html',THEME/'assets/profile/Amirreza-Golavar-Resume.txt',THEME/'assets/profile/Amirreza-Golavar.vcf']
  trans=str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789')
  for p in paths:
   self.assertTrue(p.is_file(),str(p))
   s=html.unescape(p.read_text()).translate(trans)
   self.assertNotRegex(s,r'(?i)pv[\s_-]*network|پیوی|پی‌وی|پیوینتورک')
   self.assertNotRegex(s,r'(?<!\d)(?:\+?98|0098|0)9[0-9]{9}(?!\d)')
   self.assertNotRegex(s,r'(?im)\btel:|^TEL[;:]')
 def test_js_no_secret_or_tracking(self):
  s=self.text('site/themes/tehnet/assets/js/visual-refresh.js')
  self.assertIn('localStorage',s);self.assertIn('Escape',s)
  self.assertIn('beforeprint',s);self.assertNotIn('fetch(',s)
 def test_svg_valid(self):
  import xml.etree.ElementTree as ET
  p=THEME/'assets/img/network-art.svg';self.assertTrue(p.is_file())
  root=ET.fromstring(p.read_text());self.assertEqual(root.attrib.get('viewBox'),'0 0 640 560')
if __name__=='__main__':unittest.main(verbosity=2)
