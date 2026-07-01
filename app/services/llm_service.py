import httpx
from app.core.config import settings
from typing import List, Dict

class LLMService:
    @staticmethod
    async def generate_response(prompt: str) -> str:
        """
        Sends a prompt to the local Ollama instance and returns the generated text.
        """
        url = f"{settings.ollama_base_url}/api/generate"
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            return str(data.get("response", ""))

    @staticmethod
    def build_prompt(query: str, context_chunks: List[str]) -> str:
        """
        Constructs a prompt with context.
        """
        context_str = "\n\n---\n\n".join(context_chunks)
        prompt = (
            "You are a helpful and accurate assistant. Use the following context to answer the user's question.\n"
            "If the context does not contain the answer, say \"I do not know based on the provided context.\"\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )
        return prompt
