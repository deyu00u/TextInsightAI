import unittest
import pymupdf as fitz
from analysis_utils import analyze_text, extract_pdf_text

class TextTests(unittest.TestCase):
    def test_counts(self):
        r = analyze_text('Rice grows. Rice feeds people!\n\nFarmers grow rice.')
        self.assertEqual(r['words'], 8)
        self.assertEqual(r['sentences'], 3)
        self.assertEqual(r['paragraphs'], 2)
        self.assertEqual(r['frequent_words'][0], ('rice', 3))
    def test_empty(self):
        self.assertEqual(analyze_text('')['words'], 0)
    def test_filter(self):
        self.assertEqual(analyze_text('the the rice')['frequent_words'], [('rice', 1)])
        self.assertEqual(analyze_text('the the rice', False)['frequent_words'][0], ('the', 2))
    def test_pdf(self):
        with fitz.open() as doc:
            doc.new_page().insert_text((72,72), 'Rice grows in fields.')
            doc.new_page()
            data = doc.tobytes()
        text, pages, empty = extract_pdf_text(data)
        self.assertIn('Rice grows in fields.', text)
        self.assertEqual((pages, empty), (2, 1))
    def test_blank_pdf(self):
        with fitz.open() as doc:
            doc.new_page()
            data = doc.tobytes()
        with self.assertRaisesRegex(ValueError, 'No selectable text'):
            extract_pdf_text(data)

if __name__ == '__main__':
    unittest.main()
