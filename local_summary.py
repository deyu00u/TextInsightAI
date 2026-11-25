"""Extractive summarization using a pretrained neural sentence embedding model."""
import re
from functools import lru_cache
from pathlib import Path
import numpy as np
from analysis_utils import MAX_AI_CHARS

MODEL_NAME = 'BAAI/bge-small-en-v1.5'
CACHE_DIR = Path(__file__).resolve().parent / '.model_cache'

@lru_cache(maxsize=1)
def load_model():
    from fastembed import TextEmbedding
    CACHE_DIR.mkdir(exist_ok=True)
    try:
        return TextEmbedding(model_name=MODEL_NAME, cache_dir=str(CACHE_DIR), local_files_only=True)
    except Exception:
        return TextEmbedding(model_name=MODEL_NAME, cache_dir=str(CACHE_DIR))


def split_sentences(text):
    pieces = re.split(r'(?<=[.!?])\s+|\n\s*\n', text.strip())
    return list(dict.fromkeys(re.sub(r'\s+', ' ', part).strip() for part in pieces if re.search(r'\w', part)))


def select_sentences(sentences, embeddings, limit):
    vectors = np.asarray(embeddings, dtype=float)
    if vectors.ndim != 2 or len(vectors) != len(sentences):
        raise ValueError('Unexpected embedding dimensions.')
    vectors = vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-12)
    centroid = vectors.mean(axis=0)
    centroid /= max(np.linalg.norm(centroid), 1e-12)
    relevance = vectors @ centroid
    chosen = []
    remaining = set(range(len(sentences)))
    while remaining and len(chosen) < limit:
        def score(i):
            similarity = max((float(vectors[i] @ vectors[j]) for j in chosen), default=0.0)
            return (0.75 * relevance[i] - 0.25 * max(0., similarity), -i)
        best = max(remaining, key=score)
        chosen.append(best)
        remaining.remove(best)
    return [sentences[i] for i in sorted(chosen)]


def generate_summary(text, length='Balanced'):
    if len(text) > MAX_AI_CHARS:
        raise ValueError('Input exceeds 40,000 characters. Select a shorter excerpt.')
    sentences = split_sentences(text)
    if not sentences:
        raise ValueError('No readable sentences found.')
    max_sentences = {'Short': 2, 'Balanced': 4, 'Detailed': 7}[length]
    # Keep the summary shorter than the source when multiple sentences exist.
    count = min(max_sentences, max(1, (len(sentences) + 1) // 2))
    model = load_model()
    embeddings = list(model.embed(sentences, batch_size=16))
    return ' '.join(select_sentences(sentences, embeddings, count))
