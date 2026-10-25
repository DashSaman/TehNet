"""Local Argon2 password gate; opaque revocable sessions, never WordPress accounts."""
from contextlib import contextmanager,closing
from datetime import datetime,timezone
import hashlib
import hmac
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time

from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from argon2.exceptions import VerificationError
from .models import AccessContext

PASSWORD_HASH=PasswordHash.recommended()
VERIFY_LOCK=threading.BoundedSemaphore(1)
TOKEN=re.compile(r'^[A-Za-z0-9_-]{43}$')
SCHEMA='''
CREATE TABLE identity(version INTEGER NOT NULL,checksum TEXT NOT NULL);
CREATE TABLE credential(id INTEGER PRIMARY KEY CHECK(id=1),hash TEXT NOT NULL,epoch INTEGER NOT NULL);
CREATE TABLE challenge(id TEXT PRIMARY KEY,csrf TEXT NOT NULL,expires REAL NOT NULL);
CREATE TABLE session(id TEXT PRIMARY KEY,csrf TEXT NOT NULL,expires REAL NOT NULL,epoch INTEGER NOT NULL);
CREATE TABLE throttle(id INTEGER PRIMARY KEY CHECK(id=1),window REAL NOT NULL,attempts INTEGER NOT NULL);
'''
SCHEMA_HASH=hashlib.sha256(SCHEMA.encode()).hexdigest()

class AuthDenied(Exception):pass
class AuthThrottled(Exception):pass

def token_hash(token):
    if not isinstance(token,str) or not TOKEN.fullmatch(token):return None
    return hashlib.sha256(token.encode('ascii')).hexdigest()

def no_symlink(path):
    if any(part.is_symlink() for part in [path,*path.absolute().parents]):
        raise ValueError('State symlinks are not allowed')

class AuthStore:
    def __init__(self,path:Path,*,clock=time.time):
        self.path=Path(path);self.clock=clock

    def initialize(self):
        no_symlink(self.path)
        self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        with closing(sqlite3.connect(self.path)) as db:
            version=db.execute('PRAGMA user_version').fetchone()[0]
            if version==0:
                db.executescript('BEGIN IMMEDIATE;'+SCHEMA)
                db.execute('INSERT INTO identity VALUES(1,?)',(SCHEMA_HASH,))
                db.execute('PRAGMA user_version=1');db.commit()
            self._check(db)
        os.chmod(self.path,0o600)

    @staticmethod
    def _check(db):
        if db.execute('PRAGMA user_version').fetchone()[0]!=1:
            raise ValueError('Unsupported auth schema; no state changed')
        if db.execute('SELECT version,checksum FROM identity').fetchall()!=[(1,SCHEMA_HASH)]:
            raise ValueError('Auth migration identity mismatch')
        # Identity alone cannot certify a restored/damaged database's actual tables.
        for query in ['SELECT id,hash,epoch FROM credential LIMIT 0',
                      'SELECT id,csrf,expires FROM challenge LIMIT 0',
                      'SELECT id,csrf,expires,epoch FROM session LIMIT 0',
                      'SELECT id,window,attempts FROM throttle LIMIT 0']:
            db.execute(query)
        rows=db.execute('SELECT id,hash,epoch FROM credential').fetchall()
        if len(rows)>1 or any(row[0]!=1 or not row[1].startswith('$argon2id$') or not isinstance(row[2],int) or row[2]<1 for row in rows):
            raise ValueError('Invalid credential state')

    @contextmanager
    def connection(self,*,write=False):
        no_symlink(self.path)
        with closing(sqlite3.connect(self.path.absolute().as_uri()+'?mode=rw',uri=True,timeout=2)) as db:
            self._check(db)
            if write:db.execute('BEGIN IMMEDIATE')
            try:
                yield db
                if write:db.commit()
            except BaseException:
                if write:db.rollback()
                raise

    @property
    def configured(self):
        if not self.path.exists():return False
        with self.connection() as db:return db.execute('SELECT 1 FROM credential WHERE id=1').fetchone() is not None

    def set_password(self,password):
        if not 16<=len(password)<=256 or len(password.encode('utf-8'))>1024:
            raise ValueError('Use a password of 16 to 256 characters')
        encoded=PASSWORD_HASH.hash(password)
        with self.connection(write=True) as db:
            db.execute('INSERT INTO credential VALUES(1,?,1) ON CONFLICT(id) DO UPDATE SET hash=excluded.hash,epoch=credential.epoch+1',(encoded,))
            db.execute('DELETE FROM session');db.execute('DELETE FROM challenge')

    def challenge(self):
        if not self.configured:raise AuthDenied()
        now=self.clock();nonce=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
        with self.connection(write=True) as db:
            db.execute('DELETE FROM challenge WHERE expires<=?',(now,))
            if db.execute('SELECT COUNT(*) FROM challenge').fetchone()[0]>=128:raise AuthThrottled()
            db.execute('INSERT INTO challenge VALUES(?,?,?)',(token_hash(nonce),csrf,now+600))
        return nonce,csrf

    def login(self,nonce,csrf,password):
        key=token_hash(nonce)
        if key is None or not isinstance(csrf,str) or not TOKEN.fullmatch(csrf):raise AuthDenied()
        now=self.clock()
        # Consume challenges and charge attempts before the expensive password KDF.
        with self.connection(write=True) as db:
            row=db.execute('SELECT csrf,expires FROM challenge WHERE id=?',(key,)).fetchone()
            if row is None or row[1]<=now or not hmac.compare_digest(row[0],csrf):raise AuthDenied()
            throttle=db.execute('SELECT window,attempts FROM throttle WHERE id=1').fetchone()
            if throttle and now-throttle[0]<60 and throttle[1]>=5:raise AuthThrottled()
            window,count=(throttle[0],throttle[1]+1) if throttle and 0<=now-throttle[0]<60 else (now,1)
            db.execute('INSERT INTO throttle VALUES(1,?,?) ON CONFLICT(id) DO UPDATE SET window=excluded.window,attempts=excluded.attempts',(window,count))
            db.execute('DELETE FROM challenge WHERE id=?',(key,))
            credential=db.execute('SELECT hash,epoch FROM credential WHERE id=1').fetchone()
        if credential is None or not isinstance(password,str) or len(password)>256 or len(password.encode('utf-8'))>1024:
            raise AuthDenied()
        if not VERIFY_LOCK.acquire(blocking=False):raise AuthThrottled()
        try:
            try:valid,updated=PASSWORD_HASH.verify_and_update(password,credential[0])
            except (ValueError,UnknownHashError,VerificationError):
                # A corrupt/unsupported stored hash is a denial, never a bypass.
                valid,updated=False,None
        finally:VERIFY_LOCK.release()
        if not valid:raise AuthDenied()
        token=secrets.token_urlsafe(32);expires=now+3600
        with self.connection(write=True) as db:
            current=db.execute('SELECT epoch FROM credential WHERE id=1').fetchone()
            if current!=(credential[1],):raise AuthDenied()
            db.execute('DELETE FROM session WHERE expires<=?',(now,))
            if db.execute('SELECT COUNT(*) FROM session').fetchone()[0]>=64:raise AuthThrottled()
            if updated:db.execute('UPDATE credential SET hash=? WHERE id=1',(updated,))
            db.execute('INSERT INTO session VALUES(?,?,?,?)',(token_hash(token),secrets.token_urlsafe(32),expires,credential[1]))
        return token,AccessContext(principal_id='owner',session_id=token_hash(token),scope='restricted',expires_at=datetime.fromtimestamp(expires,timezone.utc))

    def _row(self,db,session_id):
        return db.execute('SELECT s.csrf,s.expires FROM session s JOIN credential c ON c.epoch=s.epoch WHERE s.id=? AND c.id=1 AND s.expires>?',(session_id,self.clock())).fetchone()

    def session(self,token):
        key=token_hash(token)
        if key is None or not self.path.exists():return None
        with self.connection() as db:row=self._row(db,key)
        if not row:return None
        return AccessContext(principal_id='owner',session_id=key,scope='restricted',expires_at=datetime.fromtimestamp(row[1],timezone.utc))

    def validate_context(self,context):
        if not isinstance(context,AccessContext) or context.principal_id!='owner' or context.scope!='restricted':return False
        with self.connection() as db:row=self._row(db,context.session_id)
        return bool(row and datetime.fromtimestamp(row[1],timezone.utc)==context.expires_at)

    def csrf(self,context):
        if not self.validate_context(context):raise AuthDenied()
        with self.connection() as db:return self._row(db,context.session_id)[0]

    def logout(self,token,csrf):
        context=self.session(token)
        if context is None or not isinstance(csrf,str) or not TOKEN.fullmatch(csrf):raise AuthDenied()
        with self.connection(write=True) as db:
            row=self._row(db,context.session_id)
            if not row or not hmac.compare_digest(row[0],csrf):raise AuthDenied()
            db.execute('DELETE FROM session WHERE id=?',(context.session_id,))

    def revoke_all(self):
        with self.connection(write=True) as db:db.execute('DELETE FROM session')

    def revoke_token(self,token):
        key=token_hash(token)
        if key:
            with self.connection(write=True) as db:db.execute('DELETE FROM session WHERE id=?',(key,))

    def reset_lockout(self):
        with self.connection(write=True) as db:db.execute('DELETE FROM throttle');db.execute('DELETE FROM challenge')
