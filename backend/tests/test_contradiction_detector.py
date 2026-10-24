from app.services.contradiction_detector import detect
from app.services.contradiction_explainer import explain
from app.services.embedder import embed
from app.services.network_builder import build


def _chunk(cid, doc_id, text):
    return {"id": cid, "document_id": doc_id, "text": text, "embedding": embed(text)}


def test_two_opposing_docs_yield_cross_doc_record():
    doc_a = [
        "Global climate policy and fossil fuel use shape economic growth worldwide. "
        "Fossil fuels drive energy security and support economic growth across nations.\n\n"
        "Governments should increase fossil fuel subsidies to ensure energy security. "
        "Economic growth depends on reliable fossil fuel supply and energy security.",
        "Global climate policy must increase fossil fuel investment for energy security. "
        "Fossil fuel supply ensures economic growth and stable energy security worldwide.",
    ]
    doc_b = [
        "Global climate policy and fossil fuel use shape economic growth worldwide. "
        "Fossil fuels do not drive energy security and harm economic growth across nations.\n\n"
        "Governments should decrease fossil fuel subsidies to protect energy security. "
        "Economic growth does not depend on fossil fuel supply and energy security suffers.",
        "Global climate policy must decrease fossil fuel investment for energy security. "
        "Fossil fuel supply does not ensure economic growth and threatens energy security worldwide.",
    ]
    chunks = []
    cid = 1
    for t in doc_a:
        chunks.append(_chunk(cid, 1, t))
        cid += 1
    for t in doc_b:
        chunks.append(_chunk(cid, 2, t))
        cid += 1

    results = detect(chunks)
    assert len(results) >= 1
    cross = [r for r in results if r["same_doc"] is False]
    assert len(cross) >= 1
    by_id = {c["id"]: c for c in chunks}
    for r in cross:
        info = explain(by_id[r["a_id"]]["text"], by_id[r["b_id"]]["text"], r["confidence"])
        assert info["claim_a"]
        assert info["claim_b"]
        assert info["severity"] in {"minor", "factual", "fundamental"}


def test_single_doc_internal_conflict_flagged_same_doc():
    t1 = (
        "Global climate policy and fossil fuel use shape economic growth worldwide. "
        "Governments should increase fossil fuel subsidies to ensure energy security."
    )
    t2 = (
        "Global climate policy and fossil fuel use shape economic growth worldwide. "
        "Governments should decrease fossil fuel subsidies since they harm energy security."
    )
    chunks = [_chunk(11, 5, t1), _chunk(12, 5, t2)]
    results = detect(chunks)
    same = [r for r in results if r["same_doc"] is True]
    assert len(same) >= 1


def test_network_builder_resolves_chunk_ids_via_map():
    # run_analysis-style records carry chunk ids, not doc ids.
    records = [
        {"chunk_a_id": 101, "chunk_b_id": 202},
        {"chunk_a_id": 202, "chunk_b_id": 303},
    ]
    chunk_to_doc = {
        101: {"id": 1, "label": "a.txt"},
        202: {"id": 2, "label": "b.txt"},
        303: {"id": 3, "label": "c.txt"},
    }
    net = build(records, chunk_to_doc)
    assert len(net["nodes"]) == 3
    assert len(net["edges"]) == 2


def test_network_builder_backward_compat_doc_keys():
    net = build([{"doc_a": 1, "doc_b": 2}, {"doc_a": 1, "doc_b": 2}])
    assert len(net["nodes"]) == 2
    assert net["edges"] == [{"a": 1, "b": 2, "count": 2}]
