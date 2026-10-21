from contextlib import redirect_stdout,redirect_stderr
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from app.cli import main
from app.auth import AuthStore

class AuthCliTests(unittest.TestCase):
    def run_cli(self,root,command,interactive,answers=()):
        out=io.StringIO()
        with patch.dict(os.environ,{'TEHNET_SOFTWARE_AUTH':str(root/'auth'),'TEHNET_SOFTWARE_DATA':str(root/'data'),'TEHNET_SOFTWARE_RESTRICTED':'0'}),patch('sys.argv',['cli',command]),patch('sys.stdin.isatty',return_value=interactive),patch('getpass.getpass',side_effect=answers),redirect_stdout(out),redirect_stderr(out):
            main()
        return out.getvalue()
    def test_password_requires_terminal_and_never_accepts_plain_argument_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with self.assertRaises(SystemExit):self.run_cli(root,'set-password',False)
            self.assertFalse((root/'auth/auth.sqlite').exists())
    def test_interactive_setup_does_not_print_password_and_admin_revoke_works(self):
        password='fixture-only interactive password !123'
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);out=self.run_cli(root,'set-password',True,[password,password])
            self.assertNotIn(password,out)
            store=AuthStore(root/'auth/auth.sqlite');nonce,csrf=store.challenge();token,_=store.login(nonce,csrf,password)
            self.run_cli(root,'revoke-sessions',False)
            self.assertIsNone(store.session(token))
    def test_confirmation_mismatch_keeps_state_absent(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with self.assertRaises(SystemExit):self.run_cli(root,'set-password',True,['fixture-password 123!','different'])
            self.assertFalse((root/'auth/auth.sqlite').exists())
