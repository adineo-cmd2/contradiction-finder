"""Candidate generation: top-K cross-doc cosine + same-doc pairs, NLI filter."""

from app.services.embedder import cosine
from app.services.nli_classifier import classify


def detect(chunks: list[dict], k: int = 3, cos_thresh: float = 0.35, nli_keep: float = 0.5) -> list[dict]:
    by_id: dict = {c["id"]: c for c in chunks}
    candidates: dict[tuple, dict] = {}

    # Cross-doc: for each chunk, top-k cosine partners from OTHER docs.
    for c in chunks:
        scored = []
        for o in chunks:
            if o["id"] == c["id"]:
                continue
            if o["document_id"] == c["document_id"]:
                continue
            sim = cosine(c.get("embedding") or [], o.get("embedding") or [])
            if sim >= cos_thresh:
                scored.append((sim, o))
        scored.sort(key=lambda t: t[0], reverse=True)
        for _, o in scored[:k]:
            key = tuple(sorted((c["id"], o["id"])))
            if key not in candidates:
                candidates[key] = {"a_id": key[0], "b_id": key[1]}

    # Same-doc: all pairs above threshold.
    doc_groups: dict = {}
    for c in chunks:
        doc_groups.setdefault(c["document_id"], []).append(c)
    for group in doc_groups.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                sim = cosine(a.get("embedding") or [], b.get("embedding") or [])
                if sim >= cos_thresh:
                    key = tuple(sorted((a["id"], b["id"])))
                    if key not in candidates:
                        candidates[key] = {"a_id": key[0], "b_id": key[1]}

    results: list[dict] = []
    for key, pair in candidates.items():
        a = by_id[pair["a_id"]]
        b = by_id[pair["b_id"]]
        res = classify(a.get("text", ""), b.get("text", ""))
        if res["label"] == "CONTRADICTION" and res["confidence"] >= nli_keep:
            results.append(
                {
                    "a_id": pair["a_id"],
                    "b_id": pair["b_id"],
                    "confidence": res["confidence"],
                    "same_doc": a["document_id"] == b["document_id"],
                }
            )
    results.sort(key=lambda r: r["confidence"], reverse=True)
    return results
