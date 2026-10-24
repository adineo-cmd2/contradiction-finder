"""Paragraph-aware chunker: split on blank lines, merge tiny ones.

Target ~200 words per chunk with 30-word overlap between consecutive chunks.
Short text yields a single chunk.
"""

import re

CHUNK_WORDS = 200
OVERLAP_WORDS = 30
MIN_PARA_WORDS = 30
MIN_TAIL_WORDS = 50


def _merge_tiny_paragraphs(paras: list[str]) -> list[str]:
    merged: list[str] = []
    for p in paras:
        if merged and (
            len(merged[-1].split()) < MIN_PARA_WORDS or len(p.split()) < MIN_PARA_WORDS
        ):
            merged[-1] = f"{merged[-1]} {p}"
        else:
            merged.append(p)
    # If first para was tiny and alone, it stays; merge forward pass for leading tiny
    if len(merged) >= 2 and len(merged[0].split()) < MIN_PARA_WORDS:
        merged[1] = f"{merged[0]} {merged[1]}"
        merged.pop(0)
    return merged


def chunk_text(text: str) -> list[str]:
    stripped = (text or "").strip()
    if not stripped:
        return []
    paras = [p.strip() for p in re.split(r"\n\s*\n", stripped) if p.strip()]
    if not paras:
        return []
    paras = _merge_tiny_paragraphs(paras)
    words: list[str] = []
    for i, p in enumerate(paras):
        words.extend(p.split())
    if len(words) <= CHUNK_WORDS:
        return [" ".join(words)]
    chunks: list[str] = []
    starts: list[int] = []
    step = CHUNK_WORDS - OVERLAP_WORDS
    for start in range(0, len(words), step):
        piece = words[start : start + CHUNK_WORDS]
        if not piece:
            break
        chunks.append(" ".join(piece))
        starts.append(start)
        if start + CHUNK_WORDS >= len(words):
            break
    if len(chunks) >= 2 and len(chunks[-1].split()) < MIN_TAIL_WORDS:
        chunks[-2] = " ".join(words[starts[-2] :])
        chunks.pop()
    return chunks
