"""Synthetic local drill ONLY. Never accepts production paths or credentials.

Exercises a SQLite backup, verified bundle restore, pointer cutover and rollback.
Does not exercise Docker, Nginx, TLS, DNS, remote transfer or application auth.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import sqlite3
import tempfile
import time
import zipfile


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def manifest(root):
    return {p.relative_to(root).as_posix(): {'size_bytes': p.stat().st_size, 'sha256': digest(p)}
            for p in sorted(root.rglob('*')) if p.is_file()}


def verify_files(root, expected):
    root = root.resolve()
    for name, record in expected.items():
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name:
            raise ValueError('unsafe manifest path')
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('missing or escaped file')
        if path.stat().st_size != record['size_bytes'] or digest(path) != record['sha256']:
            raise ValueError('file integrity mismatch')
    if set(manifest(root)) != set(expected):
        raise ValueError('unlisted files in restored tree')


def verify_database(path, expected_release):
    try:
        with closing(sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True)) as db:
            if db.execute('PRAGMA integrity_check').fetchone() != ('ok',):
                raise ValueError('SQLite integrity failure')
            if db.execute('SELECT value FROM state WHERE name = ?', ('release',)).fetchone() != (expected_release,):
                raise ValueError('restored state mismatch')
    except sqlite3.Error as exc:
        raise ValueError('unusable SQLite snapshot') from exc


def run_rehearsal(payload_bytes=16 * 1024 * 1024):
    if payload_bytes <= 0 or payload_bytes > 256 * 1024 * 1024:
        raise ValueError('fixture size must be in 1..256 MiB')
    timings = {}
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='melika-synthetic-') as temp:
        root = Path(temp)
        source = root / 'foreign-fixture'
        source.mkdir()
        (source / 'objects').mkdir()
        # Random bytes avoid an unrealistically tiny compressed test transfer.
        (source / 'objects' / 'synthetic-artifact.bin').write_bytes(os.urandom(payload_bytes))
        (source / 'config.json').write_text(json.dumps({'base_path': '/melika', 'rubika_enabled': False}), encoding='utf-8')
        with closing(sqlite3.connect(root / 'live.sqlite')) as live:
            live.execute('PRAGMA journal_mode=WAL')
            live.execute('CREATE TABLE state(name TEXT PRIMARY KEY, value TEXT)')
            live.execute('INSERT INTO state VALUES (?, ?)', ('release', 'release-A'))
            live.commit()
            with closing(sqlite3.connect(source / 'catalog.sqlite')) as snapshot:
                live.backup(snapshot)
        verify_database(source / 'catalog.sqlite', 'release-A')
        expected = manifest(source)
        timings['fixture_and_snapshot_seconds'] = time.perf_counter() - started
        phase = time.perf_counter()
        bundle = root / 'release.zip'
        with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_STORED) as archive:
            for name in expected:
                archive.write(source / name, name)
        incoming = root / 'iran-fixture-incoming.zip'
        shutil.copyfile(bundle, incoming)
        if digest(bundle) != digest(incoming):
            raise ValueError('local transfer digest mismatch')
        timings['bundle_and_local_copy_seconds'] = time.perf_counter() - phase
        phase = time.perf_counter()
        restored = root / 'release-A'
        restored.mkdir()
        # Extract ONLY this process's own archive and known manifest members.
        # This is deliberately not a production archive importer.
        with zipfile.ZipFile(incoming) as archive:
            if set(archive.namelist()) != set(expected):
                raise ValueError('bundle member mismatch')
            for name in expected:
                target = restored / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(name) as src, target.open('xb') as dst:
                    shutil.copyfileobj(src, dst)
        verify_files(restored, expected)
        verify_database(restored / 'catalog.sqlite', 'release-A')
        timings['restore_and_verify_seconds'] = time.perf_counter() - phase
        phase = time.perf_counter()
        active = root / 'ACTIVE'
        staged = root / 'ACTIVE.next'
        active.write_text(source.name, encoding='utf-8')
        staged.write_text('release-A', encoding='utf-8')
        staged.replace(active)
        if active.read_text(encoding='utf-8') != 'release-A':
            raise ValueError('cutover failed')
        timings['synthetic_cutover_seconds'] = time.perf_counter() - phase
        phase = time.perf_counter()
        staged.write_text(source.name, encoding='utf-8')
        staged.replace(active)
        rollback_target = root / active.read_text(encoding='utf-8')
        if rollback_target != source or not rollback_target.is_dir():
            raise ValueError('rollback pointer failed')
        verify_files(rollback_target, expected)
        verify_database(rollback_target / 'catalog.sqlite', 'release-A')
        timings['rollback_and_source_verify_seconds'] = time.perf_counter() - phase
        result = {'schema_version': 1, 'tested_at_utc': datetime.now(timezone.utc).isoformat(),
                  'scope': 'synthetic-local-filesystem-only', 'platform': platform.platform(),
                  'python': platform.python_version(), 'payload_bytes': payload_bytes,
                  'bundle_bytes': bundle.stat().st_size, 'timings': timings,
                  'restore_verified': True, 'rollback_verified': True, 'rollback_target_exists': True,
                  'production_migration_accepted': False,
                  'not_tested': ['Linux permissions', 'Docker', 'Nginx', 'TLS', 'DNS',
                                 'WAN transfer', 'real catalog', 'VPN authentication', 'foreign-to-Iran cutover']}
    result['total_seconds'] = time.perf_counter() - started
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload-mib', type=int, default=16)
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.runs <= 10:
        parser.error('--runs must be 1..10')
    report = {'runs': [run_rehearsal(args.payload_mib * 1024 * 1024) for _ in range(args.runs)]}
    # Refuse overwriting an existing evidence record.
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report, indent=2))
