from datetime import datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    rubrics: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False
    )

    created_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )