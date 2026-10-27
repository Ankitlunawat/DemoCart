import csv
import io
import json
import unittest
from pathlib import Path
from analytics import load_products, filter_products, summarize, to_csv, to_json

DATA = Path(__file__).resolve().parents[1] / 'output' / 'products.csv'

class DemoCartDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_products(DATA)

    def test_60_unique_products_on_five_pages(self):
        result = summarize(self.rows)
        self.assertEqual(result['products'], 60)
        self.assertEqual(result['unique_skus'], 60)
        self.assertEqual(len(result['source_pages']), 5)
        self.assertEqual(len(result['categories']), 5)

    def test_search_filters_by_sku_and_name(self):
        self.assertEqual([x['sku'] for x in filter_products(self.rows, search='SKU-0001')], ['SKU-0001'])
        self.assertTrue(filter_products(self.rows, search='Atlas'))
        self.assertEqual(filter_products(self.rows, search='not-a-product'), [])

    def test_category_stock_price_rating_filter_combination(self):
        matched = filter_products(self.rows, categories=['Audio'], availability='In Stock',
                                  min_price=500, max_price=1400, min_rating=3.5)
        self.assertTrue(matched)
        for row in matched:
            self.assertEqual(row['category'],'Audio')
            self.assertEqual(row['availability'],'In Stock')
            self.assertTrue(500 <= row['price_inr'] <= 1400)
            self.assertGreaterEqual(row['rating'],3.5)

    def test_filtered_csv_json_round_trip(self):
        matched = filter_products(self.rows, categories=['Gaming'])
        data = list(csv.DictReader(io.StringIO(to_csv(matched).decode('utf-8-sig'))))
        self.assertEqual(len(data),len(matched))
        self.assertEqual([x['sku'] for x in data], [x['sku'] for x in matched])
        self.assertEqual(json.loads(to_json(matched).decode('utf-8')), matched)

    def test_empty_selection_has_safe_kpis(self):
        self.assertEqual(summarize([])['avg_price_inr'], 0)
        self.assertEqual(to_csv([]).decode('utf-8-sig').splitlines()[0], 'sku,product_name,category,price_inr,rating,availability,source_page')

    def test_duplicate_or_bad_data_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            with open(Path(folder)/'bad.csv','w',newline='',encoding='utf-8') as f:
                with open(DATA,encoding='utf-8-sig',newline='') as original:
                    f.write(original.read())
                f.write('\nSKU-0001,Duplicated,Audio,200,4,In Stock,page-1.html')
            with self.assertRaises(ValueError):load_products(Path(folder)/'bad.csv')

if __name__ == '__main__': unittest.main()