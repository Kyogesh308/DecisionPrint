"""
Private: loads and chunks source documents for the baseline RAG.
Not a Hindsight memory stack — eval-only, in-process, no persistence.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("decisionprint.eval.chunker")

CHUNK_SIZE_WORDS = 150       # target words per chunk
CHUNK_OVERLAP_WORDS = 30     # overlap between adjacent chunks


@dataclass
class Chunk:
    text: str
    source_path: str         # relative path within data_dir
    chunk_index: int
    word_count: int


def load_chunks(data_dir: str) -> list[Chunk]:
    """
    Recursively load all .md and .txt files under data_dir and
    split them into overlapping word-window chunks.

    Returns an empty list (not an error) if data_dir is empty or missing.
    """
    root = Path(data_dir)
    if not root.exists():
        logger.warning("load_chunks: data_dir '%s' does not exist", data_dir)
        return []

    chunks: list[Chunk] = []
    for path in sorted(root.rglob("*")):
        if path.suffix not in (".md", ".txt"):
            continue
        if "gold" in path.parts:
            continue          # skip gold label files — they are answers, not evidence

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.warning("load_chunks: could not read '%s': %s", path, exc)
            continue

        rel = str(path.relative_to(root))
        file_chunks = _split_into_chunks(text, rel)
        chunks.extend(file_chunks)

    logger.info("load_chunks: loaded %d chunks from %d-file scan of '%s'",
                len(chunks), sum(1 for _ in root.rglob("*.md")) + sum(1 for _ in root.rglob("*.txt")),
                data_dir)
    return chunks


def _split_into_chunks(text: str, source_path: str) -> list[Chunk]:
    """
    Split text into overlapping word-window chunks.
    Window: CHUNK_SIZE_WORDS words, step: CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS words.
    """
    words = text.split()
    if not words:
        return []

    step = max(1, CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS)
    chunks = []
    idx = 0

    for start in range(0, len(words), step):
        window = words[start : start + CHUNK_SIZE_WORDS]
        if len(window) < 10:
            break      # skip tiny trailing fragments
        chunks.append(Chunk(
            text=" ".join(window),
            source_path=source_path,
            chunk_index=idx,
            word_count=len(window),
        ))
        idx += 1

    return chunks
