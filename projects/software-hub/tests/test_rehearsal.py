"""Safety checks for the synthetic migration rehearsal, not the future service."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'rehearse_migration.py'
if TOOL.exists():
    spec = importlib.util.spec_from_file_location('rehearsal', TOOL)
    rehearsal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rehearsal)
else:
    rehearsal = None


class MigrationRehearsalTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(rehearsal, 'Synthetic rehearsal tool is not implemented')

    def test_restore_and_rollback_preserve_exact_state(self):
        report = rehearsal.run_rehearsal(payload_bytes=65536)
        self.assertEqual(report['scope'], 'synthetic-local-filesystem-only')
        self.assertTrue(report['restore_verified'])
        self.assertTrue(report['rollback_verified'])
        self.assertTrue(report['rollback_target_exists'])
        self.assertFalse(report['production_migration_accepted'])
        self.assertEqual(report['payload_bytes'], 65536)
        self.assertGreater(report['bundle_bytes'], 65536)
        self.assertGreater(report['total_seconds'], 0)

    def test_tampered_restored_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'payload').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                rehearsal.verify_files(root, {'payload': {'size_bytes': 3, 'sha256': '0' * 64}})

    def test_manifest_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                rehearsal.verify_files(Path(temp), {'../outside': {'size_bytes': 0, 'sha256': '0' * 64}})

    def test_unlisted_restored_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'unlisted').write_bytes(b'x')
            with self.assertRaises(ValueError):
                rehearsal.verify_files(root, {})

    def test_invalid_db_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / 'broken.sqlite'
            db.write_bytes(b'not a database')
            with self.assertRaises(ValueError):
                rehearsal.verify_database(db, 'release-A')


if __name__ == '__main__':
    unittest.main()
