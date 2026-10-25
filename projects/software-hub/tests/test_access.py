from contextlib import closing
from datetime import datetime,timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest

from app.auth import AuthStore,AuthDenied,AuthThrottled
from app.models import AccessContext

PASSWORD='fixture-only never a production password 123!'

class AuthTests(unittest.TestCase):
    def test_incomplete_auth_schema_is_rejected_even_with_matching_identity(self):
        with closing(sqlite3.connect(self.path)) as db:db.execute('DROP TABLE credential');db.commit()
        with self.assertRaises((ValueError,sqlite3.Error)):
            with self.auth.connection():pass

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'auth.sqlite'
        self.now=1000000.0
        self.auth=AuthStore(self.path,clock=lambda:self.now)
        self.auth.initialize()
        self.auth.set_password(PASSWORD)
    def login(self,password=PASSWORD):
        nonce,csrf=self.auth.challenge()
        return self.auth.login(nonce,csrf,password)
    def test_password_hash_and_session_secrets_are_not_plaintext(self):
        token,context=self.login()
        data=self.path.read_bytes()
        self.assertNotIn(PASSWORD.encode(),data)
        self.assertNotIn(token.encode(),data)
        self.assertIn(b'$argon2id$',data)
        self.assertTrue(self.auth.validate_context(context))
        self.assertEqual(self.auth.session(token),context)
    def test_missing_state_never_creates_database_on_read(self):
        path=self.path.parent/'absent.sqlite';auth=AuthStore(path)
        self.assertFalse(auth.configured)
        self.assertIsNone(auth.session('a'*43))
        self.assertFalse(path.exists())
    def test_wrong_password_and_replayed_challenge_fail(self):
        nonce,csrf=self.auth.challenge()
        with self.assertRaises(AuthDenied):self.auth.login(nonce,csrf,'wrong password')
        with self.assertRaises(AuthDenied):self.auth.login(nonce,csrf,PASSWORD)
    def test_csrf_is_bound_to_challenge_cookie(self):
        nonce,csrf=self.auth.challenge();other,_=self.auth.challenge()
        with self.assertRaises(AuthDenied):self.auth.login(other,csrf,PASSWORD)
        with self.assertRaises(AuthDenied):self.auth.login(nonce,'bad',PASSWORD)
    def test_session_expires_and_forged_context_fails(self):
        token,context=self.login();self.now+=3601
        self.assertIsNone(self.auth.session(token))
        self.assertFalse(self.auth.validate_context(context))
        forged=AccessContext(principal_id='owner',session_id='a'*64,scope='restricted',expires_at=datetime.now(timezone.utc))
        self.assertFalse(self.auth.validate_context(forged))
    def test_logout_requires_csrf_and_revokes_session(self):
        token,context=self.login()
        with self.assertRaises(AuthDenied):self.auth.logout(token,'bad')
        self.auth.logout(token,self.auth.csrf(context))
        self.assertIsNone(self.auth.session(token))
    def test_rotation_revocation_and_password_change(self):
        first,_=self.login();second,_=self.login()
        self.assertNotEqual(first,second)
        self.auth.revoke_all();self.assertIsNone(self.auth.session(first))
        token,_=self.login();self.auth.set_password(PASSWORD+' changed')
        self.assertIsNone(self.auth.session(token))
        with self.assertRaises(AuthDenied):self.login()
    def test_rate_limit_survives_restart_and_can_be_reset_locally(self):
        for _ in range(5):
            with self.assertRaises(AuthDenied):self.login('wrong')
        restarted=AuthStore(self.path,clock=lambda:self.now)
        nonce,csrf=restarted.challenge()
        with self.assertRaises(AuthThrottled):restarted.login(nonce,csrf,PASSWORD)
        restarted.reset_lockout();self.login()
    def test_weak_password_and_future_schema_fail_closed(self):
        with self.assertRaises(ValueError):self.auth.set_password('short')
        with closing(sqlite3.connect(self.path)) as db:db.execute('PRAGMA user_version=99');db.commit()
        with self.assertRaises(ValueError):self.auth.session('a'*43)
    def test_challenge_expiry_and_unbounded_state_are_prevented(self):
        nonce,csrf=self.auth.challenge();self.now+=601
        with self.assertRaises(AuthDenied):self.auth.login(nonce,csrf,PASSWORD)
        for _ in range(128):self.auth.challenge()
        with self.assertRaises(AuthThrottled):self.auth.challenge()
