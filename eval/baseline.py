"""
Baseline RAG: simple in-memory TF-IDF retrieval over data/ documents.
This is an eval-only comparison baseline — NOT a product component.
It must never be imported by intelligence/, facade/, ui/, or store/.
"""
from __future__ import annotations

import logging
import math
import re
from collections import Counter

from eval._chunker import Chunk, load_chunks

logger = logging.getLogger("decisionprint.eval.baseline")

# Module-level chunk cache — loaded once per process run, keyed by data_dir
_chunk_cache: dict[str, list[Chunk]] = {}


def run_baseline_rag(question: str, *, data_dir: str = "./data", top_k: int = 3) -> str:
    """
    Retrieve top_k document chunks most relevant to question using TF-IDF,
    then concatenate them as a single string answer.

    Returns an empty string if no chunks are available.
    This function is eval-only — it must not be called from any product code path.
    """
    chunks = _get_chunks(data_dir)
    if not chunks:
        logger.warning("run_baseline_rag: no chunks loaded from '%s'", data_dir)
        return ""

    scores = _score_chunks(question, chunks)
    top_chunks = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]

    if not top_chunks:
        return ""

    parts = []
    for chunk, score in top_chunks:
        parts.append(f"[Source: {chunk.source_path}]\n{chunk.text}")
    return "\n\n---\n\n".join(parts)


# --------------------------------------------------------------------------- #
# TF-IDF                                                                        #
# --------------------------------------------------------------------------- #

def _get_chunks(data_dir: str) -> list[Chunk]:
    """Load from cache or disk."""
    if data_dir not in _chunk_cache:
        _chunk_cache[data_dir] = load_chunks(data_dir)
    return _chunk_cache[data_dir]


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    return re.findall(r"\b[a-z]{2,}\b", text.lower())


def _score_chunks(query: str, chunks: list[Chunk]) -> list[tuple[Chunk, float]]:
    """
    Score each chunk against the query using TF-IDF cosine similarity.
    Pure Python, no external ML dependencies.
    """
    query_tokens = _tokenize(query)
    if not query_tokens:
        return [(c, 0.0) for c in chunks]

    # Build document-frequency index over all chunks
    n_docs = len(chunks)
    doc_freq: Counter = Counter()
    tokenized_chunks: list[list[str]] = []
    for chunk in chunks:
        tokens = _tokenize(chunk.text)
        tokenized_chunks.append(tokens)
        doc_freq.update(set(tokens))

    def idf(term: str) -> float:
        df = doc_freq.get(term, 0)
        if df == 0:
            return 0.0
        return math.log((n_docs + 1) / (df + 1)) + 1.0   # smoothed IDF

    def tf_idf_vector(tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        total = max(len(tokens), 1)
        return {term: (count / total) * idf(term) for term, count in tf.items()}

    def cosine(v1: dict[str, float], v2: dict[str, float]) -> float:
        common = set(v1) & set(v2)
        if not common:
            return 0.0
        dot = sum(v1[t] * v2[t] for t in common)
        mag1 = math.sqrt(sum(x * x for x in v1.values()))
        mag2 = math.sqrt(sum(x * x for x in v2.values()))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)

    query_vec = tf_idf_vector(query_tokens)
    results = []
    for chunk, tokens in zip(chunks, tokenized_chunks):
        chunk_vec = tf_idf_vector(tokens)
        score = cosine(query_vec, chunk_vec)
        results.append((chunk, score))

    return results


def clear_chunk_cache() -> None:
    """Clear the in-process chunk cache. Call from tests to reset state."""
    _chunk_cache.clear()
