from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Settings(BaseSettings):
    database_url: str
    elasticsearch_url: str = "http://localhost:9200"

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_async_engine(
    settings.database_url,
    echo=True
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)