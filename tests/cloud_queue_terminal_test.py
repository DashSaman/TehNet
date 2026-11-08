import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).resolve().parents[1] / "tools/cloud-queue/prompt_state.py"
spec = importlib.util.spec_from_file_location("queue_prompt_state", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
P = {"license": rb"Do you want to see.*license",
     "repeat": rb"repeat new password\s*[:>]",
     "new": rb"new password\s*[:>]",
     "prompt": rb"\[[^\n]+\]\s*>"}

class PromptStateTests(unittest.TestCase):
    def test_new_password_prompt_supersedes_license_history(self):
        response = b"Do you want to see software license? [Y/n]: n\nChange your password\nnew password>"
        self.assertEqual(m.select_prompt(response, P), "new")

    def test_shell_prompt_supersedes_echoed_confirmation(self):
        response = b"repeat new password> \nPassword changed\n[admin@MikroTik] >"
        self.assertEqual(m.select_prompt(response, P), "prompt")

    def test_repeat_prompt_is_not_misclassified_as_new(self):
        self.assertEqual(m.select_prompt(b"repeat new password>", P), "repeat")

    def test_partial_response_does_not_advance_login(self):
        self.assertIsNone(m.select_prompt(b"RouterOS is starting\n", P))

if __name__ == "__main__":
    unittest.main()
