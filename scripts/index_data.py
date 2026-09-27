import asyncio

from elasticsearch import AsyncElasticsearch
from sqlalchemy import select

from app.database import async_session, settings
from app.models import Document


async def index_data():
    es = AsyncElasticsearch(settings.elasticsearch_url)

    try:
        async with async_session() as session:
            result = await session.execute(
                select(Document)
            )

            documents = result.scalars().all()

            for document in documents:
                await es.index(
                    index="documents",
                    id=str(document.id),
                    document={
                        "id": document.id,
                        "text": document.text,
                    },
                )

            print(f"Indexed {len(documents)} documents")

    finally:
        await es.close()


if __name__ == "__main__":
    asyncio.run(index_data())