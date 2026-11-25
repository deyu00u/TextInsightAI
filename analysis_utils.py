"""Local document extraction and descriptive statistics."""
import re
from collections import Counter

STOPWORDS = set('the a an and or but in on at to for of with by as it this that these those is are was were be been being from has have had he she they them their his her we our you your i me my not can could will would should do does did if then than so such about into also which who what when where why how there here its very more most some any each other only all both through up out no nor just while because'.split())
WORD_PATTERN = r"[^\W_]+(?:['’\-][^\W_]+)*"
MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_AI_CHARS = 40000


def extract_pdf_text(data):
    import pymupdf as fitz
    if len(data) > MAX_PDF_BYTES:
        raise ValueError('PDF exceeds the 20 MB limit.')
    with fitz.open(stream=data, filetype='pdf') as doc:
        if doc.needs_pass:
            raise ValueError('Password-protected PDFs are not supported.')
        pages = [page.get_text(sort=True).strip() for page in doc]
    if not any(pages):
        raise ValueError('No selectable text found. Scanned PDFs require OCR, which is not included.')
    return '\n\n'.join(p for p in pages if p), len(pages), sum(not bool(p) for p in pages)


def analyze_text(text, exclude_stopwords=True):
    words = re.findall(WORD_PATTERN, text.casefold())
    sentences = [s for s in re.split(r'[.!?]+(?:\s+|$)', text.strip()) if re.search(r'\w', s)]
    paragraphs = [p for p in re.split(r'\n\s*\n', text.strip()) if p.strip()]
    filtered = [w for w in words if not exclude_stopwords or (w not in STOPWORDS and len(w) > 1)]
    return {'words': len(words), 'characters': len(text), 'characters_no_spaces': len(re.sub(r'\s', '', text)), 'sentences': len(sentences), 'paragraphs': len(paragraphs), 'frequent_words': Counter(filtered).most_common(10)}


