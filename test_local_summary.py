import unittest
from unittest.mock import patch
from local_summary import split_sentences, select_sentences, generate_summary

class LocalSummaryTests(unittest.TestCase):
    def test_split(self):
        self.assertEqual(split_sentences('Rice grows.\nRice grows. Farmers harvest it!'), ['Rice grows.', 'Farmers harvest it!'])
    def test_rank_source_order(self):
        self.assertEqual(select_sentences(['A', 'B', 'C'], [[1, 0], [1, 0], [0, 1]], 2), ['A', 'B'])
    def test_mocked_model(self):
        with patch('local_summary.load_model') as model:
            model.return_value.embed.return_value = [[1, 0], [1, 0], [0, 1]]
            self.assertEqual(generate_summary('Rice grows. Rice feeds people. Birds fly.'), 'Rice grows. Rice feeds people.')
    def test_empty(self):
        with self.assertRaises(ValueError):
            generate_summary('')
