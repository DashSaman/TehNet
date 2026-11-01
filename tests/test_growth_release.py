"""Boundary tests; full file/content orchestration also requires an isolated native rehearsal."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import subprocess
import os
import contextlib
import io
from unittest import mock

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

    def test_support_scope_is_exact_body_only_and_guards_current_metadata(self):
        scope = 'tehnet-service-network-support-20261101-v1'
        files, extra, runtime = self.module.scope_spec(scope)
        self.assertEqual(files, [])
        self.assertEqual(extra, ['content/network-support-2026-11-01/manifest.json', 'content/network-support-2026-11-01/network-support.html', 'ops/migrate-growth-content.php'])
        self.assertEqual(len(runtime), 8)
        self.assertIn('site/mu-plugins/tehnet-search-metadata.php', runtime)
        self.assertNotIn(scope, self.module.LESSON_SCOPES)
        self.assertIn(scope, self.module.GUARDED_SCOPES)

    def test_ip_dhcp_dns_scope_is_distinct_and_guards_current_metadata(self):
        files, extra, runtime = self.module.scope_spec('tehnet-editorial-ip-dhcp-dns-20261101-v1')
        self.assertEqual(files, [])
        self.assertEqual(extra, ['content/ip-dhcp-dns-editorial-2026-11-01/manifest.json', 'content/ip-dhcp-dns-editorial-2026-11-01/ip-dhcp-dns.html', 'ops/migrate-growth-content.php'])
        self.assertEqual(len(runtime), 8)
        self.assertIn('site/mu-plugins/tehnet-search-metadata.php', runtime)

    def test_network_setup_scope_is_body_only_current_guarded_and_separate(self):
        scope = 'tehnet-service-network-setup-20261101-v1'
        files, extra, runtime = self.module.scope_spec(scope)
        self.assertEqual(files, [])
        self.assertEqual(extra, ['content/network-setup-2026-11-01/manifest.json', 'content/network-setup-2026-11-01/network-setup.html', 'ops/migrate-growth-content.php'])
        self.assertEqual(len(runtime), 8)
        self.assertIn('site/mu-plugins/tehnet-search-metadata.php', runtime)
        self.assertNotIn(scope, self.module.LESSON_SCOPES)
        self.assertIn(scope, self.module.GUARDED_SCOPES)
        prefixes = [row[2] for row in self.module.CONTENT_SCOPES.values()]
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

    def test_relative_dot_destination_is_resolved_before_member_io(self):
        # A real relative path, not a stub: Windows counts the unresolved cwd/../
        # spelling against its relative-path limit even when the final path fits.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); repo = root / 'repo'; repo.mkdir()
            files, extra, runtime = self.module.scope_spec(self.module.SUPPORT_SCOPE)
            for name in set(extra + runtime + ['ops/release-growth-content.py']):
                file = repo / name; file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(b'committed support fixture\n')
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=repo, stderr=subprocess.PIPE).decode().strip()
            git('init'); git('add', '.'); git('-c', 'user.name=QA', '-c', 'user.email=qa@example.invalid', 'commit', '-m', 'fixture')
            commit = git('rev-parse', 'HEAD')
            # Keep the normalized absolute path short while making its lexical
            # relative spelling exceed260. Each intermediate directory exists.
            suffix = '/payload/' + extra[1]
            depth = max(4, (285 - len(str(root)) - len(suffix)) // 8)
            current = root
            for i in range(depth): current = current / ('cwd%03d' % i); current.mkdir()
            output = Path(*(['..'] * depth)) / 'bundle'
            previous = Path.cwd()
            try:
                os.chdir(current)
                self.module.build_bundle(repo, output, commit, commit, self.module.SUPPORT_SCOPE)
            finally:
                os.chdir(previous)
            self.assertTrue((root / 'bundle/bundle.json').is_file())
            self.assertEqual((root / 'bundle/payload' / extra[1]).read_bytes(), b'committed support fixture\n')

    def test_bundle_destination_cannot_adopt_existing_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); existing = root / 'existing'; existing.mkdir()
            sentinel = existing / 'foreign'; sentinel.write_bytes(b'preserve')
            for output in [existing]:
                with self.assertRaises(RuntimeError):
                    self.module.build_bundle(root, output, 'a'*40, 'b'*40, self.module.SUPPORT_SCOPE)
            self.assertEqual(sentinel.read_bytes(), b'preserve')

    def test_dangling_symlink_bundle_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); link = root / 'link'; target = root / 'uncreated'
            try: link.symlink_to(target, target_is_directory=True)
            except OSError: self.skipTest('Host lacks symlink creation permission')
            with self.assertRaises(RuntimeError):
                self.module.build_bundle(root, link, 'a'*40, 'b'*40, self.module.SUPPORT_SCOPE)
            self.assertFalse(target.exists())

    def test_private_diagnostics_reject_relative_repository_and_webroot(self):
        with self.assertRaises(RuntimeError): self.module.private_diagnostics_directory(Path('relative'))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            for marker in ['.git', 'wp-config.php']:
                (root / marker).write_text('owned fixture')
                with self.assertRaises(RuntimeError): self.module.private_diagnostics_directory(root)
                (root / marker).unlink()

    def test_failure_detail_is_saved_privately_and_not_printed(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp).resolve()
            sentinel = 'SYNTHETIC-SECRET-SHOULD-STAY-IN-PRIVATE-LOG'
            stdout = io.StringIO(); stderr = io.StringIO()
            args = ['release', '--mode', 'bundle', '--bundle', str(directory / 'bundle'),
                    '--source-commit', 'a'*40, '--baseline-commit', 'b'*40, '--diagnostics-dir', str(directory)]
            with mock.patch('sys.argv', args), mock.patch.object(self.module, 'build_bundle', side_effect=RuntimeError(sentinel)), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = self.module.main()
            self.assertEqual(code, 1)
            import json
            public = json.loads(stdout.getvalue())
            self.assertEqual(public['phase'], 'bundle')
            self.assertEqual(public['error_type'], 'RuntimeError')
            self.assertTrue(public['private_diagnostics_saved'])
            self.assertNotIn(sentinel, stdout.getvalue() + stderr.getvalue())
            files = list(directory.glob('failure-*.log')); self.assertEqual(len(files), 1)
            self.assertIn(sentinel, files[0].read_text(encoding='utf-8'))
            if os.name != 'nt': self.assertEqual(files[0].stat().st_mode & 0o077, 0)

    def test_unrestricted_diagnostics_directory_is_refused_before_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            if os.name == 'nt':
                # Grant a harmless owned empty fixture a broader read ACL, then
                # revoke it; never change the private vault or a real repository.
                for grant in ['*S-1-1-0:(OI)(CI)(RX)', '*S-1-1-0:(OI)(CI)(IO)(R)']:
                    result = subprocess.run(['icacls.exe', str(root), '/grant', grant], capture_output=True)
                    self.assertEqual(result.returncode, 0)
                    try:
                        with self.assertRaises(RuntimeError): self.module.private_diagnostics_directory(root)
                    finally:
                        restored = subprocess.run(['icacls.exe', str(root), '/remove:g', '*S-1-1-0'], capture_output=True)
                        self.assertEqual(restored.returncode, 0)
            else:
                root.chmod(0o755)
                with self.assertRaises(RuntimeError): self.module.private_diagnostics_directory(root)
                root.chmod(0o700)


if __name__ == '__main__':
    unittest.main()
