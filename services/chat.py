import json
from openai import AzureOpenAI
from ..repositories.chat import ChatRepository
from ..services.search import SearchService
from ..models.chat import ChatSession, ChatMessage
from ..models.article import Article
from ..schemas.chat import ChatMessageRead

class ChatService:
    def __init__(
        self,
        repo: ChatRepository,
        search_service: SearchService,
        azure_openai_key: str,
        azure_openai_endpoint: str,
        api_version: str = "2025-04-01-preview",
    ):
        self.repo = repo
        self.search_service = search_service
        self.client = AzureOpenAI(
            api_key=azure_openai_key,
            azure_endpoint=azure_openai_endpoint,
            api_version=api_version
        )
    
    def create_session(self, user_id: int, title: str | None = None) -> ChatSession:
        return self.repo.create_session(user_id, title)

    def get_session(self, session_id: int) -> ChatSession | None:
        return self.repo.get_session(session_id)
    
    def list_user_sessions(self, user_id: int) -> list[ChatSession]:
        return self.repo.list_user_sessions(user_id)
    
    def get_session_messages(self, session_id: int) -> list[ChatMessage]:
        return self.repo.get_session_messages(session_id)
    
    def send_message(self, session_id: int, user_message: str, model: str = "gpt-4o") -> tuple[ChatMessageRead, list[int]]:
        """
        Send a message and get AI response using RAG.
        Return: (assistant_message, source_article_ids)
        """
        # 1. Store user message
        self.repo.add_message(session_id, role="user", content=user_message)

        # 2. Search for relevant articles (RAG retrieval)
        search_results = self.search_service.search_articles(user_message, top_k=3)

        # 3. Build context from search results
        context = self._build_context(search_results)
        source_ids = [article.id for article, score in search_results]

        # 4. Get chat history for context
        messages = self.repo.get_session_messages(session_id)
        conversation_history = self._build_conversation_history(messages[-10:])  # Last 10 messages

        # 5. Create prompt with context
        system_prompt = """You are a helpful AI assistant for a knowledge base. Answer questions based
        on the provided context from the knowledge base articles. If the context doesn't contain relevant
        information, say so clearly. Always cite which articles you used to answer."""

        user_prompt = f"""Context from knowledge base: 
        {context} 

        User question: {user_message}"""

        # 6. Call Azure OpenAI chat completion
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        assistant_message = response.choices[0].message.content

        # 7. Store assistant message with sources
        message = self.repo.add_message(
            session_id,
            role="assistant",
            content=assistant_message,
            sources=json.dumps(source_ids)
        )

        # Convert to Pydantic model before returning
        return ChatMessageRead.model_validate(message), source_ids

    def _build_context(self, search_results: list[tuple[Article, float]]) -> str:
        """Build context string from search results."""
        context_parts = []
        for i, (article, score) in enumerate(search_results, 1):
            context_parts.append(f"Article {i} (ID: {article.id}, Title: {article.title}):\n{article.content}\n")
        return "\n".join(context_parts)
    
    def _build_conversation_history(self, messages: list[ChatMessage]) -> list[dict]:
        """Convert ChatMessage list to OpenAI message format."""
        return [{"role": msg.role, "content": msg.content} for msg in messages if msg.role in ["user", "assistant"]]
