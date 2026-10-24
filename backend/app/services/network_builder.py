"""Document-level contradiction network."""


def _resolve_doc(chunk_id, chunk_to_doc):
    if not chunk_to_doc or chunk_id not in chunk_to_doc:
        return None
    val = chunk_to_doc[chunk_id]
    if isinstance(val, dict):
        return val.get("id")
    return val


def _doc_label(doc_id, chunk_to_doc):
    if chunk_to_doc:
        for val in chunk_to_doc.values():
            if isinstance(val, dict) and val.get("id") == doc_id and val.get("label"):
                return val["label"]
    return f"Doc {doc_id}"


def _doc_pair(rec: dict | object, chunk_to_doc: dict | None = None) -> tuple | None:
    if isinstance(rec, dict):
        if "doc_a" in rec and "doc_b" in rec:
            return (rec["doc_a"], rec["doc_b"])
        if "a" in rec and "b" in rec and chunk_to_doc is None:
            return (rec["a"], rec["b"])
        if "doc_a_id" in rec and "doc_b_id" in rec:
            return (rec["doc_a_id"], rec["doc_b_id"])
        for a_key, b_key in (
            ("chunk_a_id", "chunk_b_id"),
            ("chunk_a", "chunk_b"),
            ("a_id", "b_id"),
        ):
            if a_key in rec and b_key in rec:
                if chunk_to_doc is None:
                    continue
                da = _resolve_doc(rec[a_key], chunk_to_doc)
                db = _resolve_doc(rec[b_key], chunk_to_doc)
                if da is not None and db is not None:
                    return (da, db)
                return None
        # "a"/"b" with a map present means chunk ids.
        if chunk_to_doc is not None and "a" in rec and "b" in rec:
            da = _resolve_doc(rec["a"], chunk_to_doc)
            db = _resolve_doc(rec["b"], chunk_to_doc)
            if da is not None and db is not None:
                return (da, db)
            return None
        return None
    for a_attr, b_attr in (("doc_a", "doc_b"), ("a", "b")):
        if hasattr(rec, a_attr) and hasattr(rec, b_attr):
            return (getattr(rec, a_attr), getattr(rec, b_attr))
    if chunk_to_doc is not None:
        for a_attr, b_attr in (("chunk_a_id", "chunk_b_id"),):
            if hasattr(rec, a_attr) and hasattr(rec, b_attr):
                da = _resolve_doc(getattr(rec, a_attr), chunk_to_doc)
                db = _resolve_doc(getattr(rec, b_attr), chunk_to_doc)
                if da is not None and db is not None:
                    return (da, db)
                return None
    return None


def build(records: list, chunk_to_doc: dict | None = None) -> dict:
    counts: dict = {}
    edge_counts: dict[tuple, int] = {}
    for rec in records:
        pair = _doc_pair(rec, chunk_to_doc)
        if not pair:
            continue
        a, b = pair
        counts[a] = counts.get(a, 0) + 1
        counts[b] = counts.get(b, 0) + 1
        key = tuple(sorted((a, b)))
        edge_counts[key] = edge_counts.get(key, 0) + 1
    nodes = [
        {"id": doc_id, "label": _doc_label(doc_id, chunk_to_doc), "count": c}
        for doc_id, c in sorted(counts.items())
    ]
    edges = [{"a": a, "b": b, "count": c} for (a, b), c in sorted(edge_counts.items())]
    return {"nodes": nodes, "edges": edges}
