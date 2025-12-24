"""LLM provider abstraction for RAG."""

from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: list[str],
        system_prompt: str | None = None,
    ) -> str:
        """Generate a response given a prompt and context."""
        ...

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        context: list[str],
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response given a prompt and context."""
        ...


DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer the question.
If the context doesn't contain relevant information, say "I don't have enough information to answer that question."
Always cite the source when providing information."""


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        temperature: float = 0.7,
    ):
        from openai import AsyncOpenAI

        self.model = model
        self.temperature = temperature
        self.client = AsyncOpenAI(api_key=api_key)

    def _build_messages(
        self,
        prompt: str,
        context: list[str],
        system_prompt: str | None = None,
    ) -> list[dict]:
        sys_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        context_text = "\n\n---\n\n".join(context)

        return [
            {"role": "system", "content": sys_prompt},
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion: {prompt}",
            },
        ]

    async def generate(
        self,
        prompt: str,
        context: list[str],
        system_prompt: str | None = None,
    ) -> str:
        messages = self._build_messages(prompt, context, system_prompt)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content or ""

    async def stream(
        self,
        prompt: str,
        context: list[str],
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        messages = self._build_messages(prompt, context, system_prompt)
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(
        self,
        model: str = "llama3",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
    ):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature

    def _build_prompt(
        self,
        prompt: str,
        context: list[str],
        system_prompt: str | None = None,
    ) -> str:
        sys_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        context_text = "\n\n---\n\n".join(context)
        return f"""{sys_prompt}

Context:
{context_text}

Question: {prompt}

Answer:"""

    async def generate(
        self,
        prompt: str,
        context: list[str],
        system_prompt: str | None = None,
    ) -> str:
        import httpx

        full_prompt = self._build_prompt(prompt, context, system_prompt)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": self.temperature},
                },
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()["response"]

    async def stream(
        self,
        prompt: str,
        context: list[str],
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        import httpx

        full_prompt = self._build_prompt(prompt, context, system_prompt)
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": True,
                    "options": {"temperature": self.temperature},
                },
                timeout=120.0,
            ) as response:
                response.raise_for_status()
                import json

                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]


def get_llm_provider(
    provider: str = "openai",
    model: str | None = None,
    api_key: str | None = None,
) -> LLMProvider:
    """Get an LLM provider instance."""
    if provider == "openai":
        return OpenAIProvider(
            model=model or "gpt-4o-mini",
            api_key=api_key,
        )
    elif provider == "ollama":
        return OllamaProvider(
            model=model or "llama3",
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
