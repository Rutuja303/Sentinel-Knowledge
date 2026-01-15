# Sentinel Knowledge - Project Architecture & Flow

## 🤖 AI Models Used

### Primary Configuration (Default - Free & Local)
- **LLM Provider**: Ollama (Free, runs locally)
- **LLM Model**: `llama3.1:8b` (8 billion parameter model)
- **Embedding Model**: `nomic-embed-text` (Text embedding model)

### Alternative Configuration (Paid - Cloud)
- **LLM Provider**: OpenAI (Paid API)
- **LLM Model**: `gpt-3.5-turbo` (or `gpt-4`)
- **Embedding Model**: `text-embedding-ada-002`

**Configuration**: Set `LLM_PROVIDER=ollama` or `LLM_PROVIDER=openai` in `.env`

---

## 🔍 What is RAG (Retrieval Augmented Generation)?

RAG is a technique that combines:
1. **Retrieval**: Finding relevant information from a knowledge base
2. **Augmentation**: Adding that information to the AI's context
3. **Generation**: Using the AI to generate answers based on the retrieved context

### Why RAG?
- **Prevents Hallucination**: AI only answers based on your actual documentation
- **Up-to-date Information**: Can update knowledge base without retraining the AI
- **Source Attribution**: Can cite which documents were used
- **Gap Detection**: Can identify when information is missing

---

## 📊 RAG Implementation in This Project

### RAG Model Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    RAG Pipeline                          │
└─────────────────────────────────────────────────────────┘

1. DOCUMENT INGESTION
   ├── PDF, DOCX, TXT, Markdown files
   ├── Confluence pages (via API)
   └── Text extraction & chunking

2. EMBEDDING GENERATION
   ├── Convert text chunks → Vector embeddings
   ├── Using: nomic-embed-text (Ollama) or text-embedding-ada-002 (OpenAI)
   └── Store in ChromaDB vector database

3. QUERY PROCESSING
   ├── User asks a question
   ├── Convert question → Vector embedding
   └── Search similar vectors in ChromaDB

4. RETRIEVAL
   ├── Find top 5 most similar document chunks
   ├── Calculate similarity scores (cosine similarity)
   └── Return relevant context

5. GENERATION
   ├── Send question + retrieved context to LLM
   ├── LLM generates answer based on context
   └── Return answer with sources

6. GAP DETECTION
   ├── Analyze similarity scores
   ├── Check for uncertainty phrases
   ├── Track repeated queries
   └── Flag knowledge gaps
```

---

## 🔄 Complete Project Flow

### Phase 1: Document Ingestion

```
User uploads documents
    ↓
DocumentIngestionService
    ├── Extract text (PDF, DOCX, TXT, MD)
    ├── Split into chunks (500-1000 chars)
    └── Prepare metadata (filename, chunk_id)
    ↓
ConfluenceIngestionService (Optional)
    ├── Fetch pages from Confluence
    ├── Convert HTML → Text
    └── Extract metadata (page_id, space_key)
    ↓
EmbeddingService
    ├── Generate embeddings for each chunk
    ├── Using: nomic-embed-text (Ollama) or text-embedding-ada-002 (OpenAI)
    └── Store in ChromaDB vector database
```

### Phase 2: Query Processing

```
User asks question via Dashboard/API
    ↓
RAGService.query()
    ├── Step 1: RETRIEVE
    │   ├── Convert question → embedding
    │   ├── Search ChromaDB for similar chunks
    │   ├── Get top 5 results with similarity scores
    │   └── Return: documents, scores, metadata
    │
    ├── Step 2: GENERATE
    │   ├── Build context from retrieved documents
    │   ├── Create prompt with context + question
    │   ├── Send to LLM (llama3.1:8b or gpt-3.5-turbo)
    │   └── Generate answer
    │
    └── Step 3: RETURN
        ├── Answer text
        ├── Source documents
        ├── Confidence score (avg similarity)
        └── Similarity scores
```

### Phase 3: Gap Detection

```
RAGService returns results
    ↓
GapDetectorService.detect_gap()
    ├── Rule 1: Low Similarity
    │   ├── Check if max similarity < 0.3
    │   └── Flag as "low_similarity" gap
    │
    ├── Rule 2: Empty Retrieval
    │   ├── Check if no documents found
    │   └── Flag as "empty_retrieval" gap (HIGH severity)
    │
    ├── Rule 3: Uncertainty Phrases
    │   ├── Check answer for phrases like "I'm not sure"
    │   └── Flag as "uncertainty" gap
    │
    └── Rule 4: Repeated Queries
        ├── Check if similar query asked 3+ times
        └── Flag as "repeated_query" gap (HIGH severity)
    ↓
Store gap in gaps.json
    ├── Track occurrence count
    ├── Track affected users
    └── Suggest documentation topic
```

### Phase 4: Dashboard Display

```
GapDetectorService
    ↓
FastAPI Endpoints
    ├── /gaps - List all gaps
    ├── /gaps/stats - Statistics
    └── /query - Query with gap detection
    ↓
Streamlit Dashboard
    ├── Display gaps with filters
    ├── Show analytics & charts
    └── Export gap data
```

---

## 🧠 Technical Components

### 1. EmbeddingService
**Purpose**: Convert text to vectors and manage vector database

**Technology**:
- **Embedding Models**:
  - Ollama: `nomic-embed-text` (768 dimensions)
  - OpenAI: `text-embedding-ada-002` (1536 dimensions)
- **Vector Database**: ChromaDB (persistent, local storage)
- **Similarity Metric**: Cosine similarity

**Process**:
```python
Text → Embedding Model → Vector (768 or 1536 numbers) → ChromaDB
```

### 2. RAGService
**Purpose**: Implement RAG pipeline (Retrieve + Generate)

**Components**:
- **Retrieval**: Vector similarity search in ChromaDB
- **Generation**: LLM-based answer generation
- **LLM Models**:
  - Ollama: `llama3.1:8b` (8B parameters, runs locally)
  - OpenAI: `gpt-3.5-turbo` or `gpt-4` (cloud API)

**RAG Prompt Structure**:
```
System: "You are a helpful assistant that answers questions based on provided context..."

Context from documentation:
[Document 1 - Relevance: 0.85]
<chunk text>

[Document 2 - Relevance: 0.72]
<chunk text>

Question: <user question>

Please provide an answer based on the context above.
```

### 3. GapDetectorService
**Purpose**: Detect knowledge gaps automatically

**Detection Rules**:
1. **Low Similarity**: Max similarity < 0.3 threshold
2. **Empty Retrieval**: No documents found
3. **Uncertainty Phrases**: Answer contains "I'm not sure", etc.
4. **Repeated Queries**: Same/similar query asked 3+ times

**Severity Levels**:
- **High**: Empty retrieval, repeated queries, very low similarity (<0.2)
- **Medium**: Low similarity (0.2-0.3), uncertainty phrases
- **Low**: Borderline cases

### 4. QuestionGeneratorService
**Purpose**: Generate suggested questions from knowledge base

**Process**:
1. Retrieve sample documents from ChromaDB
2. Extract titles and content snippets
3. Send to LLM with prompt to generate questions
4. Return list of suggested questions

---

## 📈 Data Flow Diagram

```
┌──────────────┐
│  Documents   │
│  (PDF/DOCX/  │
│  Confluence) │
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│  Ingestion      │
│  (Text Extract) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Chunking       │
│  (500-1000      │
│   chars)        │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│  Embedding      │──────▶│  ChromaDB    │
│  Generation     │       │  (Vector     │
│  (nomic-embed)  │       │   Store)     │
└─────────────────┘      └──────────────┘

┌──────────────┐
│  User Query  │
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│  Query          │
│  Embedding      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│  Vector Search  │──────▶│  Top 5 Docs  │
│  (ChromaDB)     │       │  + Scores    │
└──────┬──────────┘      └──────────────┘
       │
       ▼
┌─────────────────┐
│  LLM Generation │
│  (llama3.1:8b)  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Answer +       │
│  Sources        │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Gap Detection  │
│  (4 Rules)       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Dashboard      │
│  Display        │
└─────────────────┘
```

---

## 🔧 Key Technologies

### AI/ML Stack
- **LangChain**: RAG framework, LLM integration
- **Ollama**: Local LLM runtime (free)
- **OpenAI API**: Cloud LLM (paid alternative)
- **ChromaDB**: Vector database for embeddings

### Backend
- **FastAPI**: REST API framework
- **Python 3.9+**: Programming language

### Frontend
- **Streamlit**: Dashboard framework
- **Plotly**: Data visualization
- **Pandas**: Data manipulation

### Data Storage
- **ChromaDB**: Vector embeddings (persistent)
- **JSON**: Gap records (`data/gaps.json`)

---

## 🎯 What RAG Does Here

### 1. **Answer Questions**
- User asks: "How do we handle deployment rollbacks?"
- RAG retrieves relevant documentation chunks
- LLM generates answer based on retrieved context
- Returns answer with source citations

### 2. **Detect Knowledge Gaps**
- If similarity scores are low → Gap detected
- If no documents found → Gap detected
- If answer contains uncertainty → Gap detected
- If question asked multiple times → Gap detected

### 3. **Provide Insights**
- Track which questions can't be answered
- Identify missing documentation topics
- Measure documentation coverage
- Suggest areas needing documentation

---

## 📝 Example Flow

### Example 1: Successful Query

```
User: "How do we roll back a deployment?"

1. RAGService.retrieve()
   → Searches ChromaDB
   → Finds 5 relevant chunks (similarity: 0.85, 0.78, 0.72, 0.65, 0.58)
   
2. RAGService.generate_answer()
   → Sends context + question to llama3.1:8b
   → LLM generates: "To roll back a deployment, follow these steps..."
   
3. GapDetectorService.detect_gap()
   → Max similarity: 0.85 (> 0.3 threshold)
   → No uncertainty phrases
   → No gap detected ✅
   
4. Return to user:
   {
     "answer": "To roll back a deployment...",
     "sources": ["deployment-guide.pdf"],
     "confidence_score": 0.72,
     "is_gap": false
   }
```

### Example 2: Gap Detected

```
User: "How do we handle payment gateway failures?"

1. RAGService.retrieve()
   → Searches ChromaDB
   → Finds 2 chunks (similarity: 0.25, 0.18) ❌ Low similarity
   
2. RAGService.generate_answer()
   → LLM generates: "I'm not sure about payment gateway failures..."
   
3. GapDetectorService.detect_gap()
   → Max similarity: 0.25 (< 0.3 threshold) ❌
   → Contains "I'm not sure" ❌
   → Gap detected!
   
4. Create gap record:
   {
     "query": "How do we handle payment gateway failures?",
     "gap_type": "low_similarity",
     "severity": "high",
     "occurrence_count": 1,
     "suggested_topic": "Payment Gateway Failure Handling"
   }
   
5. Return to user:
   {
     "answer": "I'm not sure about payment gateway failures...",
     "is_gap": true,
     "gap_reason": "Low similarity score: 0.25"
   }
```

---

## 🚀 Why This Architecture?

### Benefits
1. **Free & Local**: Uses Ollama (no API costs)
2. **Accurate**: RAG prevents AI hallucination
3. **Gap Detection**: Automatically finds missing docs
4. **Scalable**: Can handle thousands of documents
5. **Flexible**: Supports multiple LLM providers

### Use Cases
- **Documentation Q&A**: Answer questions from company docs
- **Knowledge Gap Analysis**: Find missing documentation
- **Onboarding**: Help new employees find information
- **Compliance**: Ensure critical processes are documented

---

## 📚 Summary

**RAG Model**: Custom implementation using LangChain
- **Retrieval**: ChromaDB vector search
- **Generation**: Ollama (llama3.1:8b) or OpenAI (gpt-3.5-turbo)

**AI Models**:
- **LLM**: llama3.1:8b (default) or gpt-3.5-turbo
- **Embeddings**: nomic-embed-text (default) or text-embedding-ada-002

**What RAG Does**:
1. Converts documents to searchable vectors
2. Finds relevant information for questions
3. Generates accurate answers based on your docs
4. Detects when information is missing

**Project Flow**:
Ingestion → Embedding → Storage → Query → Retrieval → Generation → Gap Detection → Dashboard
