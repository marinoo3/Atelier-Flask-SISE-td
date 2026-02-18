from typing import Optional

from sqlalchemy import Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

# TODO: Import the Base object from the base module.


class Document:
    """
    SQLAlchemy model representing a scientific document record.

    This model stores references to scientific documents, medical guidelines,
    and research papers used for the RAG system.

    Attributes:
        id (int): Unique identifier for the document.
        title (str): Title of the document.
        binary (bytes): Binary content of the document (e.g., PDF data).
        category (Optional[str]): Optional category or type of the document.
        url (Optional[str]): Optional URL where the document can be accessed.
    """

    # TODO: Configurer le nom de la table

    # TODO: Finir de définir les colonnes de la table
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, unique=True
    )
