"""Versioned SQLite creation and consistent snapshots. No migration during HTTP requests."""
from contextlib import closing
import hashlib
from pathlib import Path
import sqlite3

VERSION = 1
MIGRATION = Path(__file__).with_name('migrations') / '001_initial.sql'


def initialize(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sql = MIGRATION.read_text(encoding='utf-8')
    checksum = hashlib.sha256(sql.encode()).hexdigest()
    with closing(sqlite3.connect(path)) as db:
        version = db.execute('PRAGMA user_version').fetchone()[0]
        if version > VERSION:
            raise ValueError('Unsupported future database schema; no state changed')
        if version == VERSION:
            saved = db.execute('SELECT sha256 FROM schema_migrations WHERE version=?', (VERSION,)).fetchone()
            if saved != (checksum,):
                raise ValueError('Applied migration identity does not match this release')
            return
        if version != 0:
            raise ValueError('Unsupported upgrade path')
        # One transaction; SQLite rolls it back if the connection closes on error.
        db.executescript('BEGIN IMMEDIATE;\n' + sql)
        db.execute('INSERT INTO schema_migrations(version,sha256) VALUES (?,?)', (VERSION,checksum))
        db.execute('PRAGMA user_version=1')
        db.commit()


def open_readonly(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    if db.execute('PRAGMA user_version').fetchone()[0] != VERSION:
        db.close()
        raise ValueError('Unsupported schema; run approved initialization outside the app')
    return db


def snapshot(source: Path, destination: Path) -> None:
    if destination.exists():
        raise ValueError('Snapshot must not overwrite existing state')
    with closing(open_readonly(source)) as src, closing(sqlite3.connect(destination)) as dst:
        src.backup(dst)
        if dst.execute('PRAGMA integrity_check').fetchone() != ('ok',):
            raise ValueError('Backup integrity failed')
