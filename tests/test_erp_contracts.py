import importlib.util
from pathlib import Path
import unittest

MODULE=Path(__file__).resolve().parents[1]/'integrations/tehnet_erp/tehnet_erp/contracts.py'
class ERPContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib=None
        if MODULE.exists():
            spec=importlib.util.spec_from_file_location('erp_contracts',MODULE);cls.lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.lib)
    def module(self):
        self.assertIsNotNone(self.lib,'ERP boundary not implemented');return self.lib
    def test_exact_meter_total(self):self.assertEqual(self.module().line_total('2.5','1000'),2500)
    def test_fractional_rial_rejected(self):
        with self.assertRaises(ValueError):self.module().line_total('0.333','1')
    def test_float_input_rejected(self):
        with self.assertRaises(ValueError):self.module().money(0.1)
    def test_negative_money_rejected(self):
        with self.assertRaises(ValueError):self.module().money('-1')
    def test_exponent_input_rejected(self):
        with self.assertRaises(ValueError):self.module().quantity('1e3')
    def test_quantity_precision_rejected(self):
        with self.assertRaises(ValueError):self.module().quantity('0.0001')
    def test_payment_currency_mismatch_rejected(self):
        with self.assertRaises(ValueError):self.module().validate_money_event({'currency':'IRT','amount_irr':'100','expected_amount_irr':'100'})
    def test_payment_amount_mismatch_rejected(self):
        with self.assertRaises(ValueError):self.module().validate_money_event({'currency':'IRR','amount_irr':'100','expected_amount_irr':'101'})
    def test_event_hash_ignores_json_key_order(self):
        self.assertEqual(self.module().payload_hash({'a':1,'b':2}),self.module().payload_hash({'b':2,'a':1}))
    def test_conflicting_payload_hash_differs(self):
        self.assertNotEqual(self.module().payload_hash({'amount':100}),self.module().payload_hash({'amount':101}))
if __name__=='__main__':unittest.main(verbosity=2)
