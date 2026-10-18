"""Scoped public metadata recovery; caller holds the shared engine operation lock."""
import hashlib,os,re,sqlite3,tempfile
from contextlib import closing
from pathlib import Path
from app.storage import safe_path

def fingerprint(path):
    safe_path(Path(path))
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def snapshot(source,target):
    source=safe_path(Path(source));target=safe_path(Path(target))
    if target.exists():raise ValueError('Backup already exists')
    with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as original,closing(sqlite3.connect(target)) as backup:
        original.backup(backup)
        if backup.execute('PRAGMA integrity_check').fetchone()!=('ok',):raise ValueError('Backup integrity failed')
    target.chmod(0o600)

def restore_public(current,backup,expected_current):
    current=safe_path(Path(current));backup=safe_path(Path(backup))
    expected=[expected_current] if isinstance(expected_current,str) else list(expected_current)
    if not 1<=len(expected)<=2 or any(not isinstance(x,str) or not re.fullmatch('[a-f0-9]{64}',x) for x in expected):raise ValueError('One or two exact transaction fingerprints required')
    if fingerprint(current) not in expected:raise ValueError('Concurrent metadata differs; reconcile instead of overwriting')
    owner=current.stat()
    with closing(sqlite3.connect(backup.as_uri()+'?mode=ro',uri=True)) as db:
        if db.execute('PRAGMA integrity_check').fetchone()!=('ok',):raise ValueError('Backup integrity failed')
        if db.execute('SELECT visibility FROM identity').fetchall()!=[('public',)]:raise ValueError('Public snapshot required')
    # Temporary state is SQLite metadata only, atomically published on same filesystem.
    with tempfile.TemporaryDirectory(prefix='.catalog-rollback-',dir=current.parent) as temp:
        staged=Path(temp)/'external.sqlite';snapshot(backup,staged)
        if os.name=='posix':os.chown(staged,owner.st_uid,owner.st_gid)
        staged.chmod(0o600)
        with staged.open('r+b') as f:os.fsync(f.fileno())
        os.replace(staged,current)
        if os.name=='posix':
            fd=os.open(current.parent,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(fd)
            finally:os.close(fd)
