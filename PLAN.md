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

## Phase 8: Authentication & Multi-tenancy ✅ COMPLETED

**Priority: Medium | Effort: M | Duration: 2-3 days**

### 8.1 User Authentication

- [x] JWT-based authentication (access + refresh tokens)
- [x] User registration/login
- [x] Password hashing with bcrypt

**Implementation:** `core/auth.py`, `api/routes/auth.py`

### 8.2 Multi-tenancy

- [x] User model with admin flag
- [x] Optional auth (AUTH_ENABLED env var)

**Implementation:** `core/models.py` (User), `core/config.py`

### 8.3 API Keys

- [x] Generate API keys for programmatic access
- [x] API key authentication via X-API-Key header
- [x] Last used tracking

**Implementation:** `core/models.py` (APIKey), `core/auth.py`

---

## Phase 9: Performance & Scale ✅ COMPLETED

**Priority: Low | Effort: L | Duration: 3-5 days**

### 9.1 Background Jobs

- [x] ARQ for async tasks
- [x] Job queue for embeddings, table summaries
- [x] Batch document processing

**Implementation:** `core/jobs.py`

### 9.2 Caching

- [x] In-memory caching (TTL + LRU)
- [x] Embedding cache
- [x] Search result cache
- [x] LLM response cache

**Implementation:** `core/cache.py`

### 9.3 Optimization

- [x] Batch embedding generation
- [x] Cache stats and management endpoints

**Implementation:** `api/routes/admin.py`

---

## Phase 10: Advanced Features ✅ COMPLETED

**Priority: Low | Effort: L | Duration: Ongoing**

### 10.1 Query Expansion

- [x] HyDE (Hypothetical Document Embeddings)
- [x] Multi-query retrieval
- [x] Query rewriting with LLM

**Implementation:** `services/advanced_rag.py`

### 10.2 Re-ranking

- [x] Lexical re-ranking
- [x] Reciprocal Rank Fusion (RRF)

**Implementation:** `services/advanced_rag.py`

### 10.3 Advanced Search Endpoint

- [x] POST /search/advanced with method selection
- [x] Supports: hyde, multi_query, rerank

**Implementation:** `api/routes/search.py`

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
✅ Phase 8 (Auth) - COMPLETED
✅ Phase 9 (Performance) - COMPLETED
✅ Phase 10 (Advanced) - COMPLETED
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
| `core/auth.py` | JWT & API key authentication |
| `api/routes/auth.py` | Auth endpoints (register, login, tokens) |
| `core/cache.py` | In-memory caching (TTL + LRU) |
| `core/jobs.py` | ARQ background jobs |
| `api/routes/admin.py` | Cache management endpoints |
| `services/advanced_rag.py` | HyDE, multi-query, re-ranking |

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
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user |
| POST | `/auth/api-keys` | Create API key |
| GET | `/auth/api-keys` | List API keys |
| DELETE | `/auth/api-keys/{id}` | Delete API key |
| GET | `/admin/cache/stats` | Get cache statistics |
| POST | `/admin/cache/clear` | Clear all caches |
| GET | `/admin/health/detailed` | Detailed health info |
| POST | `/search/advanced` | Advanced search (HyDE, multi-query, rerank) |

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
