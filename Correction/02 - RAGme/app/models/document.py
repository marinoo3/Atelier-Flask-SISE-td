from typing import Optional

from sqlalchemy import Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Document(Base):
    """
    SQLAlchemy model representing a scientific document record.

    This model stores references to scientific documents, medical guidelines,
    and research papers used for the RAG system.

    Attributes:
        id (int): Primary key, auto-incremented unique identifier.
        title (str): Document title (max 500 characters). Required.
        content (str): Content of the document. Required.
        url (str): URL of the document. Required.
        category (str): Category of the document. Optional.
        created_at (datetime): Timestamp of record creation. Auto-generated.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, unique=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    # content as a pdf blop
    binary: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self):
        """Return a string representation of the Document instance."""
        return f"<Document(id={self.id}, title='{self.title[:50]}...')>"
