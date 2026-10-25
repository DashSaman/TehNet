from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib,inspect,json,os,unittest

@unittest.skipUnless(os.name=='posix','Native publication uses flock/symlink')
class PublicationPointerTests(unittest.TestCase):
    def test_crash_reconciliation_uses_actual_old_route_and_repairs_real_pointer(self):
        from tools.offline_refresh import reconcile_pending
        from tools.offline_publication import set_current
        with TemporaryDirectory() as temp:
            root=Path(temp);old=root/'old';new=root/'new';old.mkdir();new.mkdir();pointer=root/'current'
            set_current(pointer,new)
            snippet=root/'snippet';snippet.write_bytes(b'old routes');before=root/'before';before.write_bytes(b'old routes')
            pending={'before_file':str(before),'old_sha256':hashlib.sha256(b'old routes').hexdigest(),'new_sha256':hashlib.sha256(b'new routes').hexdigest(),'public':str(new),'previous_public':str(old)}
            checked=[]
            result=reconcile_pending({'pending':pending},snippet,check=checked.append,reload=lambda:None,sync=lambda target:set_current(pointer,target))
            self.assertEqual(checked,[str(old)])
            self.assertEqual(pointer.resolve(),old)
            self.assertIsNone(result['pending'])

    def test_candidate_pointer_is_changed_before_nginx_and_old_pointer_restored_on_failure(self):
        from tools import offline_publication as publication
        self.assertIn('current_pointer',inspect.signature(publication.publish).parameters,'Publication must invalidate prior provider acceptance before route change')
        with TemporaryDirectory() as temp:
            root=Path(temp);source=root/'source';source.mkdir();public=root/'public'/'new';public.parent.mkdir();previous=public.parent/'old';previous.mkdir()
            raw=b'{"accepted":true,"id":"noble-devtools-amd64"}'
            for name in publication.FILES:(source/name).write_text('code')
            (source/'profile.json').write_bytes(raw);(source/'acceptance.json').write_text(json.dumps({'offline_install_pass':True,'profile_sha256':hashlib.sha256(raw).hexdigest()}))
            snippet=root/'snippet';snippet.write_bytes(publication.BASE.read_bytes().replace(b'\r\n',b'\n')+b'\n# routes\n')
            events=[]
            def pointer(path,target):events.append(('pointer',target))
            def run(*args):
                events.append(('command',args))
                if args==('systemctl','reload','nginx') and len([e for e in events if e[0]=='command'])==2:raise RuntimeError('injected')
            with patch.object(publication,'routes',return_value='\n# routes\n'),patch.object(publication,'set_current',side_effect=pointer,create=True):
                with self.assertRaisesRegex(RuntimeError,'prior snippet restored'):
                    publication.publish(source,snippet,public,root/'backup',previous_public=previous,current_pointer=public.parent/'current',run=run)
            self.assertEqual(events[0],('pointer',public))
            self.assertEqual([e for e in events if e[0]=='pointer'],[('pointer',public),('pointer',previous)])

if __name__=='__main__':unittest.main()
