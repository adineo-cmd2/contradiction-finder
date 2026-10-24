from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.contradiction_record import ContradictionRecord
from app.models.corpus import Corpus
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User

router = APIRouter()


@router.get("/{doc_id}")
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    corpus = (
        db.query(Corpus)
        .filter(Corpus.id == doc.corpus_id, Corpus.user_id == user.id)
        .first()
    )
    if corpus is None:
        raise HTTPException(status_code=404, detail="document not found")
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == doc.id)
        .order_by(DocumentChunk.idx)
        .all()
    )
    text = "\n\n".join(c.text or "" for c in chunks)
    chunk_ids = {c.id for c in chunks}
    records = (
        db.query(ContradictionRecord)
        .filter(ContradictionRecord.corpus_id == doc.corpus_id)
        .all()
    )
    flags = []
    for r in records:
        if not r.same_doc:
            continue
        if r.chunk_a_id in chunk_ids and r.chunk_b_id in chunk_ids:
            flags.append(
                {"snippet": (r.claim_a or "")[:200], "severity": r.severity}
            )
    return {"id": doc.id, "filename": doc.filename, "text": text, "flags": flags}
