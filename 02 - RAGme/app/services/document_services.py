"""
Document Service Module.

This module provides database query operations for Document records.

Example:
    >>> from app.services import DocumentService
    >>> service = DocumentService()
    >>> documents = service.get_all()
"""

from pathlib import Path
from typing import List, Optional

from sqlalchemy.exc import IntegrityError

from app.database import Database, db
from app.models import Document
from app.parser import PDFHandler
from app.rag.vector_store import document_store
from app.schemas import DocumentSchema


class DocumentService:
    """
    Service class for Document database operations.

    Provides CRUD operations and common queries for Document records.

    Example:
        >>> service = DocumentService()
        >>> all_docs = service.get_all()
        >>> doc = service.get_by_id(1)
    """

    def __init__(
        self, db_manager: Database = db, pdf_handler: PDFHandler = PDFHandler()
    ):
        """
        Initialize the DocumentService.

        Args:
            db_session: Database session/connection. Defaults to app's db.
            pdf_handler: PDF handler instance. Defaults to a new PDFHandler.
        """
        self.db_manager = db_manager
        self.pdf_handler = pdf_handler

    ################################################################
    # READ METHODS
    ################################################################

    def get_all(self) -> list[DocumentSchema]:
        """
        Retrieve all documents from the database.

        Returns:
            list[DocumentSchema]: List of all Document records.

        Example:
            >>> documents = service.get_all()
            >>> for doc in documents:
            ...     print(doc.titre)
        """

        results = list()

        with self.db_manager.session() as session:
            documents = session.query(Document).all()

            for document in documents:
                results.append(DocumentSchema.model_validate(document))

        return results

    def get_by_id(self, document_id: int) -> DocumentSchema:
        """
        Retrieve a document by ID.

        Args:
            document_id (int): The document's unique identifier.

        Returns:
            DocumentSchema: The Document if found, None otherwise.

        Example:
            >>> doc = service.get_by_id(1)
            >>> if doc:
            ...     print(doc.titre)
        """
        with self.db_manager.session() as session:
            document = session.query(Document).filter_by(id=document_id).first()

            document_schema = (
                DocumentSchema.model_validate(document) if document else None
            )

            if not document_schema:
                raise ValueError(f"Document with id={document_id} not found.")

            return document_schema

    ################################################################
    # CREATE METHODS
    ################################################################
    def create(
        self,
        title: str,
        binary: bytes,
        category: Optional[str] = None,
        url: Optional[str] = None,
    ) -> DocumentSchema:
        """
        Create a new document record.

        Args:
            title (str): The document title
            binary (bytes): The pdf blop
            text_content (Optional[str]): The extracted text content of the pdf, used for the vector store
            category (Optional[str]): The document category
            url (str): The source URL of the document

        Returns:
            DocumentSchema: The newly created Document record
        """
        with self.db_manager.session() as session:
            document = Document(title=title, binary=binary, category=category, url=url)

            session.add(document)
            session.commit()
            session.flush()

            document_schema = DocumentSchema.model_validate(document)

            # Parse the pdf blob to add and chunk for the vector store if no text_content is provided
            text_content = self.pdf_handler.read_pdf_from_bytes(document_schema.binary)

            # add to vector store
            document_store.add(
                item_id=document_schema.chroma_id,
                content=text_content,
                metadata=document_schema.chroma_metadata,
            )

            return document_schema

    def create_from_pdf_folder(self, folder_path: Path) -> List[DocumentSchema]:
        """Function to create new documents from all pdfs in a folder.

        Args:
            folder_path (str): The path of the folder containing the pdf files.

        Raises:
            FileNotFoundError: If the folder does not exist.
            ValueError: If the folder is empty or if no valid pdf files are found.

        Returns:
            list[DocumentSchema]: The list of newly created Document records.
        """
        base_path = Path(folder_path)

        # queue to explore subdirectories using bread firsth search
        path_queue = [base_path]

        documents = []

        while path_queue:
            # pop the first directory
            current_path = path_queue.pop(0)

            # iteration on all the files in the current path
            for path in current_path.iterdir():
                # if a subdirectory is found append the subdirectory to the queue
                if path.is_dir():
                    path_queue.append(path)

                # if a file and a pdf: create a document
                elif path.is_file() and path.suffix.lower() == ".pdf":
                    with open(path, "rb") as f:
                        # get the title as a file name
                        title = path.stem

                        # get the binary
                        binary = f.read()

                        if title and binary:
                            # get the subfoldername as the category
                            category = (
                                path.parent.name if path.parent != base_path else None
                            )

                            try:
                                document = self.create(
                                    title=title,
                                    binary=binary,
                                    category=category,
                                    url="",
                                )
                                documents.append(document)
                            except IntegrityError:
                                continue

        if not documents:
            raise ValueError("No valid PDF files found in the folder.")

        return documents

    ################################################################
    # UPDATE METHODS
    ################################################################

    def update_document(
        self,
        document_id: int,
        title: str,
        binary: bytes,
        category: Optional[str],
        url: str,
    ) -> DocumentSchema:
        """Update an existing document with new information.

        Args:
            document_id (int): The unique identifier of the document to update.
            title (str): The new title for the document.
            binary (bytes): The new binary content for the document.
            category (Optional[str]): The new category for the document.
            url (str): The new URL for the document.

        Returns:
            DocumentSchema: The updated Document record.
        """

        # get the text content from the new binary
        text_content = self.pdf_handler.read_pdf_from_bytes(binary)

        with self.db_manager.session() as session:
            document = session.query(Document).filter_by(id=document_id).first()
            if not document:
                raise ValueError(f"Document with id={document_id} not found.")

            document.title = title
            document.binary = binary
            document.category = category
            document.url = url
            session.commit()
            session.flush()

            document_schema = DocumentSchema.model_validate(document)

            # update in chroma_db
            document_store.add(
                item_id=document_schema.chroma_id,
                content=text_content,
                metadata=document_schema.chroma_metadata,
            )

            return document_schema

    ################################################################
    # DELETE METHODS
    ################################################################
    def delete(self, document_id: int) -> bool:
        """
        Delete a document by ID.

        Args:
            document_id (int): The document's unique identifier.

        Returns:
            bool: True if deleted, False if document not found.

        Example:
            >>> deleted = service.delete(1)
        """
        with self.db_manager.session() as session:
            document = session.query(Document).filter_by(id=document_id).first()
            if document:
                session.delete(document)
                session.commit()

                # delete from chroma_db
                document_store.delete(where={"document_id": document.id})
                return True
            return False
