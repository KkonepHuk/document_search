from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session

app = FastAPI(
    title="Document Search",
    version="1.0.0",
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