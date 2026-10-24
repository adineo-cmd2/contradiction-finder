from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import contradictions, corpus, documents
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

import app.models.user  # noqa: F401 register tables
import app.models.corpus  # noqa: F401
import app.models.document  # noqa: F401
import app.models.document_chunk  # noqa: F401
import app.models.contradiction_record  # noqa: F401

Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(title="Contradiction Finder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:4323"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


app.include_router(corpus.router, prefix="/api/corpus", tags=["corpus"])
app.include_router(
    contradictions.router, prefix="/api/contradictions", tags=["contradictions"]
)
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
