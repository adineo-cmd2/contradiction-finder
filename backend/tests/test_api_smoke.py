"""Smoke: corpus -> upload A/B -> analyse -> list -> detail -> network."""

from fastapi.testclient import TestClient

from app.main import app

DOC_A = (
    "Coffee is healthy. Studies show coffee extends life. "
    "Coffee research studies show coffee is safe and good for life and health. "
    "Coffee extends life and health."
)

DOC_B = (
    "Coffee is dangerous. Research proves coffee shortens life. "
    "Coffee research studies show coffee is dangerous and bad for life and health. "
    "Coffee does not extend life and health suffers."
)


def test_api_smoke():
    c = TestClient(app)

    r = c.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    r = c.post("/api/corpus", json={"name": "coffee"})
    assert r.status_code == 200
    corpus_id = r.json()["corpus_id"]

    for fname, text in (("docA.txt", DOC_A), ("docB.txt", DOC_B)):
        r = c.post(
            f"/api/corpus/{corpus_id}/upload",
            files={"file": (fname, text.encode("utf-8"), "text/plain")},
        )
        assert r.status_code == 200

    r = c.post(f"/api/corpus/{corpus_id}/analyse")
    assert r.status_code == 200
    assert r.json()["contradictions_found"] >= 1

    r = c.get("/api/contradictions", params={"corpus_id": corpus_id})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert len(body["items"]) >= 1
    first = body["items"][0]
    assert {"id", "doc_a", "doc_b", "severity", "confidence", "summary"} <= set(first)

    rid = first["id"]
    r = c.get(f"/api/contradictions/{rid}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["id"] == rid
    assert detail["text_a"]
    assert detail["text_b"]

    r = c.get(
        "/api/contradictions/network", params={"corpus_id": corpus_id}
    )
    assert r.status_code == 200
    net = r.json()
    assert len(net["nodes"]) >= 1
    assert len(net["edges"]) >= 1
