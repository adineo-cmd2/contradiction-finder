from datetime import datetime

from pydantic import BaseModel


class CorpusCreate(BaseModel):
    name: str


class CorpusOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
