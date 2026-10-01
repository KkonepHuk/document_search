from fastapi import Depends, FastAPI, HTTPException
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel, ConfigDict
from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_elasticsearch, get_session
from app.models import Document


class DocumentSearchRequest(BaseModel):
    query: str

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rubrics: list[str]
    text: str
    created_date: str


app = FastAPI(
    title="Document Search",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": result.scalar(),
    }

@app.post("/documents/search", response_model=list[DocumentOut])
async def search_documents(
    data: DocumentSearchRequest,
    session: AsyncSession = Depends(get_session),
    es: AsyncElasticsearch = Depends(get_elasticsearch),
):
    result = await es.search(
        index="documents",
        query={"match": {"text": data.query}},
        size=10000,
    )

    hits = result.get("hits", {}).get("hits", [])
    document_ids = [int(hit["_id"]) for hit in hits if "_id" in hit]

    if not document_ids:
        return []

    result = await session.execute(
        select(Document)
        .where(Document.id.in_(document_ids))
        .order_by(desc(Document.created_date))
        .limit(10000)
    )

    documents = result.scalars().all()

    return [
        DocumentOut(
            id=document.id,
            rubrics=document.rubrics,
            text=document.text,
            created_date=document.created_date.isoformat(),
        )
        for document in documents
    ]

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    session: AsyncSession = Depends(get_session),
    es: AsyncElasticsearch = Depends(get_elasticsearch),
):
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    await session.delete(document)
    await session.commit()

    await es.delete(
        index="documents",
        id=str(document_id),
        ignore=[404],
    )

    return {
        "message": "Document deleted",
        "id": document_id,
    }