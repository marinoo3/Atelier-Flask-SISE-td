import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import Messages, SystemMessage, UserMessage, AssistantMessage

from app.parser import MdParser
from app.schemas import Chunk, Context

load_dotenv()


class LLMSession:
    """
    Session handler for Mistral LLM interactions.

    Manages model selection, prompt templates and conversation history.
    """

    id: str
    name: str
    model_name: str
    temperature = 0.5
    max_tokens = 5000
    messages: list[Messages] = []

    system_prompt = """
    Tu es un expert en statistique et en science des données.
    Tu reçois du contexte qui peut t'être utile pour répondre aux questions de l'utilisateur.
    """

    def __init__(self, name: str, model: str = "mistral-small-latest"):
        """
        Initialize the LLM handler.

        Args:
            model: Mistral model name. Default to 'mistral-small-latest'
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self._api_key = os.getenv("MISTRAL_API_KEY")

        if not self._api_key:
            raise Exception("MISTRAL_API_KEY not found in environment variables")

        self._client = None
        self.model_name = model
        self.__init_messages()

    @property
    def client(self):
        """Lazy initialization of Mistral client."""
        if self._client is None:
            self._client = Mistral(api_key=self._api_key)

        return self._client

    def __init_messages(self) -> None:
        """
        Create (or erase) the list of message with the initial system prompt
        """
        self.messages = [SystemMessage(content=self.system_prompt)]

    def __convert_message(self, message: Messages) -> Messages:
        """
        Convert the content of a mistral message to HTML

        Returns:
            Messages: Converted model
        """
        return message.model_copy(
            update={
                "content": MdParser.to_html(str(message.content))
            }
        )

    def build_context(self, query: str, chunks: list[Chunk]) -> Context:
        """
        Create a RAG context / prompt from a list of chunk.

        Args:
            chunks (list[Chunk]): The chunks to build a context from
            query (str): User message query

        Returns:
            Context: Context object
        """
        context = Context(query=query, chunks=chunks)

        return context

    def send_message(self, message: str, context: Optional[Context] = None) -> Messages:
        """
        Generate a response in a conversation context with history.

        Args:
            message (str): The user message.
            history (list[Message], optional): List of previous messages [{"role": "user"|"assistant", "content": "..."}].
            context (str, optional): Optional RAG context prompt.

        Returns:
            LLMResponse with content and usage stats
        """
        # Add RAG context if provided
        if context:
            self.messages.append(SystemMessage(content=context.context))

        # Add new user message
        self.messages.append(UserMessage(content=message))

        response = self.client.chat.complete(
            model=self.model_name,
            messages=self.messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        if not response.choices:
            raise ValueError("Invalid response from Mistral API")

        # Add LLM response to conversation
        self.messages.append(response.choices[0].message)

        return self.__convert_message(response.choices[0].message) 
    
    def get_messages(self) -> list[Messages]:
        """
        Retrieve the list of user and assistant messages.
        Convert content to HTML format.

        Returns:
            list[Messages]: Session messages
        """
        return [
            self.__convert_message(message) 
            for message in self.messages 
            if message.role in ["user", "assistant"]
        ]


class LLMHandler:
    """
    Manage LLMHandler sessions
    """

    sessions: dict[str, LLMSession] = {}

    def get_session(self, id: str) -> LLMSession:
        """
        Retrieve a LLMSession from its uuid

        Args:
            id (int): Session uuid
        """
        session = self.sessions.get(id)
        if not session:
            raise IndexError(f"No session found with uuid {id}")

        return session
    
    def get_all_sessions(self) -> list[LLMSession]:
        """
        Get the list of all LLMSessions

        Returns:
            list[LLMSession]: All LLMSessions
        """
        return list(self.sessions.values())

    def create_session(self, name: str) -> LLMSession:
        """
        Create and store a LLMSession

        Returns:
            LLMHandler: The LLMSession instance
        """
        session = LLMSession(name)
        self.sessions[session.id] = session
        return session

    def delete_session(self, id: str) -> None:
        """
        Delete a LLMSession instance

        Args:
            id (int): Session uuid
        """
        session = self.get_session(id)
        self.sessions.pop(session.id)


llm_handler = LLMHandler()


# Fake sessions
llm_handler.create_session('test session')
hello_session = llm_handler.create_session('hello')
hello_session.messages.append(UserMessage(content="Hello there"))
hello_session.messages.append(AssistantMessage(content="Hi, how can I help you"))