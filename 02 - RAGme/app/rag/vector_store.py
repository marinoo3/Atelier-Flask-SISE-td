"""
Vector Store Module.

This module provides CRUD operations for vector embeddings in ChromaDB,
handling documents and patient records for the RAG system.

Example:
    >>> from app.rag.vector_store import VectorStore, CollectionType
    >>> store = VectorStore(CollectionType.DOCUMENTS)
    >>> store.add("doc_001", "Medical content...", {"type": "protocol"})
    >>> results = store.search("diabetes treatment")
"""

from typing import List, Optional

from app.database import CollectionType, vector_db
from app.rag.vectorizer import Vectorizer
from app.schemas import Chunk


class VectorStore:
    """
    Vector store for ChromaDB operations.

    Provides methods for adding, searching, and deleting vector embeddings.
    Works with any collection type (documents, patients).

    Attributes:
        collection_type (CollectionType): The type of collection to use.
        vectorizer (Vectorizer): Service for generating embeddings.
        id_field (str): The metadata field name for item IDs.

    Example:
        >>> store = VectorStore(CollectionType.DOCUMENTS)
        >>> store.add("doc_001", "Medical content...", {"type": "protocol"})
        >>> results = store.search("diabetes treatment", n_results=5)
    """

    def __init__(
        self,
        collection_type: CollectionType,
        vectorizer: Optional[Vectorizer] = None,
        chroma_db=vector_db,
    ):
        """
        Initialize the VectorStore.

        Args:
            collection_type (CollectionType): The collection to use.
            vectorizer (Vectorizer, optional): Custom vectorizer instance.
            id_field (str): Metadata field name for item IDs. Defaults to "item_id".
        """
        self.collection_type = collection_type
        self.vectorizer = vectorizer or Vectorizer()
        self.chroma_db = chroma_db

    @property
    def collection(self):
        """Get the ChromaDB collection."""
        return self.chroma_db.get_collection(self.collection_type)

    def add(
        self,
        item_id: str,
        content: str,
        metadata: Optional[dict] = None,
        no_chunking: bool = False,
    ) -> int:
        """
        Add an item to the vector store.

        Chunks the content, generates embeddings, and stores them in ChromaDB.

        Args:
            item_id (str): Unique identifier for the item.
            content (str): The text content to embed.
            metadata (dict, optional): Additional metadata to store with each chunk.
            no_chunking (bool, optional): Whether to skip chunking and embed the entire content as one chunk. Defaults to False.
        Returns:
            int: Number of chunks added.

        Example:
            >>> n_chunks = store.add(
            ...     item_id="doc_001",
            ...     content="Long medical document...",
            ...     metadata={"type": "protocol"}
            ... )
        """
        # Chunk the content
        chunks = self.vectorizer.chunk_text(content) if not no_chunking else [content]
        if not chunks:
            return 0

        # Generate embeddings
        embeddings = self.vectorizer.generate_embeddings(chunks)

        # Prepare metadata for each chunk
        base_metadata = metadata or {}

        ids = []
        documents = []
        metadatas = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{item_id}_chunk_{i}"
            chunk_metadata = {
                **base_metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
            }

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(chunk_metadata)

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[dict] = None,
        embed: bool = False,
    ) -> List[Chunk]:
        """
        Search for similar items using semantic search.

        Args:
            query (str): The search query text.
            n_results (int): Maximum number of results. Defaults to 5.
            where (dict, optional): Metadata filter for the search.
            embed (bool, optional): Whether the query is already an embedding. Defaults to False.

        Returns:
            list[DocumentSchema]: List of DocumentSchema objects representing the search results.

        Example:
            >>> results = store.search("chest pain", n_results=3)
            >>> for doc in results:
            ...     print(doc.title, doc.content[:100])

        Example:
            >>> results = store.search("chest pain", n_results=3)
            >>> results = store.search("diabetes", where={"type": "protocol"})
        """
        query_embedding = query if embed else self.vectorizer.generate_embedding(query)

        search_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }

        if where:
            search_params["where"] = where

        results = self.collection.query(**search_params)

        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 - distance

                chunk = Chunk(
                    chroma_id=chunk_id,
                    content=results["documents"][0][i] if results["documents"] else "",
                    distance=distance,
                    score=similarity,
                    metadata=dict(
                        results["metadatas"][0][i] if results["metadatas"] else {},
                    ),
                )

                formatted_results.append(chunk)

        return formatted_results

    def delete(self, where: dict) -> bool:
        """
        Delete all chunks associated with an item.

        Args:
            where (dict): The where clause to filter chunks for deletion.


        Returns:
            bool: True if chunks were deleted, False if none found.
        """

        existing = self.collection.get(where=where)

        if not existing["ids"]:
            return False

        self.collection.delete(ids=existing["ids"])
        return True


document_store = VectorStore(CollectionType.DOCUMENTS)
