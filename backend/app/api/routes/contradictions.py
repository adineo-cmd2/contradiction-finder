from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.contradiction_record import ContradictionRecord
from app.models.corpus import Corpus
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.services.network_builder import build

router = APIRouter()


def _own_corpus(db: Session, user_id: int, corpus_id: int) -> Corpus:
    corpus = (
        db.query(Corpus)
        .filter(Corpus.id == corpus_id, Corpus.user_id == user_id)
        .first()
    )
    if corpus is None:
        raise HTTPException(status_code=404, detail="corpus not found")
    return corpus


def _chunk_maps(db: Session, corpus_id: int):
    docs = db.query(Document).filter(Document.corpus_id == corpus_id).all()
    doc_names = {d.id: d.filename for d in docs}
    doc_ids = list(doc_names)
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id.in_(doc_ids))
        .all()
        if doc_ids
        else []
    )
    chunk_to_doc = {
        c.id: {"id": c.document_id, "label": doc_names.get(c.document_id, "")}
        for c in chunks
    }
    chunk_text = {c.id: c.text or "" for c in chunks}
    return doc_names, chunk_to_doc, chunk_text


@router.get("/network")
def network(
    corpus_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _own_corpus(db, user.id, corpus_id)
    _doc_names, chunk_to_doc, _texts = _chunk_maps(db, corpus_id)
    records = (
        db.query(ContradictionRecord)
        .filter(ContradictionRecord.corpus_id == corpus_id)
        .order_by(ContradictionRecord.id)
        .all()
    )
    dicts = [
        {"chunk_a_id": r.chunk_a_id, "chunk_b_id": r.chunk_b_id} for r in records
    ]
    return build(dicts, chunk_to_doc)


@router.get("")
def list_contradictions(
    corpus_id: int,
    severity: str | None = None,
    doc: int | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _own_corpus(db, user.id, corpus_id)
    doc_names, _m, _t = _chunk_maps(db, corpus_id)
    doc_ids = list(doc_names)
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id.in_(doc_ids))
        .all()
        if doc_ids
        else []
    )
    chunk_to_doc_id = {c.id: c.document_id for c in chunks}

    q = (
        db.query(ContradictionRecord)
        .filter(ContradictionRecord.corpus_id == corpus_id)
        .order_by(ContradictionRecord.confidence.desc())
    )
    if severity:
        q = q.filter(ContradictionRecord.severity == severity)
    records = q.all()
    if doc is not None:
        records = [
            r
            for r in records
            if chunk_to_doc_id.get(r.chunk_a_id) == doc
            or chunk_to_doc_id.get(r.chunk_b_id) == doc
        ]
    total = len(records)
    page = max(1, page)
    page_size = max(1, min(100, page_size))
    sliced = records[(page - 1) * page_size : page * page_size]
    items = []
    for r in sliced:
        da = chunk_to_doc_id.get(r.chunk_a_id)
        dbb = chunk_to_doc_id.get(r.chunk_b_id)
        items.append(
            {
                "id": r.id,
                "doc_a": doc_names.get(da, ""),
                "doc_b": doc_names.get(dbb, ""),
                "doc_a_id": da,
                "doc_b_id": dbb,
                "severity": r.severity,
                "confidence": r.confidence,
                "summary": r.explanation or f"{r.claim_a} / {r.claim_b}",
            }
        )
    return {"items": items, "total": total}


@router.get("/{record_id}")
def get_contradiction(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = db.query(ContradictionRecord).filter(ContradictionRecord.id == record_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="contradiction not found")
    _own_corpus(db, user.id, r.corpus_id)
    doc_names, _m, texts = _chunk_maps(db, r.corpus_id)
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.id.in_([r.chunk_a_id, r.chunk_b_id]))
        .all()
    )
    by_id = {c.id: c for c in chunks}
    ca = by_id.get(r.chunk_a_id)
    cb = by_id.get(r.chunk_b_id)
    da = ca.document_id if ca else None
    dbb = cb.document_id if cb else None
    return {
        "id": r.id,
        "corpus_id": r.corpus_id,
        "severity": r.severity,
        "confidence": r.confidence,
        "claim_a": r.claim_a,
        "claim_b": r.claim_b,
        "explanation": r.explanation,
        "same_doc": r.same_doc,
        "doc_a": doc_names.get(da, ""),
        "doc_b": doc_names.get(dbb, ""),
        "doc_a_id": da,
        "doc_b_id": dbb,
        "text_a": texts.get(r.chunk_a_id, ""),
        "text_b": texts.get(r.chunk_b_id, ""),
    }
