import json
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from app.config import Settings
from app.models import Artifact, SourceConfig, ReleaseManifest, public_projection
from app.db import initialize, open_readonly, snapshot


class ContractTests(unittest.TestCase):
    def test_unclassified_artifact_is_restricted_and_not_projected(self):
        artifact = Artifact(sha256='a'*64, size_bytes=42, name='private-fixture', version='1', architecture='amd64', filename='file.deb')
        self.assertEqual(artifact.visibility, 'restricted')
        self.assertIsNone(public_projection(artifact))

    def test_public_projection_has_no_private_storage_or_location_fields(self):
        artifact = Artifact(sha256='b'*64, size_bytes=1, name='public', version='1', architecture='all', filename='file.deb', visibility='public')
        self.assertEqual(set(public_projection(artifact).model_dump()), {'sha256','size_bytes','name','version','architecture','filename'})

    def test_invalid_digest_and_size_are_rejected(self):
        with self.assertRaises(ValueError):
            Artifact(sha256='not-a-hash', size_bytes=-1, name='x', version='1', architecture='all', filename='x')

    def test_source_cannot_be_enabled_without_evidence(self):
        with self.assertRaises(ValueError):
            SourceConfig(id='source', provider='candidate', ecosystem='apt', routing_enabled=True)
        self.assertFalse(SourceConfig(id='source',provider='candidate',ecosystem='apt').routing_enabled)

    def test_config_rejects_unsafe_prefix_and_private_activation(self):
        self.assertEqual(Settings(data_dir=Path('unused')).base_path, '/software')
        for prefix in ['//evil', '/software/../admin', '/software?next=x', '/software/']:
            with self.assertRaises(ValueError):
                Settings(data_dir=Path('unused'), base_path=prefix)
        with self.assertRaises(ValueError):
            Settings(data_dir=Path('unused'), restricted_enabled=True)

    def test_release_manifest_rejects_floating_images(self):
        with self.assertRaises(ValueError):
            ReleaseManifest(commit='a'*40, architecture='amd64', image_digests=['python:latest'])
        manifest = ReleaseManifest(commit='a'*40,architecture='amd64',image_digests=['sha256:'+'b'*64])
        self.assertEqual(manifest.schema_version, 1)

    def test_migration_is_idempotent_and_new_records_default_restricted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'catalog.sqlite'
            initialize(path)
            initialize(path)
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute('PRAGMA user_version').fetchone(), (1,))
                self.assertEqual(db.execute('SELECT COUNT(*) FROM schema_migrations').fetchone(), (1,))
                columns = {r[1]:r[4] for r in db.execute('PRAGMA table_info(artifacts)')}
                self.assertEqual(columns['visibility'], "'restricted'")
            with closing(open_readonly(path)) as db:
                with self.assertRaises(sqlite3.OperationalError):
                    db.execute('DELETE FROM sources')

    def test_future_schema_fails_without_overwriting_it(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'catalog.sqlite'
            with closing(sqlite3.connect(path)) as db:
                db.execute('PRAGMA user_version=2')
            with self.assertRaises(ValueError):
                initialize(path)
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute('PRAGMA user_version').fetchone(), (2,))

    def test_sqlite_snapshot_includes_committed_wal_state(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'catalog.sqlite'
            target=Path(temp)/'backup.sqlite'
            initialize(path)
            with closing(sqlite3.connect(path)) as db:
                db.execute('PRAGMA journal_mode=WAL')
                db.execute("INSERT INTO audit_events(created_at,actor,action,target,detail_json) VALUES ('test','fixture','test','fixture','{}')")
                db.commit()
                snapshot(path,target)
            with closing(sqlite3.connect(target)) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM audit_events').fetchone(), (1,))
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone(), ('ok',))


if __name__ == '__main__': unittest.main()
