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

    def test_routing_scope_is_separate_and_cannot_write_runtime(self):
        scope = self.module.ROUTING_SCOPE
        files, extra, runtime = self.module.scope_spec(scope)
        self.assertEqual(files, [])
        self.assertEqual(extra, ['content/routing-editorial-2026-11-01/manifest.json', 'content/routing-editorial-2026-11-01/static-routing.html', 'ops/migrate-growth-content.php'])
        self.assertEqual(set(runtime), set(self.module.FILES + ['site/plugins/tehnet-store/tehnet-store.php']))
        # The same immutable commit can carry both lessons without sharing journals.
        prefixes = [row[2] for row in self.module.LESSON_SCOPES.values()]
        self.assertEqual(len(set(prefixes)), len(prefixes))

    def test_metadata_scope_writes_only_its_file_and_has_no_content_migrator(self):
        files, extra, runtime = self.module.scope_spec(self.module.METADATA_SCOPE)
        self.assertEqual(files, ['site/mu-plugins/tehnet-search-metadata.php'])
        self.assertEqual(extra, ['content/metadata-role-2026-11-01/manifest.json', 'ops/check-metadata-state.php'])
        self.assertNotIn(files[0], runtime)
        self.assertEqual(len(runtime), 7)
        self.assertNotIn('ops/migrate-growth-content.php', extra)

    def test_metadata_runtime_guard_is_independent_of_owned_file_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = self.module.Release.__new__(self.module.Release)
            release.root = root
            protected = root / 'mu-plugins/protected.php'; protected.parent.mkdir(); protected.write_bytes(b'baseline')
            release.m = {'runtime_guard': {'site/mu-plugins/protected.php': self.module.digest(b'baseline')}}
            release.runtime_guard()
            protected.write_bytes(b'foreign edit')
            with self.assertRaises(RuntimeError):
                release.runtime_guard()
            self.assertEqual(protected.read_bytes(), b'foreign edit')

    def test_routing_bundle_uses_only_its_committed_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); repo = root / 'repo'; repo.mkdir()
            scope = self.module.ROUTING_SCOPE
            files, extra, runtime = self.module.scope_spec(scope)
            for name in set(extra + runtime + ['ops/release-growth-content.py']):
                file = repo / name; file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(b'committed routing fixture\n')
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=repo, stderr=subprocess.DEVNULL).decode().strip()
            git('init'); git('add', '.'); git('-c', 'user.name=QA', '-c', 'user.email=qa@example.invalid', 'commit', '-m', 'fixture')
            commit = git('rev-parse', 'HEAD')
            (repo / extra[1]).write_bytes(b'unreviewed working tree')
            result = self.module.build_bundle(repo, root / 'bundle', commit, commit, scope)
            import json
            metadata = json.loads((root / 'bundle/bundle.json').read_text())
            self.assertEqual(result['files'], 0)
            self.assertEqual(metadata['files'], {})
            self.assertEqual(set(metadata['members']), set(extra))
            self.assertEqual((root / 'bundle/payload' / extra[1]).read_bytes(), b'committed routing fixture\n')

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
