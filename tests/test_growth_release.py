"""Boundary tests; full file/content orchestration also requires an isolated native rehearsal."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import subprocess

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

    def test_editorial_scope_has_zero_runtime_writes_and_fixed_inputs(self):
        files, extra, runtime = self.module.scope_spec('tehnet-editorial-routeros-20261101-v1')
        self.assertEqual(files, [])
        self.assertEqual(extra, ['content/growth-editorial-2026-11-01/manifest.json', 'content/growth-editorial-2026-11-01/routeros-winbox.html', 'ops/migrate-growth-content.php'])
        self.assertEqual(set(runtime), set(self.module.FILES + ['site/plugins/tehnet-store/tehnet-store.php']))
        with self.assertRaises(ValueError):
            self.module.scope_spec('arbitrary-pages')

    def test_editorial_bundle_ignores_uncommitted_body_and_has_no_deployable_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); repo = root / 'repo'; repo.mkdir()
            files, extra, runtime = self.module.scope_spec('tehnet-editorial-routeros-20261101-v1')
            for name in set(extra + runtime + ['ops/release-growth-content.py']):
                file = repo / name; file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(b'committed fixture\n')
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=repo, stderr=subprocess.PIPE).decode().strip()
            git('init'); git('add', '.'); git('-c', 'user.name=QA', '-c', 'user.email=qa@example.invalid', 'commit', '-m', 'fixture')
            commit = git('rev-parse', 'HEAD')
            (repo / extra[1]).write_bytes(b'unreviewed working tree')
            result = self.module.build_bundle(repo, root / 'bundle', commit, commit, 'tehnet-editorial-routeros-20261101-v1')
            import json
            metadata = json.loads((root / 'bundle/bundle.json').read_text())
            self.assertEqual(result['files'], 0)
            self.assertEqual(metadata['files'], {})
            self.assertEqual((root / 'bundle/payload' / extra[1]).read_bytes(), b'committed fixture\n')
            self.assertEqual(set(metadata['runtime_guard']), set(runtime))

    def test_content_only_guard_refuses_foreign_runtime_change_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); _, _, runtime = self.module.scope_spec('tehnet-editorial-routeros-20261101-v1')
            for name in runtime:
                file = root / name.removeprefix('site/'); file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(b'baseline')
            release = self.module.Release.__new__(self.module.Release)
            release.root = root; release.files = []
            release.m = {'files': {}, 'runtime_guard': {name: self.module.digest(b'baseline') for name in runtime}}
            release.file_guard()
            changed = root / runtime[0].removeprefix('site/'); changed.write_bytes(b'foreign code')
            with self.assertRaises(RuntimeError): release.file_guard()
            self.assertEqual(changed.read_bytes(), b'foreign code')

    def test_staging_ports_are_closed_or_explicit_loopback_only(self):
        local = {'80/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '18085'}]}
        public = {'80/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '18085'}]}
        self.assertTrue(self.module.staging_ports_safe({}))
        self.assertFalse(self.module.staging_ports_safe(local))
        self.assertTrue(self.module.staging_ports_safe(local, allow_loopback=True))
        self.assertFalse(self.module.staging_ports_safe(public, allow_loopback=True))


if __name__ == '__main__':
    unittest.main()
