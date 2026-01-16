# Sentinel Knowledge - Architectural Flow

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                            │
│                    Streamlit Dashboard (Port 8501)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │   Query      │  │    Gap       │          │
│  │   Overview   │  │  Interface   │  │  Analysis    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                  │
└─────────┼─────────────────┼──────────────────┼─────────────────┘
          │                 │                  │
          │  HTTP/REST API  │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER                                  │
│              FastAPI Backend (Port 8000)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Endpoints                         │  │
│  │  • POST /query          - Query with gap detection       │  │
│  │  • GET  /gaps           - List all gaps                  │  │
│  │  • GET  /gaps/stats     - Gap statistics                 │  │
│  │  • POST /ingest         - Ingest documents               │  │
│  │  • POST /ingest/confluence - Ingest Confluence pages     │  │
│  │  • POST /analyze/confluence/all - Bulk gap analysis      │  │
│  │  • GET  /suggested-questions - Generate questions         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────┬───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     RAG      │  │    Gap       │  │  Question    │         │
│  │   Service    │  │  Detector   │  │  Generator   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                 │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐         │
│  │  Embedding   │  │  Cross-Doc   │  │  Confluence  │         │
│  │   Service    │  │  Analyzer    │  │  Ingestion   │         │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘         │
│         │                                     │                 │
└─────────┼─────────────────────────────────────┼─────────────────┘
          │                                     │
          ▼                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   ChromaDB   │  │  gaps.json   │  │  Documents/  │         │
│  │  (Vector DB) │  │  (Gap Store) │  │  Confluence  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Data Flow

### 1. Document Ingestion Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT INGESTION                        │
└─────────────────────────────────────────────────────────────┘

Local Documents                    Confluence Pages
     │                                    │
     ▼                                    ▼
┌─────────────┐                  ┌──────────────────┐
│  Ingestion  │                  │  Confluence      │
│  Service    │                  │  Ingestion      │
└──────┬──────┘                  └────────┬─────────┘
       │                                  │
       │  Parse & Chunk                   │  Fetch via API
       │  (PDF/DOCX/TXT)                 │  (HTML → Text)
       │                                  │
       ▼                                  ▼
┌──────────────────────────────────────────────────┐
│          Embedding Service                        │
│  • Convert text chunks → embeddings              │
│  • Generate vector representations                │
│  • Store metadata (title, source, chunk_index)   │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │    ChromaDB     │
         │  (Vector Store) │
         │  • Embeddings   │
         │  • Documents    │
         │  • Metadata     │
         └─────────────────┘
```

### 2. Query Processing Flow (RAG Pipeline)

```
┌─────────────────────────────────────────────────────────────┐
│                    QUERY PROCESSING                          │
└─────────────────────────────────────────────────────────────┘

User Question
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: RETRIEVE (RAGService.retrieve)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Convert question → embedding vector               │  │
│  │  2. Search ChromaDB for similar document chunks       │  │
│  │  3. Get top N results (default: 10)                  │  │
│  │  4. Calculate similarity scores (cosine distance)     │  │
│  │  5. Return: documents, scores, metadata               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: GENERATE (RAGService.generate_answer)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Build context from retrieved documents           │  │
│  │  2. Create prompt:                                    │  │
│  │     - System: "Answer based on context..."           │  │
│  │     - Context: [Document 1], [Document 2], ...      │  │
│  │     - Question: User's question                      │  │
│  │  3. Send to LLM (Ollama/OpenAI)                      │  │
│  │  4. Generate answer                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: GAP DETECTION (GapDetectorService.detect_gap)     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Analyze query results for gaps:                     │  │
│  │  • Missing Knowledge: No documents found             │  │
│  │  • Incomplete Knowledge: Uncertainty phrases         │  │
│  │  • Consistency Gap: Conflicting info                │  │
│  │  • Fragmented Knowledge: Info spread across docs     │  │
│  │  • Discoverability Gap: Hard to find                 │  │
│  │  → Save to gaps.json if gap detected                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
                    Return Response
                    • Answer
                    • Sources
                    • Confidence Score
                    • Gap Info (if detected)
```

### 3. Gap Analysis Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    GAP ANALYSIS                             │
└─────────────────────────────────────────────────────────────┘

Two Analysis Methods:

┌──────────────────────────────────┐  ┌──────────────────────────┐
│  Method 1: Real-time Detection   │  │  Method 2: Bulk Analysis  │
│  (During Queries)                │  │  (Cross-Document)        │
└──────────────────────────────────┘  └──────────────────────────┘
         │                                      │
         │  Each query triggers                 │  Analyze all docs
         │  gap detection                       │  for inconsistencies
         │                                      │
         ▼                                      ▼
┌──────────────────────────────────┐  ┌──────────────────────────┐
│  GapDetectorService              │  │  CrossDocumentAnalyzer   │
│  • Check similarity scores       │  │  • Extract entities      │
│  • Check answer quality          │  │  • Compare documents     │
│  • Check query history           │  │  • Find inconsistencies  │
│  • Detect 5 gap types            │  │  • Detect missing info  │
└──────────────┬───────────────────┘  └──────────┬───────────────┘
               │                                  │
               └──────────────┬───────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   gaps.json     │
                    │  (Persistent)   │
                    │  • Gap details  │
                    │  • Occurrences   │
                    │  • Severity     │
                    │  • Sources      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Gap Analysis   │
                    │    Dashboard    │
                    │  • Table view   │
                    │  • Filters     │
                    │  • Charts      │
                    │  • Export CSV  │
                    └─────────────────┘
```

---

## 🧩 Component Details

### Service Layer Components

#### 1. **EmbeddingService**
- **Purpose**: Vector embeddings and ChromaDB management
- **Responsibilities**:
  - Convert text → embeddings (OpenAI/Ollama)
  - Store/retrieve from ChromaDB
  - Search similar documents
  - Manage document metadata
- **Storage**: `chroma_db/` directory

#### 2. **RAGService**
- **Purpose**: RAG pipeline (Retrieve + Generate)
- **Dependencies**: EmbeddingService
- **Responsibilities**:
  - Retrieve relevant documents
  - Generate answers using LLM
  - Calculate confidence scores
- **LLM Options**: Ollama (local) or OpenAI (cloud)

#### 3. **GapDetectorService**
- **Purpose**: Automatic gap detection
- **Storage**: `data/gaps.json`
- **Detection Rules**:
  1. **Missing Knowledge**: No documents found
  2. **Incomplete Knowledge**: Uncertainty phrases, missing info
  3. **Consistency Gap**: Conflicting information
  4. **Fragmented Knowledge**: Info spread across docs
  5. **Discoverability Gap**: Hard to find knowledge
- **Tracks**: Occurrence count, severity, source documents

#### 4. **QuestionGeneratorService**
- **Purpose**: Generate suggested questions
- **Dependencies**: EmbeddingService
- **Process**:
  - Sample documents from knowledge base
  - Extract topics and content
  - Generate questions via LLM
  - Return 3-4 suggested questions

#### 5. **ConfluenceIngestionService**
- **Purpose**: Ingest Confluence documentation
- **Process**:
  - Connect to Confluence API
  - Fetch pages from spaces
  - Convert HTML → text
  - Chunk and prepare for embedding

#### 6. **CrossDocumentAnalyzer**
- **Purpose**: Bulk gap analysis across all documents
- **Process**:
  - Extract entities, schemas, tables from each doc
  - Compare documents for inconsistencies
  - Find missing definitions
  - Detect cross-document gaps

---

## 🔌 API Endpoints

### Query Endpoints
- `POST /query` - Query knowledge base with gap detection
- `GET /suggested-questions` - Get dynamically generated questions

### Gap Endpoints
- `GET /gaps` - List all detected gaps (with filters)
- `GET /gaps/stats` - Get gap statistics
- `DELETE /gaps/{gap_id}` - Delete a specific gap

### Ingestion Endpoints
- `POST /ingest` - Ingest local documents
- `POST /ingest/file` - Ingest single uploaded file
- `POST /ingest/confluence` - Ingest Confluence pages
- `POST /ingest/confluence/page/{page_id}` - Ingest single page

### Analysis Endpoints
- `POST /analyze/confluence/all` - Bulk gap analysis of all Confluence data

### Confluence Endpoints
- `GET /confluence/spaces` - List all spaces
- `GET /confluence/spaces/{space_key}/pages` - List pages in space
- `GET /confluence/pages/{page_id}` - Get specific page content

---

## 💾 Data Storage

### 1. ChromaDB (Vector Database)
- **Location**: `chroma_db/`
- **Stores**:
  - Document embeddings (vectors)
  - Text chunks
  - Metadata (title, source, page_id, etc.)
- **Purpose**: Fast similarity search

### 2. gaps.json
- **Location**: `data/gaps.json`
- **Stores**:
  - All detected gaps
  - Query history
  - Gap details (type, severity, occurrences, sources)
- **Format**: JSON

### 3. Documents Directory
- **Location**: `data/documents/`
- **Stores**: Original uploaded documents (PDF, DOCX, TXT)

---

## 🔄 Request-Response Flow Examples

### Example 1: User Query

```
1. User enters question in Query Interface
   ↓
2. Frontend → POST /query
   {
     "question": "What are the key fields in monolith_orders?",
     "user_id": "user123"
   }
   ↓
3. Backend processes:
   a. RAGService.query()
      - Retrieve: Search ChromaDB
      - Generate: LLM creates answer
   b. GapDetectorService.detect_gap()
      - Analyze results
      - Detect gap if found
   ↓
4. Response:
   {
     "answer": "The key fields are...",
     "sources": ["DBT Design Document"],
     "confidence_score": 0.85,
     "is_gap": true,
     "gap_reason": "incomplete_knowledge"
   }
   ↓
5. Frontend displays answer + gap indicator
```

### Example 2: Bulk Gap Analysis

```
1. User clicks "Analyze All Confluence Data"
   ↓
2. Frontend → POST /analyze/confluence/all
   ↓
3. Backend processes:
   a. Fetch fresh data from Confluence
   b. Ingest into ChromaDB
   c. CrossDocumentAnalyzer:
      - Extract entities from all docs
      - Compare for inconsistencies
      - Find missing information
   d. Save gaps to gaps.json
   ↓
4. Response:
   {
     "total_confluence_pages": 7,
     "gaps_detected": 12,
     "message": "Analysis complete"
   }
   ↓
5. Frontend refreshes Gap Analysis table
```

---

## 🎯 Key Design Patterns

### 1. **Service-Oriented Architecture**
- Each service has a single responsibility
- Services are loosely coupled
- Easy to test and maintain

### 2. **Lazy Initialization**
- Services initialize only when needed
- Handles missing API keys gracefully
- Optional services (Confluence) don't break app

### 3. **Shared State**
- Single `GapDetectorService` instance
- Shared `gaps.json` storage
- Real-time updates across UI

### 4. **RAG Pattern**
- Retrieve: Vector similarity search
- Augment: Add context to prompt
- Generate: LLM creates answer

### 5. **Gap Detection Strategy**
- Multiple detection rules
- Severity classification
- Occurrence tracking

---

## 🔐 Configuration

### Environment Variables (.env)
```
# LLM Provider (ollama or openai)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=gemma3:latest

# OpenAI (alternative)
OPENAI_API_KEY=sk-...
OPENAI_LLM_MODEL=gpt-3.5-turbo

# Embedding Storage (memory or chromadb)
EMBEDDING_STORAGE=chromadb

# Confluence (optional)
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-token
```

---

## 📊 Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Vector DB**: ChromaDB
- **LLM**: Ollama (local) or OpenAI (cloud)
- **Embeddings**: OpenAI `text-embedding-ada-002` or Ollama `nomic-embed-text`

### Frontend
- **Framework**: Streamlit
- **Visualization**: Plotly
- **Styling**: Custom CSS (light/dark themes)

### Data Storage
- **Vector DB**: ChromaDB (persistent)
- **Gap Storage**: JSON file (`gaps.json`)
- **Documents**: File system (`data/documents/`)

---

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Browser                         │
│  • Dashboard (Streamlit) - Port 8501                    │
└────────────────────┬──────────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend Server                      │
│  • API Endpoints - Port 8000                            │
│  • CORS enabled for frontend                            │
└────────────────────┬──────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────┐        ┌──────────────┐
│   ChromaDB   │        │  Ollama/     │
│  (Local)     │        │  OpenAI API  │
└──────────────┘        └──────────────┘
```

---

## 🔍 Key Flows Summary

1. **Ingestion**: Documents → Chunks → Embeddings → ChromaDB
2. **Query**: Question → Embedding → Search → Retrieve → Generate → Detect Gap
3. **Analysis**: All Docs → Extract Entities → Compare → Find Gaps → Store
4. **Display**: Gaps → Filter → Visualize → Export

---

This architecture provides:
- ✅ Scalable service-oriented design
- ✅ Real-time gap detection
- ✅ Multiple data sources (local files + Confluence)
- ✅ Flexible LLM backend (local or cloud)
- ✅ Persistent storage for gaps and vectors
- ✅ Interactive dashboard for analysis
