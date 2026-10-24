from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.contradiction_record import ContradictionRecord
from app.models.corpus import Corpus
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User


def test_user_corpus_docs_chunks_contradiction_link():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    u = User(email="contra@example.com", password_hash=hash_password("secret123"))
    db.add(u)
    db.commit()
    db.refresh(u)

    corpus = Corpus(user_id=u.id, name="Climate papers")
    db.add(corpus)
    db.commit()
    db.refresh(corpus)
    assert corpus.user_id == u.id

    doc_a = Document(corpus_id=corpus.id, filename="paper_a.txt")
    doc_b = Document(corpus_id=corpus.id, filename="paper_b.txt")
    db.add_all([doc_a, doc_b])
    db.commit()
    db.refresh(doc_a)
    db.refresh(doc_b)
    assert doc_a.corpus_id == corpus.id
    assert doc_b.corpus_id == corpus.id

    chunk_a = DocumentChunk(
        document_id=doc_a.id,
        idx=0,
        text="Global temperatures are rising rapidly.",
        embedding=[0.1, 0.2],
        section="intro",
    )
    chunk_b = DocumentChunk(
        document_id=doc_b.id,
        idx=0,
        text="Global temperatures are not rising at all.",
        embedding=[0.1, 0.3],
        section="intro",
    )
    db.add_all([chunk_a, chunk_b])
    db.commit()
    db.refresh(chunk_a)
    db.refresh(chunk_b)
    assert chunk_a.document_id == doc_a.id
    assert chunk_b.document_id == doc_b.id

    record = ContradictionRecord(
        corpus_id=corpus.id,
        chunk_a_id=chunk_a.id,
        chunk_b_id=chunk_b.id,
        claim_a="Global temperatures are rising rapidly.",
        claim_b="Global temperatures are not rising at all.",
        severity="factual",
        explanation="Direct polarity flip on temperature trend.",
        confidence=0.75,
        same_doc=False,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    assert record.corpus_id == corpus.id
    assert record.chunk_a_id == chunk_a.id
    assert record.chunk_b_id == chunk_b.id
    assert record.same_doc is False

    db.close()
