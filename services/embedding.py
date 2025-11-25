from openai import AzureOpenAI
import json

class EmbeddingService:
    def __init__(self, api_key: str, azure_endpoint: str, api_version: str = "2025-04-01-preview"):
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version
        )
    
    def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> list[float]:
        """Generate embedding for give text."""
        response = self.client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    
    def embedding_to_json(self, embedding: list[float]) -> str:
        """Convert embedding list to JSON string for storage."""
        return json.dumps(embedding)

    def json_to_embedding(self, json_str: str) -> list[float]:
        """Convert JSON string back to embedding list."""
        return json.loads(json_str)