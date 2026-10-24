from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.contradiction_record import ContradictionRecord
from app.models.corpus import Corpus
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.schemas.corpus import CorpusCreate
from app.services.ingestion_pipeline import ingest_file, run_analysis

router = APIRouter()

_ALLOWED = {".txt", ".md", ".pdf", ".docx"}


def _own_corpus(db: Session, user_id: int, corpus_id: int) -> Corpus:
    corpus = (
        db.query(Corpus)
        .filter(Corpus.id == corpus_id, Corpus.user_id == user_id)
        .first()
    )
    if corpus is None:
        raise HTTPException(status_code=404, detail="corpus not found")
    return corpus


@router.post("")
def create_corpus(
    body: CorpusCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    corpus = Corpus(user_id=user.id, name=body.name)
    db.add(corpus)
    db.commit()
    db.refresh(corpus)
    return {"corpus_id": corpus.id}


@router.get("")
def list_corpora(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    corpora = (
        db.query(Corpus)
        .filter(Corpus.user_id == user.id)
        .order_by(Corpus.id)
        .all()
    )
    out = []
    for c in corpora:
        docs = db.query(Document).filter(Document.corpus_id == c.id).count()
        analysed = (
            db.query(ContradictionRecord)
            .filter(ContradictionRecord.corpus_id == c.id)
            .count()
            > 0
        )
        out.append(
            {
                "id": c.id,
                "name": c.name,
                "docs": docs,
                "analysed": analysed,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
        )
    return out


@router.delete("/{corpus_id}")
def delete_corpus(
    corpus_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    corpus = _own_corpus(db, user.id, corpus_id)
    doc_ids = [
        row[0]
        for row in db.query(Document.id)
        .filter(Document.corpus_id == corpus.id)
        .all()
    ]
    if doc_ids:
        db.query(ContradictionRecord).filter(
            ContradictionRecord.corpus_id == corpus.id
        ).delete(synchronize_session=False)
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id.in_(doc_ids)
        ).delete(synchronize_session=False)
        db.query(Document).filter(Document.id.in_(doc_ids)).delete(
            synchronize_session=False
        )
    else:
        db.query(ContradictionRecord).filter(
            ContradictionRecord.corpus_id == corpus.id
        ).delete(synchronize_session=False)
    db.delete(corpus)
    db.commit()
    return {"ok": True}


@router.post("/{corpus_id}/upload")
async def upload(
    corpus_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    corpus = _own_corpus(db, user.id, corpus_id)
    name = file.filename or ""
    ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in _ALLOWED:
        raise HTTPException(
            status_code=400, detail="bad file type (use .txt/.md/.pdf/.docx)"
        )
    raw = await file.read()
    doc_id = ingest_file(db, corpus.id, name, raw, file.content_type or "")
    chunks = (
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).count()
    )
    return {"document_id": doc_id, "chunks": chunks}


@router.post("/{corpus_id}/analyse")
def analyse(
    corpus_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    corpus = _own_corpus(db, user.id, corpus_id)
    found = run_analysis(db, corpus.id)
    return {"contradictions_found": found}
