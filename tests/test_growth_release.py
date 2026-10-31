"""Boundary tests; full file/content orchestration also requires an isolated native rehearsal."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'ops/release-growth-content.py'


class ReleaseBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('growth_release', SOURCE)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_bundle_member_escape_and_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'good').write_bytes(b'good')
            self.assertEqual(self.module.member(root, 'good').read_bytes(), b'good')
            for name in ('../other', '/absolute', 'a/../../other', 'a\\other'):
                with self.assertRaises((ValueError, RuntimeError)):
                    self.module.member(root, name)
            try:
                (root / 'link').symlink_to(root / 'good')
            except OSError:
                return  # Windows non-admin hosts may lack symlink privileges.
            with self.assertRaises(RuntimeError):
                self.module.member(root, 'link')

    def test_rollback_preserves_foreign_file_edit_before_any_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first, second = root / 'first', root / 'second'
            first.write_bytes(b'owned new')
            second.write_bytes(b'foreign edit')
            entries = {
                'first': {'old': self.module.digest(b'old'), 'new': self.module.digest(b'owned new')},
                'second': {'old': None, 'new': self.module.digest(b'owned new')},
            }
            with self.assertRaises(RuntimeError):
                self.module.validate_restore(root, entries)
            self.assertEqual(first.read_bytes(), b'owned new')
            self.assertEqual(second.read_bytes(), b'foreign edit')

    def test_atomic_replace_and_restore_missing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / 'nested/item'
            self.module.atomic_write(target, b'complete', 0o640, None, None)
            self.assertEqual(target.read_bytes(), b'complete')
            self.assertEqual(list(target.parent.glob('*.tmp.*')), [])
            self.module.validate_restore(root, {'nested/item': {'old': None, 'new': self.module.digest(b'complete')}})

    def test_modules_precede_loader_and_restore_loader_precedes_modules(self):
        order = self.module.FILES
        loader = 'site/mu-plugins/tehnet-technical-resources.php'
        modules = [p for p in order if '/tehnet-technical-resources/' in p]
        self.assertEqual(len(modules), 3)
        self.assertTrue(all(order.index(p) < order.index(loader) for p in modules))
        reverse = list(reversed(order))
        self.assertTrue(all(reverse.index(loader) < reverse.index(p) for p in modules))


if __name__ == '__main__':
    unittest.main()
