"""Metadata-only registry. Software bytes stay on approved external providers."""
from contextlib import closing,contextmanager
import hashlib
from pathlib import Path
import sqlite3
import time
from .models import Artifact,SourceConfig
from .netguard import canonical_target
from .storage import safe_path,DIGEST,FILENAME,StoreRejected,AccessDenied

SCHEMA='''CREATE TABLE identity(version INTEGER NOT NULL,checksum TEXT NOT NULL,visibility TEXT NOT NULL);
CREATE TABLE external(sha256 TEXT PRIMARY KEY,record_json TEXT NOT NULL,source_json TEXT NOT NULL,relative_path TEXT NOT NULL,url TEXT NOT NULL,verified_at REAL NOT NULL,provenance TEXT NOT NULL);'''
CHECKSUM=hashlib.sha256(SCHEMA.encode()).hexdigest()

class ExternalRegistry:
    def __init__(self,root:Path,*,visibility='restricted',authorize=None,clock=time.time):
        if visibility not in ['public','restricted']:raise StoreRejected('Invalid visibility')
        self.root=Path(root).absolute();self.database=self.root/'external.sqlite'
        self.visibility=visibility;self.authorize=authorize;self.clock=clock
    def initialize(self):
        safe_path(self.root);self.root.mkdir(mode=0o700,parents=True,exist_ok=True);safe_path(self.database)
        with closing(sqlite3.connect(self.database)) as db:
            if db.execute('PRAGMA user_version').fetchone()[0]==0:
                db.executescript('BEGIN IMMEDIATE;'+SCHEMA)
                db.execute('INSERT INTO identity VALUES(1,?,?)',(CHECKSUM,self.visibility));db.execute('PRAGMA user_version=1');db.commit()
            self._check(db)
        self.database.chmod(0o600)
    def _check(self,db):
        if db.execute('PRAGMA user_version').fetchone()[0]!=1 or db.execute('SELECT * FROM identity').fetchall()!=[(1,CHECKSUM,self.visibility)]:raise StoreRejected('Unknown external registry schema')
        db.execute('SELECT sha256,record_json,source_json,relative_path,url,verified_at,provenance FROM external LIMIT 0')
    @contextmanager
    def connection(self,*,write=False):
        safe_path(self.database)
        if not self.database.is_file() or self.database.stat().st_nlink!=1:raise StoreRejected('Initialize external registry explicitly')
        with closing(sqlite3.connect(self.database.as_uri()+('?mode=rw' if write else '?mode=ro'),uri=True,timeout=2)) as db:
            self._check(db)
            if write:db.execute('BEGIN IMMEDIATE')
            try:
                yield db
                if write:db.commit()
            except BaseException:
                if write:db.rollback()
                raise
    def _access(self,context):
        if self.visibility=='restricted' and (not self.authorize or not self.authorize(context)):raise AccessDenied()
    def register_verified(self,source,path,item,client,*,license_approved=False,provenance=''):
        if item.visibility!=self.visibility or not license_approved or not 1<=len(provenance)<=2048 or not FILENAME.fullmatch(item.filename):raise StoreRejected('Explicit classification, license and provenance required')
        if any(not 1<=len(v)<=256 for v in [item.name,item.version,item.architecture]) or item.size_bytes>512*1024**2:raise StoreRejected('Metadata/verification cap exceeded')
        if self.visibility=='public' and source.visibility!='public':raise StoreRejected('Public source classification required')
        # Validate URL syntax without a second DNS lookup; the guarded verifier resolves and pins actual transport.
        _,target_url=canonical_target(source.base_url,path,set(source.allowed_hosts))
        with self.connection() as db:
            old=db.execute('SELECT record_json,source_json,relative_path FROM external WHERE sha256=?',(item.sha256,)).fetchone()
            if old and old!=(item.model_dump_json(),source.model_dump_json(),path):raise StoreRejected('Immutable identity conflict')
            if not old and db.execute('SELECT COUNT(*) FROM external').fetchone()[0]>=10000:raise StoreRejected('Registry cap exceeded')
        result=client.verify_remote(source,path,item)
        if not result.full_hash_verified or result.state!='present_verified':raise StoreRejected('Full verification required')
        with self.connection(write=True) as db:
            # Concurrent registrations cannot change an existing digest's meaning.
            old=db.execute('SELECT record_json,source_json,relative_path FROM external WHERE sha256=?',(item.sha256,)).fetchone()
            if old and old!=(item.model_dump_json(),source.model_dump_json(),path):raise StoreRejected('Immutable identity conflict')
            if not old and db.execute('SELECT COUNT(*) FROM external').fetchone()[0]>=10000:raise StoreRejected('Registry cap exceeded')
            db.execute('INSERT INTO external VALUES(?,?,?,?,?,?,?) ON CONFLICT(sha256) DO UPDATE SET verified_at=excluded.verified_at',
                (item.sha256,item.model_dump_json(),source.model_dump_json(),path,target_url,self.clock(),provenance))
    def artifact(self,digest,*,context=None):
        self._access(context)
        if not DIGEST.fullmatch(digest) or not self.database.exists():return None
        with self.connection() as db:row=db.execute('SELECT record_json FROM external WHERE sha256=?',(digest,)).fetchone()
        if not row:return None
        item=Artifact.model_validate_json(row[0])
        if item.sha256!=digest or item.visibility!=self.visibility:raise StoreRejected('Classification mismatch')
        return item
    def list_artifacts(self,q='',cursor=0,limit=50,*,context=None):
        self._access(context)
        if not self.database.exists():return {'items':[],'total':0}
        if not 0<=cursor<=10000 or not 1<=limit<=100 or len(q)>120:raise StoreRejected('Invalid pagination')
        with self.connection() as db:rows=db.execute('SELECT sha256,record_json FROM external ORDER BY sha256').fetchall()
        records=[]
        for digest,raw in rows:
            item=Artifact.model_validate_json(raw)
            if item.sha256!=digest or item.visibility!=self.visibility:raise StoreRejected('Classification mismatch')
            records.append(item.model_dump())
        records=[r for r in records if q.lower() in (r['name']+' '+r['version']+' '+r['architecture']).lower()]
        return {'items':records[cursor:cursor+limit],'total':len(records)}
    def download_target(self,digest,*,context=None):
        self._access(context)
        if self.visibility!='public':raise StoreRejected('Private external delivery requires a separately accepted authenticated provider; no public redirects')
        if not self.artifact(digest):raise StoreRejected('Unknown registered artifact')
        with self.connection() as db:row=db.execute('SELECT source_json,relative_path,url,verified_at FROM external WHERE sha256=?',(digest,)).fetchone()
        source=SourceConfig.model_validate_json(row[0])
        if not source.routing_enabled or source.visibility!='public' or source.permission_state!='approved' or source.domestic_state!='verified' or not source.approval_evidence:raise StoreRejected('Source unavailable')
        if not 0<=self.clock()-row[3]<=3600:raise StoreRejected('Verification expired; operator must reverify')
        _,target_url=canonical_target(source.base_url,row[1],set(source.allowed_hosts))
        if target_url!=row[2]:raise StoreRejected('Target mismatch')
        return target_url
