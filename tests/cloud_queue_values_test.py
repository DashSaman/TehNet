import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("queue_values", Path(__file__).parents[1] / "tools/cloud-queue/queue_values.py")
values = importlib.util.module_from_spec(spec)
spec.loader.exec_module(values)

class QueueLimitReadback(unittest.TestCase):
    def test_actual_routeros_suffix_readback(self):
        self.assertEqual(values.exact_queue_limits("64k/128k"), (64000, 128000))

    def test_equivalent_integer_readback(self):
        self.assertEqual(values.exact_queue_limits("64000/128000"), (64000, 128000))

    def test_reversed_limits_are_not_equivalent(self):
        with self.assertRaises(ValueError):
            values.exact_queue_limits("128k/64k")

    def test_invalid_or_unbounded_limits_are_rejected(self):
        for candidate in ("0/0", "64k", "64k//128k", "64k/128k;extra"):
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                values.exact_queue_limits(candidate)

if __name__ == "__main__":
    unittest.main()
