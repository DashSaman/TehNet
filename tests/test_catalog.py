import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/'ops/catalog/catalog.py'

class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module=None
        if MODULE.exists():
            spec=importlib.util.spec_from_file_location('catalog',MODULE)
            cls.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.module)
    def catalog(self):
        self.assertIsNotNone(self.module,'Catalog normalizer is not implemented')
        return self.module
    def product(self):
        return {'id':7,'name':'کابل Cat6 PVC حلقه 305 متری تست فلوک پرمننت','permalink':'https://saieedshabake.ir/product/cable/','type':'simple','sku':'supplier-sku','description':'COPYRIGHTED TEXT','short_description':'COPYRIGHTED SHORT','prices':{'price':'123456','currency_code':'IRT'},'is_in_stock':True,'images':[{'src':'https://saieedshabake.ir/image.jpg'}],'review_count':9,'average_rating':'5','categories':[{'id':1}],'attributes':[]}
    def manifest(self,products=None):
        return self.catalog().build_manifest(products or [self.product()],[{'id':1,'name':'کابل','slug':'cable','parent':0}])
    def test_source_prices_and_stock_never_become_sale_data(self):
        p=self.manifest()['products'][0]
        self.assertEqual((p['status'],p['stock_quantity'],p['regular_price'],p['sku']),('draft',0,'','TN-SN-7'))
        self.assertEqual(p['source_observation']['price']['price'],'123456')
        self.assertTrue(p['source_observation']['in_stock'])
    def test_media_reviews_and_copyrighted_prose_are_excluded(self):
        p=self.manifest()['products'][0]
        self.assertEqual(p['images'],[])
        self.assertNotIn('COPYRIGHTED',p['description'])
        self.assertNotIn('average_rating',p)
        self.assertEqual(p['media_license'],'unverified-not-imported')
    def test_duplicate_ids_rejected_before_any_import(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):
            self.manifest([self.product(),self.product()])
    def test_external_source_url_rejected(self):
        p=self.product();p['permalink']='https://example.com/private'
        with self.assertRaisesRegex(ValueError,'source URL'):
            self.manifest([p])
    def test_unknown_category_is_not_silently_dropped(self):
        p=self.product();p['categories']=[{'id':99}]
        with self.assertRaisesRegex(ValueError,'category'):
            self.manifest([p])
    def test_unsupported_variation_type_is_not_lost(self):
        p=self.product();p['type']='variable'
        with self.assertRaisesRegex(ValueError,'variable'):
            self.manifest([p])
    def test_source_technical_claim_does_not_become_verified_title(self):
        p=self.manifest()['products'][0]
        self.assertNotIn('تست',p['name'])
        self.assertIn('test-certificate-required',p['review_flags'])
        self.assertEqual(p['verified_specifications'],[])
    def test_telephone_cat6_is_quarantined_for_review(self):
        p=self.product();p['name']='کیستون تلفن Cat6 UTP'
        row=self.manifest([p])['products'][0]
        self.assertIn('telephone-category-conflict',row['review_flags'])
        self.assertEqual(row['status'],'draft')
    def test_official_category_parentage_is_preserved(self):
        m=self.catalog().build_manifest([self.product()],[{'id':1,'name':'کابل','slug':'cable','parent':2},{'id':2,'name':'پسیو','slug':'passive','parent':0}])
        self.assertEqual(m['categories'][0]['parent'],2)
    def test_manifest_is_deterministic_and_does_not_mutate_input(self):
        rows=[self.product()];before=copy.deepcopy(rows)
        one=self.manifest(rows);two=self.manifest(rows)
        self.assertEqual(one,two);self.assertEqual(rows,before)

if __name__=='__main__':unittest.main(verbosity=2)
