"""Embedding generation service."""

import asyncio
from typing import Protocol

from sentence_transformers import SentenceTransformer


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text."""
        ...

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        ...


class SentenceTransformerEmbeddings:
    """Local embeddings using sentence-transformers."""

    def __init__(self, model_id: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_id = model_id
        self._model: SentenceTransformer | None = None
        self._dimension: int | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_id)
        return self._model

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = self.model.get_sentence_embedding_dimension()
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    async def embed_async(self, texts: list[str]) -> list[list[float]]:
        """Async wrapper for embedding generation."""
        return await asyncio.to_thread(self.embed, texts)

    async def embed_query_async(self, text: str) -> list[float]:
        """Async wrapper for query embedding."""
        return await asyncio.to_thread(self.embed_query, text)


class OpenAIEmbeddings:
    """Embeddings using OpenAI API."""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
    ):
        from openai import OpenAI

        self.model = model
        self.client = OpenAI(api_key=api_key)
        self._dimension = 1536 if "small" in model else 3072

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text."""
        response = self.client.embeddings.create(input=[text], model=self.model)
        return response.data[0].embedding

    async def embed_async(self, texts: list[str]) -> list[list[float]]:
        """Async wrapper for embedding generation."""
        return await asyncio.to_thread(self.embed, texts)

    async def embed_query_async(self, text: str) -> list[float]:
        """Async wrapper for query embedding."""
        return await asyncio.to_thread(self.embed_query, text)


_default_embeddings: SentenceTransformerEmbeddings | None = None


def get_embeddings() -> SentenceTransformerEmbeddings:
    """Get the default embedding provider (singleton)."""
    global _default_embeddings
    if _default_embeddings is None:
        _default_embeddings = SentenceTransformerEmbeddings()
    return _default_embeddings
