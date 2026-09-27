import ast
import asyncio
import csv
import os
from datetime import datetime
from sqlalchemy import func, select
from app.database import async_session
from app.models import Document


CSV_PATH = os.getenv("CSV_PATH", "data/posts.csv")


async def import_data():
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).select_from(Document)
        )

        count = result.scalar_one()

        if count > 0:
            print(f"Database already contains {count} documents, skipping import")
            return

        with open(CSV_PATH, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            documents = []

            for row in reader:
                document = Document(
                    text=row["text"],
                    rubrics=ast.literal_eval(row["rubrics"]),
                    created_date=datetime.fromisoformat(row["created_date"]),
                )

                documents.append(document)

            session.add_all(documents)
            await session.commit()

            print(f"Imported {len(documents)} documents")


if __name__ == "__main__":
    asyncio.run(import_data())