"""
Vectorizer Module.

This module provides text embedding generation and chunking functionality
using sentence-transformers models.
"""

import os
from typing import Optional, Sequence

from sentence_transformers import SentenceTransformer
from transformers.utils import logging as trf_logging
from huggingface_hub import logging as hub_logging

trf_logging.disable_progress_bar()
trf_logging.set_verbosity_error()
hub_logging.set_verbosity_error()



class Vectorizer:
    """
    Class for text embedding generation and chunking.

    This class handles loading the embedding model and provides methods
    for text chunking and embedding generation.

    Attributes:
        model_name (str): Name of the sentence-transformer model.
        chunk_size (int): Size of text chunks in characters.
        chunk_overlap (int): Overlap between consecutive chunks.
    """

    _model: Optional[SentenceTransformer] = None
    _current_model_name: Optional[str] = None

    def __init__(
        self,
        model_name: Optional[str] = None,
        chunk_size: int = 750,
        chunk_overlap: int = 50,
    ):
        """
        Initialize the Vectorizer.

        Args:
            model_name (str, optional): Sentence-transformer model name.
                Defaults to EMBEDDING_MODEL env var or "all-MiniLM-L6-v2".
            chunk_size (int): Number of characters per chunk. Defaults to 750.
            chunk_overlap (int): Overlap between chunks. Defaults to 50.
        """
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

        try:
            Vectorizer._model = SentenceTransformer(self.model_name, device="cpu")
        except Exception as e:
            print(f"Error loading embedding model '{self.model_name}': {e}")
            raise

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @property
    def model(self) -> SentenceTransformer:
        """
        Get or load the embedding model (lazy initialization, singleton).

        The model is shared across all Vectorizer instances to
        avoid loading it multiple times.

        Returns:
            SentenceTransformer: The loaded model instance.
        """
        if (
            Vectorizer._model is None
            or Vectorizer._current_model_name != self.model_name
        ):
            try:
                Vectorizer._model = SentenceTransformer(self.model_name, device="cpu")
            except Exception as e:
                print(f"Error loading embedding model '{self.model_name}': {e}")
                raise

            Vectorizer._current_model_name = self.model_name

        return Vectorizer._model

    def generate_embeddings(self, texts: list[str]) -> list[Sequence[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts (list[str]): List of text strings to embed.

        Returns:
            list[Sequence[float]]: List of embedding vectors.

        Example:
            >>> embeddings = service.generate_embeddings(["Hello", "World"])
            >>> len(embeddings)
            2
            >>> len(embeddings[0])  # Dimension of embedding
            384
        """
        if not texts:
            raise ValueError("Cannot generate embeddings for empty text list")

        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def generate_embedding(self, text: str) -> Sequence[float]:
        """
        Generate an embedding for a single text string.

        Args:
            text (str): Text string to embed.
        Returns:
            Sequence[float]: Embedding vector.
        """
        if not text:
            raise ValueError("Cannot generate embedding for empty string")

        return self.generate_embeddings([text])[0]

    def chunk_text(self, text: str) -> list[str]:
        """
        Chunk text into smaller pieces with overlapping segments to maintain context.

        Args:
            text (str): The text to chunk.

        Returns:
            list[str]: List of text chunks.
        """
        if not text:
            raise ValueError("Can't chunk empty string")

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)

            start += self.chunk_size - self.chunk_overlap

        return chunks
