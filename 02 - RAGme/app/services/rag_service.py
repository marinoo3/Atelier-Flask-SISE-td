from typing import Optional

from app.rag import VectorStore, document_store, llm_handler
from app.rag.llm import LLMHandler
from app.schemas import Context


class RagService:
    def __init__(
        self,
        vector_store: VectorStore = document_store,
        llm_handler: LLMHandler = llm_handler,
    ) -> None:
        self.vector_store = vector_store
        self.llm_handler = llm_handler

    def make_query(self, query: str, session_id: str) -> tuple[str, Optional[Context]]:
        """
        Process RAG, set conversation if provided and make a query to the LLM

        Args:
            query (str): User query
            session_id (str): UUID of the chat bot session

        Returns:
            str: LLM response
        """
        # Retrieve LLM session
        session = self.llm_handler.get_session(session_id)

        # Retrieve related document chunks (RAG)
        related_chunks = self.vector_store.search(query)

        # Build RAG prompt from chunks
        context = None
        if related_chunks:
            context = session.build_context(query, related_chunks)

        # Query LLM
        response = session.send_message(query, context=context)

        return str(response.content), context
