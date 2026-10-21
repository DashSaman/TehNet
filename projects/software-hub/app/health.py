"""Durable network quotas, per-host leases and failure circuits. Explicit CLI init only."""
from contextlib import contextmanager,closing
from dataclasses import dataclass
from datetime import datetime,timezone,timedelta
import hashlib
import os
from pathlib import Path
import secrets
import sqlite3
import time
from .models import ProbeBudget

class BudgetDenied(Exception):pass

SCHEMA='''
CREATE TABLE identity(checksum TEXT NOT NULL);
CREATE TABLE daily(day TEXT PRIMARY KEY,requests INTEGER NOT NULL,bytes INTEGER NOT NULL);
CREATE TABLE host(hostname TEXT PRIMARY KEY,last REAL NOT NULL,failures INTEGER NOT NULL,successes INTEGER NOT NULL,blocked REAL NOT NULL,token TEXT,lease_until REAL NOT NULL);
CREATE TABLE full_worker(id INTEGER PRIMARY KEY CHECK(id=1),token TEXT NOT NULL,lease_until REAL NOT NULL);
'''
CHECKSUM=hashlib.sha256(SCHEMA.encode()).hexdigest()
@dataclass(frozen=True)
class Ticket:
    host:str
    token:str
    full:bool

class NetworkBudget:
    def __init__(self,path:Path,limits:ProbeBudget|None=None,*,clock=time.time):
        self.path=Path(path);self.limits=limits or ProbeBudget();self.clock=clock
    def initialize(self):
        self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        self._paths()
        with closing(sqlite3.connect(self.path)) as db:
            if db.execute('PRAGMA user_version').fetchone()[0]==0:
                db.executescript('BEGIN IMMEDIATE;'+SCHEMA)
                db.execute('INSERT INTO identity VALUES(?)',(CHECKSUM,));db.execute('PRAGMA user_version=1');db.commit()
            self._check(db)
        os.chmod(self.path,0o600)
    def _paths(self):
        if any(p.is_symlink() for p in [self.path,*self.path.absolute().parents]):raise ValueError('Budget state symlink rejected')
    @staticmethod
    def _check(db):
        if db.execute('PRAGMA user_version').fetchone()[0]!=1 or db.execute('SELECT checksum FROM identity').fetchall()!=[(CHECKSUM,)]:
            raise ValueError('Unsupported budget schema or migration identity')
    @contextmanager
    def connection(self):
        self._paths()
        with closing(sqlite3.connect(self.path.absolute().as_uri()+'?mode=rw',uri=True,timeout=2)) as db:
            self._check(db);db.execute('BEGIN IMMEDIATE')
            try:yield db;db.commit()
            except BaseException:db.rollback();raise
    def reserve(self,host,max_bytes,*,full=False):
        if max_bytes<0 or max_bytes>(512*1024*1024 if full else self.limits.sample_bytes):raise BudgetDenied('BODY_CAP')
        now=self.clock();day=datetime.fromtimestamp(now,timezone.utc).strftime('%Y-%m-%d');token=secrets.token_hex(16)
        with self.connection() as db:
            row=db.execute('SELECT last,failures,successes,blocked,token,lease_until FROM host WHERE hostname=?',(host,)).fetchone()
            if row and (now-row[0]<1 or row[3]>now or row[5]>now):raise BudgetDenied('HOST_BACKOFF')
            if db.execute('SELECT COUNT(*) FROM host WHERE lease_until>?',(now,)).fetchone()[0]>=self.limits.concurrency:raise BudgetDenied('GLOBAL_CONCURRENCY')
            worker=db.execute('SELECT lease_until FROM full_worker WHERE id=1').fetchone()
            if full and worker and worker[0]>now:raise BudgetDenied('FULL_WORKER_BUSY')
            used=db.execute('SELECT requests,bytes FROM daily WHERE day=?',(day,)).fetchone() or (0,0)
            charge=max_bytes if full else 0
            if used[0]>=self.limits.requests_per_day or used[1]+charge>self.limits.full_bytes_per_day:raise BudgetDenied('DAILY_QUOTA')
            db.execute('INSERT INTO daily VALUES(?,?,?) ON CONFLICT(day) DO UPDATE SET requests=excluded.requests,bytes=excluded.bytes',(day,used[0]+1,used[1]+charge))
            db.execute('DELETE FROM daily WHERE day<?',((datetime.fromtimestamp(now,timezone.utc)-timedelta(days=31)).strftime('%Y-%m-%d'),))
            lease_until=now+self.limits.timeout_seconds+30
            db.execute('INSERT INTO host VALUES(?,?,0,0,0,?,?) ON CONFLICT(hostname) DO UPDATE SET last=excluded.last,token=excluded.token,lease_until=excluded.lease_until',(host,now,token,lease_until))
            if full:db.execute('INSERT INTO full_worker VALUES(1,?,?) ON CONFLICT(id) DO UPDATE SET token=excluded.token,lease_until=excluded.lease_until',(token,lease_until))
        return Ticket(host,token,full)
    def finish(self,ticket,success,*,retry_after=0):
        now=self.clock()
        with self.connection() as db:
            row=db.execute('SELECT failures,successes,blocked FROM host WHERE hostname=? AND token=?',(ticket.host,ticket.token)).fetchone()
            if not row:return
            failures,successes,blocked=row
            if success:
                successes+=1
                if successes>=2:failures=0;blocked=0
            else:
                failures+=1;successes=0
                if failures>=3:blocked=now+300
            blocked=max(blocked,now+min(max(retry_after,0),86400)) if retry_after else blocked
            db.execute('UPDATE host SET failures=?,successes=?,blocked=?,token=NULL,lease_until=0 WHERE hostname=? AND token=?',(failures,successes,blocked,ticket.host,ticket.token))
            if ticket.full:db.execute('DELETE FROM full_worker WHERE token=?',(ticket.token,))
