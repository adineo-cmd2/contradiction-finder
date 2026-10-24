"""Explain a contradiction: first-sentence claims + severity map."""

import re
from typing import Literal

Severity = Literal["minor", "factual", "fundamental"]

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _first_sentence(text: str) -> str:
    stripped = (text or "").strip().replace("\n", " ")
    if not stripped:
        return ""
    parts = _SENT_SPLIT.split(stripped)
    claim = parts[0].strip() if parts else stripped
    return claim[:200]


def _severity(confidence: float) -> Severity:
    if confidence >= 0.8:
        return "fundamental"
    if confidence >= 0.65:
        return "factual"
    return "minor"


def explain(a_text: str, b_text: str, confidence: float) -> dict:
    claim_a = _first_sentence(a_text)
    claim_b = _first_sentence(b_text)
    severity = _severity(float(confidence or 0.0))
    explanation = (
        f"The passages clash: '{claim_a}' conflicts with '{claim_b}' "
        f"(confidence {float(confidence or 0.0):.2f}). "
        "Please verify both passages against primary sources."
    )
    return {
        "claim_a": claim_a,
        "claim_b": claim_b,
        "severity": severity,
        "explanation": explanation,
    }
