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

## Phase 1: Document Chunking & Storage ✅ COMPLETED

**Priority: High | Effort: M | Duration: 1-2 days**

### 1.1 Smart Chunking

- [x] Implement Docling's hybrid chunking (semantic + token-based)
- [x] Configurable chunk size and overlap
- [x] Preserve document structure (headings, tables, lists)
- [x] Maintain metadata per chunk (page, section, source)

### 1.2 Chunk Storage

- [x] Extend database schema for chunks table
- [x] Store chunk text, metadata, and parent document reference
- [x] Add chunk retrieval endpoints

**Implementation:** `services/chunking_service.py`, `core/models.py` (Chunk model)

### 1.3 API Endpoints

- [x] `POST /documents/ingest` → auto-chunk after processing
- [x] `GET /chunks/document/{id}` → list chunks
- [x] `GET /chunks/{id}` → get single chunk

**Implementation:** `api/routes/chunks.py`, `api/routes/documents.py`

---

## Phase 2: Vector Embeddings ✅ COMPLETED

**Priority: High | Effort: M | Duration: 2-3 days**

### 2.1 Embedding Generation

- [x] Integrate embedding models:
  - **Local**: `sentence-transformers/all-MiniLM-L6-v2` (fast, small)
  - **API**: OpenAI `text-embedding-3-small`
- [x] Async batch embedding generation
- [x] Cache embeddings to avoid recomputation

**Implementation:** `core/embeddings.py`

### 2.2 Vector Database

- [x] **SQLite + sqlite-vec** (chosen for simplicity)

**Implementation:** `core/vector_store.py`

### 2.3 Embedding Pipeline

- [x] Automatic embedding generation on ingest
- [x] Progress tracking in database (`has_embedding` field)

**Implementation:** `services/rag_service.py` (`process_and_embed_document`)

---

## Phase 3: Semantic Search ✅ COMPLETED

**Priority: High | Effort: S | Duration: 1 day**

### 3.1 Search API

- [x] `POST /search` → semantic search across all documents
- [x] Filters: document_ids, file_types

**Implementation:** `api/routes/search.py`

### 3.2 Search UI

- [ ] Add search page to dashboard
- [ ] Display results with source highlighting
- [ ] Click to view full document context

---

## Phase 4: LLM Integration ✅ COMPLETED

**Priority: High | Effort: M | Duration: 2-3 days**

### 4.1 LLM Providers

- [x] **Local**: Ollama (llama3, mistral, phi-3)
- [x] **API**: OpenAI GPT-4o-mini / GPT-4o
- [x] Provider abstraction layer for easy switching

**Implementation:** `core/llm.py`

### 4.2 RAG Pipeline

- [x] Query → Embed → Search → Retrieve → Generate
- [x] Configurable context window size
- [x] Source citation in responses
- [x] Streaming responses

**Implementation:** `services/rag_service.py`, `api/routes/search.py` (`POST /search/ask`)

### 4.3 Prompt Engineering

- [x] System prompts for RAG use case
- [x] Context formatting templates

---

## Phase 5: Chat Interface ✅ COMPLETED

**Priority: Medium | Effort: M | Duration: 2-3 days**

### 5.1 Conversation Management

- [x] Chat sessions with history
- [x] Multi-turn conversations
- [x] Context-aware follow-up questions

**Implementation:** `core/models.py` (ChatSession, ChatMessage)

### 5.2 Chat API

- [x] `POST /chat/sessions` → create session
- [x] `POST /chat/sessions/{id}/messages` → send message
- [x] `GET /chat/sessions/{id}` → get history
- [x] SSE streaming support for real-time responses

**Implementation:** `api/routes/chat.py`

### 5.3 Chat UI

- [ ] Chat page in dashboard
- [ ] Message bubbles with markdown rendering
- [ ] Source citations with expandable context
- [ ] Document selector for scoped conversations

---

## Phase 6: Document Collections ✅ COMPLETED

**Priority: Medium | Effort: S | Duration: 1 day**

### 6.1 Collections/Folders

- [x] Group documents into collections
- [x] Search within collections
- [x] Chat with specific collections

**Implementation:** `core/models.py` (Collection, CollectionDocument), `api/routes/collections.py`

### 6.2 Tagging

- [x] Add tags to documents
- [x] Filter by tags in search

**Implementation:** `core/models.py` (Tag, DocumentTag), `api/routes/tags.py`

---

## Phase 7: Multi-modal RAG ✅ COMPLETED

**Priority: Medium | Effort: L | Duration: 3-5 days**

### 7.1 Table Understanding

- [x] Extract tables with structure (Markdown, HTML, CSV)
- [x] Generate table summaries with LLM
- [x] Query tables with natural language

**Implementation:** `services/multimodal_service.py`, `api/routes/tables.py`

### 7.2 Image Understanding

- [x] Store extracted images with metadata
- [x] Image storage and retrieval endpoints

**Implementation:** `core/models.py` (ExtractedImage), `api/routes/extracted_images.py`

### 7.3 Chart/Graph Analysis

- [x] Extract charts/figures from documents
- [x] Store with page and caption info

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

## Implementation Progress

```
✅ Phase 1 (Chunking) - COMPLETED
✅ Phase 2 (Embeddings) - COMPLETED  
✅ Phase 3 (Search) - COMPLETED (API only, UI pending)
✅ Phase 4 (LLM) - COMPLETED
✅ Phase 5 (Chat) - COMPLETED (API only, UI pending)
✅ Phase 6 (Collections) - COMPLETED
✅ Phase 7 (Multi-modal) - COMPLETED
⬚ Phase 8 (Auth) - NOT STARTED
⬚ Phase 9 (Performance) - NOT STARTED
⬚ Phase 10 (Advanced) - NOT STARTED
```

---

## Files Created

| File | Description |
|------|-------------|
| `core/embeddings.py` | Sentence-transformers & OpenAI embeddings |
| `core/vector_store.py` | SQLite + sqlite-vec vector store |
| `core/llm.py` | OpenAI & Ollama LLM providers |
| `services/chunking_service.py` | Docling HybridChunker integration |
| `services/rag_service.py` | RAG pipeline (search, answer, embed) |
| `api/routes/search.py` | Search & RAG endpoints |
| `api/routes/chunks.py` | Chunk management endpoints |
| `api/routes/chat.py` | Chat session endpoints |
| `api/routes/collections.py` | Collection management endpoints |
| `api/routes/tags.py` | Tag management endpoints |
| `api/routes/tables.py` | Table extraction & querying |
| `api/routes/extracted_images.py` | Image extraction endpoints |
| `services/multimodal_service.py` | Multi-modal extraction service |

---

## API Endpoints Added

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/ingest` | Process, chunk & embed document |
| GET | `/chunks/{id}` | Get single chunk |
| GET | `/chunks/document/{id}` | Get all chunks for document |
| POST | `/search` | Semantic search |
| POST | `/search/ask` | RAG Q&A with LLM |
| POST | `/chat/sessions` | Create chat session |
| GET | `/chat/sessions` | List all sessions |
| GET | `/chat/sessions/{id}` | Get session with history |
| DELETE | `/chat/sessions/{id}` | Delete session |
| POST | `/chat/sessions/{id}/messages` | Send message (RAG) |
| POST | `/chat/sessions/{id}/messages/stream` | Stream message (SSE) |
| POST | `/collections` | Create collection |
| GET | `/collections` | List all collections |
| GET | `/collections/{id}` | Get collection details |
| DELETE | `/collections/{id}` | Delete collection |
| POST | `/collections/{id}/documents` | Add documents to collection |
| GET | `/collections/{id}/documents` | Get documents in collection |
| DELETE | `/collections/{id}/documents/{doc_id}` | Remove document from collection |
| POST | `/tags` | Create tag |
| GET | `/tags` | List all tags |
| DELETE | `/tags/{id}` | Delete tag |
| POST | `/tags/documents/{doc_id}` | Add tags to document |
| GET | `/tags/documents/{doc_id}` | Get document tags |
| DELETE | `/tags/documents/{doc_id}/{tag_id}` | Remove tag from document |
| GET | `/tables/document/{doc_id}` | Get document tables |
| GET | `/tables/{id}` | Get table details |
| GET | `/tables/{id}/html` | Get table as HTML |
| GET | `/tables/{id}/csv` | Get table as CSV |
| POST | `/tables/{id}/query` | Query table with natural language |
| POST | `/tables/{id}/summarize` | Generate table summary |
| GET | `/extracted-images/document/{doc_id}` | Get document images |
| GET | `/extracted-images/{id}` | Get image details |
| GET | `/extracted-images/{id}/file` | Get image file |

---

## Tech Stack (Current)

| Component | Implementation |
|-----------|---------------|
| Vector DB | SQLite + sqlite-vec |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM (Local) | Ollama |
| LLM (API) | OpenAI GPT-4o-mini |
| Database | SQLite + SQLAlchemy |
| API | FastAPI |

---

## Success Metrics

- [ ] Search latency < 500ms for 10k chunks
- [ ] Answer relevance score > 0.8 (Ragas)
- [ ] Embedding throughput > 100 chunks/sec
- [ ] Chat response time < 3s (streaming start)
- [ ] User satisfaction score > 4/5

---

## Notes

- Using Docling's built-in HybridChunker for semantic chunking
- Embeddings stored in sqlite-vec virtual table
- LLM API key passed via `X-OpenAI-API-Key` header
- Chat sessions support document scoping
