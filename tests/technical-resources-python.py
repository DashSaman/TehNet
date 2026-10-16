"""Independent published download arithmetic checks; not a network benchmark."""
from pathlib import Path
import runpy,unittest
f=runpy.run_path(str(Path(__file__).resolve().parents[1]/'site/mu-plugins/tehnet-technical-resources/wireguard-mtu.py.txt'))['wireguard_mtu']
class MTU(unittest.TestCase):
 def test_standard_paths(self):
  for path,ip,want in [(1500,4,1440),(1500,6,1420),(1492,4,1432),(1492,6,1412)]:
   with self.subTest(path=path,ip=ip):self.assertEqual(f(path,ip),want)
 def test_invalid_inputs(self):
  for path,ip in [(575,4),(1279,6),(9001,4),(1500,5),(1500.1,4)]:
   with self.subTest(path=path,ip=ip),self.assertRaises(ValueError):f(path,ip)
if __name__=='__main__':unittest.main(verbosity=2)
