# RAG System Enhancement Plan

Transform the current document processing API into a full-featured Retrieval-Augmented Generation (RAG) system.

## Current State

✅ Document ingestion (PDF, DOCX, PPTX, XLSX, HTML, images)  
✅ Multiple output formats (Markdown, Text, JSON)  
✅ Streaming support (SSE, per-page)  
✅ Bulk processing  
✅ Image extraction  
✅ Processing history with SQLite  
✅ React dashboard with Tailwind  

---

## Phase 1: Document Chunking & Storage

**Priority: High | Effort: M | Duration: 1-2 days**

### 1.1 Smart Chunking

- [ ] Implement Docling's hybrid chunking (semantic + token-based)
- [ ] Configurable chunk size and overlap
- [ ] Preserve document structure (headings, tables, lists)
- [ ] Maintain metadata per chunk (page, section, source)

### 1.2 Chunk Storage

- [ ] Extend database schema for chunks table
- [ ] Store chunk text, metadata, and parent document reference
- [ ] Add chunk retrieval endpoints

```python
# New model
class Chunk(Base):
    id: int
    document_id: int  # FK to Document
    content: str
    chunk_index: int
    page_number: int | None
    section_title: str | None
    token_count: int
    metadata: JSON
```

### 1.3 API Endpoints

- [ ] `POST /documents/process` → auto-chunk after processing
- [ ] `GET /documents/{id}/chunks` → list chunks
- [ ] `GET /chunks/{id}` → get single chunk

---

## Phase 2: Vector Embeddings

**Priority: High | Effort: M | Duration: 2-3 days**

### 2.1 Embedding Generation

- [ ] Integrate embedding models:
  - **Local**: `sentence-transformers/all-MiniLM-L6-v2` (fast, small)
  - **Local**: `BAAI/bge-small-en-v1.5` (better quality)
  - **API**: OpenAI `text-embedding-3-small`
- [ ] Async batch embedding generation
- [ ] Cache embeddings to avoid recomputation

### 2.2 Vector Database

- [ ] **Option A**: ChromaDB (simple, file-based, good for dev)
- [ ] **Option B**: Qdrant (production-ready, Docker)
- [ ] **Option C**: PostgreSQL + pgvector (if using Postgres)

```python
# Recommended: ChromaDB for simplicity
# core/vector_store.py
class VectorStore:
    async def add_chunks(chunks: list[Chunk], embeddings: list[list[float]])
    async def search(query: str, top_k: int = 5) -> list[ChunkResult]
    async def delete_document(document_id: int)
```

### 2.3 Embedding Pipeline

- [ ] Background job queue for embedding generation
- [ ] Progress tracking in database
- [ ] Retry logic for failed embeddings

---

## Phase 3: Semantic Search

**Priority: High | Effort: S | Duration: 1 day**

### 3.1 Search API

- [ ] `POST /search` → semantic search across all documents
- [ ] `POST /documents/{id}/search` → search within document
- [ ] Hybrid search (semantic + keyword BM25)
- [ ] Filters: date range, file type, tags

```python
# Request
{
    "query": "What are the key findings?",
    "top_k": 5,
    "filters": {
        "file_types": ["pdf"],
        "date_from": "2024-01-01"
    }
}

# Response
{
    "results": [
        {
            "chunk_id": 42,
            "document_id": 7,
            "filename": "report.pdf",
            "content": "The key findings indicate...",
            "score": 0.89,
            "page": 12
        }
    ]
}
```

### 3.2 Search UI

- [ ] Add search page to dashboard
- [ ] Display results with source highlighting
- [ ] Click to view full document context

---

## Phase 4: LLM Integration

**Priority: High | Effort: M | Duration: 2-3 days**

### 4.1 LLM Providers

- [ ] **Local**: Ollama (llama3, mistral, phi-3)
- [ ] **API**: OpenAI GPT-4o-mini / GPT-4o
- [ ] **API**: Anthropic Claude
- [ ] **API**: Google Gemini
- [ ] Provider abstraction layer for easy switching

```python
# core/llm.py
class LLMProvider(Protocol):
    async def generate(prompt: str, context: list[str]) -> str
    async def stream(prompt: str, context: list[str]) -> AsyncIterator[str]
```

### 4.2 RAG Pipeline

- [ ] Query → Embed → Search → Retrieve → Generate
- [ ] Configurable context window size
- [ ] Source citation in responses
- [ ] Streaming responses

```python
# services/rag_service.py
async def answer_question(
    query: str,
    document_ids: list[int] | None = None,
    top_k: int = 5,
    stream: bool = False
) -> RAGResponse
```

### 4.3 Prompt Engineering

- [ ] System prompts for different use cases
- [ ] Context formatting templates
- [ ] Few-shot examples for better quality

---

## Phase 5: Chat Interface

**Priority: Medium | Effort: M | Duration: 2-3 days**

### 5.1 Conversation Management

- [ ] Chat sessions with history
- [ ] Multi-turn conversations
- [ ] Context-aware follow-up questions

```python
# New models
class ChatSession(Base):
    id: int
    user_id: int | None
    document_ids: list[int]
    created_at: datetime

class ChatMessage(Base):
    id: int
    session_id: int
    role: str  # user, assistant, system
    content: str
    sources: JSON  # chunk references
    created_at: datetime
```

### 5.2 Chat API

- [ ] `POST /chat/sessions` → create session
- [ ] `POST /chat/sessions/{id}/messages` → send message
- [ ] `GET /chat/sessions/{id}/messages` → get history
- [ ] WebSocket support for real-time streaming

### 5.3 Chat UI

- [ ] Chat page in dashboard
- [ ] Message bubbles with markdown rendering
- [ ] Source citations with expandable context
- [ ] Document selector for scoped conversations

---

## Phase 6: Document Collections

**Priority: Medium | Effort: S | Duration: 1 day**

### 6.1 Collections/Folders

- [ ] Group documents into collections
- [ ] Search within collections
- [ ] Chat with specific collections

```python
class Collection(Base):
    id: int
    name: str
    description: str | None
    created_at: datetime

class CollectionDocument(Base):
    collection_id: int
    document_id: int
```

### 6.2 Tagging

- [ ] Add tags to documents
- [ ] Filter by tags in search
- [ ] Auto-tagging suggestions

---

## Phase 7: Multi-modal RAG

**Priority: Medium | Effort: L | Duration: 3-5 days**

### 7.1 Table Understanding

- [ ] Extract tables with structure
- [ ] Generate table summaries
- [ ] Query tables with natural language

### 7.2 Image Understanding

- [ ] Store extracted images with embeddings
- [ ] Image captioning with VLM
- [ ] Search images by description
- [ ] Include images in RAG context

### 7.3 Chart/Graph Analysis

- [ ] Extract charts from documents
- [ ] Generate chart descriptions
- [ ] Answer questions about visual data

---

## Phase 8: Authentication & Multi-tenancy

**Priority: Medium | Effort: M | Duration: 2-3 days**

### 8.1 User Authentication

- [ ] JWT-based authentication
- [ ] User registration/login
- [ ] Password reset flow
- [ ] OAuth (Google, GitHub) optional

### 8.2 Multi-tenancy

- [ ] User-scoped documents
- [ ] Shared collections (optional)
- [ ] Usage quotas and limits

### 8.3 API Keys

- [ ] Generate API keys for programmatic access
- [ ] Rate limiting per key
- [ ] Usage tracking

---

## Phase 9: Performance & Scale

**Priority: Low | Effort: L | Duration: 3-5 days**

### 9.1 Background Jobs

- [ ] Celery or ARQ for async tasks
- [ ] Job queue for embeddings, processing
- [ ] Progress tracking and notifications

### 9.2 Caching

- [ ] Redis for embedding cache
- [ ] Query result caching
- [ ] Session caching

### 9.3 Optimization

- [ ] Batch embedding generation
- [ ] Connection pooling
- [ ] Lazy loading for large documents

---

## Phase 10: Advanced Features

**Priority: Low | Effort: L | Duration: Ongoing**

### 10.1 Query Expansion

- [ ] HyDE (Hypothetical Document Embeddings)
- [ ] Multi-query retrieval
- [ ] Query rewriting with LLM

### 10.2 Re-ranking

- [ ] Cross-encoder re-ranking
- [ ] Cohere Rerank API integration
- [ ] Reciprocal Rank Fusion

### 10.3 Evaluation & Monitoring

- [ ] RAG evaluation metrics (Ragas)
- [ ] Answer quality scoring
- [ ] Retrieval precision/recall tracking

### 10.4 Integrations

- [ ] Slack bot
- [ ] API webhooks
- [ ] Export to Notion/Confluence

---

## Recommended Implementation Order

```
Week 1: Phase 1 (Chunking) + Phase 2 (Embeddings)
        └── Core RAG infrastructure

Week 2: Phase 3 (Search) + Phase 4 (LLM)
        └── Working Q&A system

Week 3: Phase 5 (Chat) + Phase 6 (Collections)
        └── User-friendly interface

Week 4+: Phases 7-10 (Advanced features)
        └── Polish and scale
```

---

## Tech Stack Recommendations

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| Vector DB | ChromaDB | Qdrant, pgvector |
| Embeddings | BGE-small-en | Cohere, Mistral AI, OpenAI |
| LLM (Local) | Ollama + Llama3 | vLLM, LM Studio |
| LLM (API) | OpenAI GPT-4o-mini | Claude 3 Haiku, Mistral AI |
| Job Queue | ARQ (async) | Celery |
| Cache | Redis | In-memory |
| Search | Hybrid (vector + BM25) | Vector only |

---

## Quick Start: Minimal RAG (Phase 1-4)

```bash
# Install dependencies
uv add chromadb sentence-transformers openai

# New files to create
core/embeddings.py      # Embedding generation
core/vector_store.py    # ChromaDB wrapper
services/rag_service.py # RAG pipeline
api/routes/search.py    # Search endpoints
api/routes/chat.py      # Chat endpoints
```

---

## Success Metrics

- [ ] Search latency < 500ms for 10k chunks
- [ ] Answer relevance score > 0.8 (Ragas)
- [ ] Embedding throughput > 100 chunks/sec
- [ ] Chat response time < 3s (streaming start)
- [ ] User satisfaction score > 4/5

---

## Notes

- Start simple with ChromaDB + sentence-transformers
- Add LLM integration early for quick wins
- Optimize chunking strategy based on document types
- Consider Docling's built-in chunking capabilities
- Monitor costs if using API-based embeddings/LLMs
