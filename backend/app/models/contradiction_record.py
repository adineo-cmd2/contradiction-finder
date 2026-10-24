from sqlalchemy import String, Integer, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContradictionRecord(Base):
    __tablename__ = "contradiction_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    corpus_id: Mapped[int] = mapped_column(Integer, ForeignKey("corpora.id"), index=True)
    chunk_a_id: Mapped[int] = mapped_column(Integer, ForeignKey("document_chunks.id"), index=True)
    chunk_b_id: Mapped[int] = mapped_column(Integer, ForeignKey("document_chunks.id"), index=True)
    claim_a: Mapped[str] = mapped_column(Text)
    claim_b: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(50))
    explanation: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    same_doc: Mapped[bool] = mapped_column(Boolean, default=False)
