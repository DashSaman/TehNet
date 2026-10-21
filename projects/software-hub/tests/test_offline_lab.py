import io,os,tarfile,tempfile,unittest
from pathlib import Path
from tools.offline_lab import extract_clean_root

class CleanRootTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def archive(self,items):
        path=self.root/'fixture.tar'
        with tarfile.open(path,'w') as out:
            for name,link,body in items:
                item=tarfile.TarInfo(name)
                if link is not None:item.type=tarfile.SYMTYPE;item.linkname=link;out.addfile(item)
                else:item.size=len(body);out.addfile(item,io.BytesIO(body))
        return path
    def test_absolute_chroot_symlink_is_converted_without_host_escape(self):
        archive=self.archive([('usr/bin/tool',None,b'fixture'),('etc/alternatives/tool','/usr/bin/tool',None)])
        target=self.root/'client';extract_clean_root(archive,target)
        self.assertEqual((target/'etc/alternatives/tool').read_bytes(),b'fixture')
        if os.name=='posix':
            self.assertTrue((target/'etc/alternatives/tool').is_symlink())
            self.assertEqual((target/'etc/alternatives/tool').resolve(),target/'usr/bin/tool')
    def test_parent_traversal_and_escaping_symlink_refused(self):
        for items in [[('../escape',None,b'bad')],[('escape','../../escape',None)]]:
            with self.subTest(items=items):
                with self.assertRaises(tarfile.FilterError):extract_clean_root(self.archive(items),self.root/'client')
        self.assertFalse((self.root/'escape').exists())
    @unittest.skipUnless(os.name=='posix','Linux archive directory permissions')
    def test_signed_baseline_directory_modes_survive_restrictive_operator_umask(self):
        path=self.root/'mode.tar'
        with tarfile.open(path,'w') as out:
            item=tarfile.TarInfo('var/lib/apt');item.type=tarfile.DIRTYPE;item.mode=0o755;out.addfile(item)
        previous=os.umask(0o077)
        try:extract_clean_root(path,self.root/'client')
        finally:os.umask(previous)
        self.assertEqual((self.root/'client/var/lib/apt').stat().st_mode&0o777,0o755)
