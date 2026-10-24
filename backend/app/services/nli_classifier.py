"""Mock NLI classifier: token overlap + polarity flip."""

import os
import re

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_NUMBER_RE = re.compile(r"\d+")

NEGATION_CUES = {"not", "no", "never", "cannot", "without", "none", "neither"}

ANTONYM_PAIRS: list[tuple[str, str]] = [
    ("increase", "decrease"),
    ("rise", "fall"),
    ("always", "never"),
    ("all", "none"),
    ("true", "false"),
    ("hot", "cold"),
    ("up", "down"),
    ("more", "less"),
    ("higher", "lower"),
    ("faster", "slower"),
    ("safe", "dangerous"),
    ("legal", "illegal"),
    ("effective", "ineffective"),
    ("causes", "prevents"),
    ("good", "bad"),
    ("positive", "negative"),
    ("growth", "decline"),
    ("success", "failure"),
    ("before", "after"),
    ("early", "late"),
    ("open", "closed"),
    ("possible", "impossible"),
    ("present", "absent"),
    ("include", "exclude"),
]


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall((text or "").lower()))


def _has_negation(raw: str, toks: set[str]) -> bool:
    low = (raw or "").lower()
    if "n't" in low:
        return True
    return bool(toks & NEGATION_CUES)


def _antonym_split(a: set[str], b: set[str]) -> bool:
    for w1, w2 in ANTONYM_PAIRS:
        if (w1 in a and w2 in b) or (w2 in a and w1 in b):
            return True
    return False


def _number_mismatch(a_raw: str, b_raw: str, overlap: float) -> bool:
    if overlap < 0.4:
        return False
    na = set(_NUMBER_RE.findall(a_raw or ""))
    nb = set(_NUMBER_RE.findall(b_raw or ""))
    return bool(na and nb and na != nb)


def classify(a: str, b: str) -> dict:
    ta = _tokens(a)
    tb = _tokens(b)
    union = ta | tb
    overlap = len(ta & tb) / len(union) if union else 0.0

    neg_a = _has_negation(a, ta)
    neg_b = _has_negation(b, tb)
    neg_flip = neg_a ^ neg_b
    antonym_flip = _antonym_split(ta, tb)
    strong_flip = neg_flip or antonym_flip
    weak_flip = _number_mismatch(a or "", b or "", overlap)
    flip = strong_flip or weak_flip

    if strong_flip and overlap >= 0.25:
        return {"label": "CONTRADICTION", "confidence": min(0.9, 0.55 + 0.3 * overlap)}
    if not flip and overlap >= 0.5:
        return {"label": "ENTAILMENT", "confidence": 0.5 + 0.3 * overlap}
    if weak_flip and overlap >= 0.25:
        return {"label": "CONTRADICTION", "confidence": 0.5}
    return {"label": "NEUTRAL", "confidence": 0.4}


def classify_llm(a: str, b: str) -> dict:
    """LLM confirm hook: returns rule-based classify when no keys present."""
    if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
        return classify(a, b)
    return classify(a, b)
