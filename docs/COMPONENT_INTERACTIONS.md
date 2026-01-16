# Component Interactions & Gap Analysis Deep Dive

## 🔄 How Components Interact: Complete Flow

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT (Frontend)                     │
│                  Port 8501 - User Interface                 │
│  • Dashboard, Query Interface, Gap Analysis, Confluence     │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ HTTP REST API Calls
                         │ (GET, POST requests)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI (Backend API)                     │
│                  Port 8000 - API Server                      │
│  • /query, /gaps, /ingest, /analyze endpoints               │
│  • Request routing, validation, response formatting          │
└───────┬───────────────────────┬─────────────────────────────┘
        │                       │
        │                       │
        ▼                       ▼
┌──────────────┐      ┌──────────────────────────┐
│   RAG        │      │   Gap Detector           │
│   Service    │      │   Service                │
│              │      │                          │
│  • Retrieve  │      │  • Analyze results       │
│  • Generate  │      │  • Detect gaps           │
│              │      │  • Store in gaps.json    │
└──────┬───────┘      └──────────────────────────┘
       │
       │ Uses
       ▼
┌─────────────────────────────────────────────────────────────┐
│              EMBEDDING SERVICE                               │
│  • Converts text → vectors (embeddings)                     │
│  • Manages ChromaDB connection                              │
│  • Handles search operations                                │
└───────┬─────────────────────────────────────────────────────┘
        │
        │ Queries/Stores
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CHROMADB                                  │
│              (Vector Database)                               │
│  • Stores document embeddings (vectors)                     │
│  • Stores text chunks                                        │
│  • Stores metadata (title, source, page_id, etc.)           │
│  • Fast similarity search                                    │
└─────────────────────────────────────────────────────────────┘
        │
        │ (Embedding Service uses)
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM (Language Model)                      │
│  • Ollama (local) or OpenAI (cloud)                         │
│  • Generates answers from context                           │
│  • Used by RAG Service for answer generation                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Detailed Component Interactions

### 1. Query Flow: How Everything Works Together

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: User Enters Question in Streamlit                  │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ User types: "What are key fields in orders table?"
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Streamlit → FastAPI                                │
│  POST /query                                                │
│  {                                                          │
│    "question": "What are key fields in orders table?",     │
│    "user_id": "user123"                                    │
│  }                                                          │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: FastAPI Endpoint (/query)                          │
│  • Validates request                                        │
│  • Calls: rag_service.query(question)                      │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: RAG Service - RETRIEVE Phase                       │
│  rag_service.query()                                        │
│    ↓                                                        │
│  rag_service.retrieve(question)                            │
│    ↓                                                        │
│  embedding_service.search(question, n_results=10)           │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Embedding Service → ChromaDB                       │
│  • Convert question to embedding vector                    │
│  • Search ChromaDB for similar vectors                      │
│  • Return top 10 most similar document chunks              │
│  • Return: documents, distances, metadatas                  │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ Returns:
                         │ {
                         │   "documents": ["chunk1", "chunk2", ...],
                         │   "distances": [0.15, 0.23, ...],
                         │   "metadatas": [{title: "...", ...}, ...]
                         │ }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: RAG Service - GENERATE Phase                       │
│  • Build context from retrieved documents                   │
│  • Create prompt with context + question                    │
│  • Call: llm.invoke(messages)                               │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: LLM (Ollama/OpenAI)                                │
│  • Receives: System prompt + Context + Question            │
│  • Generates: Natural language answer                       │
│  • Returns: "Based on the documentation, the orders table  │
│             contains: order_id, customer_id, amount..."    │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ Returns answer
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: RAG Service Returns Result                         │
│  {                                                          │
│    "answer": "Based on documentation...",                  │
│    "sources": ["DBT Design Document"],                     │
│    "confidence_score": 0.85,                                │
│    "similarity_scores": [0.85, 0.72, ...],                 │
│    "retrieved_documents": [...],                            │
│    "metadatas": [...]                                       │
│  }                                                          │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 9: FastAPI → Gap Detector                             │
│  gap_detector.detect_gap(                                   │
│    query=question,                                          │
│    answer=rag_result["answer"],                             │
│    similarity_scores=rag_result["similarity_scores"],       │
│    retrieved_documents=rag_result["retrieved_documents"],   │
│    metadatas=rag_result["metadatas"]                       │
│  )                                                          │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 10: Gap Detector Analyzes                             │
│  • Checks if documents were found                           │
│  • Checks answer quality                                    │
│  • Checks for uncertainty phrases                           │
│  • Checks for inconsistencies                               │
│  • If gap detected → Save to gaps.json                     │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ Returns gap object or None
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 11: FastAPI Builds Response                           │
│  {                                                          │
│    "answer": "...",                                         │
│    "sources": [...],                                        │
│    "confidence_score": 0.85,                                │
│    "is_gap": true,                                          │
│    "gap_reason": "incomplete_knowledge"                      │
│  }                                                          │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ HTTP Response
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 12: Streamlit Displays                                │
│  • Shows answer to user                                     │
│  • Shows sources                                            │
│  • Shows gap indicator (if detected)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 How Gap Analysis Works - Detailed Breakdown

### Gap Detection Logic Flow

```
┌─────────────────────────────────────────────────────────────┐
│              GAP DETECTION PROCESS                           │
└─────────────────────────────────────────────────────────────┘

Inputs from RAG:
  • query: User's question
  • answer: LLM-generated answer
  • similarity_scores: [0.85, 0.72, 0.65, ...]
  • retrieved_documents: ["chunk1", "chunk2", ...]
  • metadatas: [{title: "...", page_id: "..."}, ...]

         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ RULE 1: Missing Knowledge Check                            │
│  if len(retrieved_documents) == 0:                          │
│    → Gap Type: "missing_knowledge"                           │
│    → Severity: "high"                                       │
│    → Reason: "No relevant documents found"                  │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ If no gap detected
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ RULE 2: Incomplete Knowledge Check                         │
│  Check answer for:                                          │
│  • Uncertainty phrases: "I'm not sure", "unclear", etc.     │
│  • Missing indicators: "not defined", "not specified", etc.  │
│                                                             │
│  if uncertainty phrase found:                               │
│    → Gap Type: "incomplete_knowledge"                       │
│    → Severity: "medium"                                     │
│                                                             │
│  if missing indicator + multiple docs:                     │
│    → Gap Type: "incomplete_knowledge"                       │
│    → Severity: "high"                                       │
│    → Reason: "Mentioned in one doc but missing in another" │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ If no gap detected
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ RULE 3: Consistency Gap Check                               │
│  if len(retrieved_documents) > 1:                           │
│    Check for:                                               │
│    • Contradiction phrases: "however", "but", "conflicts"   │
│    • Multiple sources with different info                   │
│    • Mismatch patterns: "4 listed but 3 defined"            │
│                                                             │
│  if contradiction found:                                   │
│    → Gap Type: "consistency_gap"                            │
│    → Severity: "high"                                       │
│    → Reason: "Conflicting information across documents"    │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ If no gap detected
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ RULE 4: Fragmented Knowledge Check                          │
│  if len(retrieved_documents) > 3:                           │
│    → Gap Type: "fragmented_knowledge"                       │
│    → Severity: "medium"                                     │
│    → Reason: "Information spread across many documents"     │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ If no gap detected
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ RULE 5: Discoverability Gap Check                          │
│  if max(similarity_scores) < 0.3:                           │
│    → Gap Type: "discoverability_gap"                        │
│    → Severity: "low"                                        │
│    → Reason: "Knowledge exists but hard to find"            │
└───────────────────────┬─────────────────────────────────────┘
                         │
                         │ If gap detected
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Save Gap to gaps.json                                       │
│  {                                                          │
│    "id": "abc123",                                          │
│    "query": "What are key fields...",                       │
│    "gap_type": "incomplete_knowledge",                      │
│    "severity": "high",                                      │
│    "occurrence_count": 1,                                   │
│    "source_page_title": "DBT Design Document",              │
│    "suggested_topic": "Orders Table Fields"                 │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 Component Interaction Details

### 1. Streamlit ↔ FastAPI Interaction

**How They Communicate:**
```python
# Streamlit (Frontend)
import requests

# Make API call
response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What are key fields?", "user_id": "user123"}
)

# Process response
data = response.json()
answer = data["answer"]
is_gap = data["is_gap"]
```

**FastAPI (Backend):**
```python
@app.post("/query")
async def query_knowledge_base(request: QueryRequest):
    # Process request
    rag_result = rag_service.query(request.question)
    gap = gap_detector.detect_gap(...)
    
    # Return response
    return QueryResponse(
        answer=rag_result["answer"],
        is_gap=gap is not None,
        ...
    )
```

**Communication Pattern:**
- **Protocol**: HTTP REST API
- **Format**: JSON (request & response)
- **Ports**: Streamlit (8501) → FastAPI (8000)
- **Methods**: GET, POST
- **CORS**: Enabled for cross-origin requests

---

### 2. FastAPI ↔ RAG Service Interaction

**How They Work Together:**
```python
# FastAPI calls RAG Service
rag_result = rag_service.query(question)

# RAG Service returns:
{
    "answer": "Generated answer...",
    "sources": ["doc1", "doc2"],
    "similarity_scores": [0.85, 0.72],
    "retrieved_documents": ["chunk1", "chunk2"],
    "metadatas": [{...}, {...}]
}
```

**RAG Service Internal Flow:**
```python
class RAGService:
    def query(self, question):
        # Step 1: Retrieve
        documents, scores, metadatas = self.retrieve(question)
        # Uses: embedding_service.search()
        
        # Step 2: Generate
        answer = self.generate_answer(question, documents, scores)
        # Uses: llm.invoke()
        
        return {
            "answer": answer,
            "sources": ...,
            ...
        }
```

---

### 3. RAG Service ↔ Embedding Service Interaction

**How They Work Together:**
```python
# RAG Service uses Embedding Service
class RAGService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
    
    def retrieve(self, query):
        # Call embedding service to search
        results = self.embedding_service.search(query, n_results=10)
        # Returns: documents, distances, metadatas
```

**Embedding Service Responsibilities:**
- Converts text to embeddings (vectors)
- Manages ChromaDB connection
- Performs similarity search
- Returns results with metadata

---

### 4. Embedding Service ↔ ChromaDB Interaction

**How They Work Together:**
```python
# Embedding Service uses ChromaDB
class EmbeddingService:
    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection("knowledge_base")
    
    def search(self, query, n_results=10):
        # Convert query to embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return {
            "documents": results["documents"][0],
            "distances": results["distances"][0],
            "metadatas": results["metadatas"][0]
        }
```

**ChromaDB Structure:**
```
Collection: "knowledge_base"
  ├── Embeddings: [vector1, vector2, ...] (768 or 1536 dimensions)
  ├── Documents: ["chunk1 text", "chunk2 text", ...]
  ├── Metadatas: [{title: "...", source: "...", ...}, ...]
  └── IDs: ["doc1_chunk0", "doc1_chunk1", ...]
```

**Operations:**
- **Add**: Store new document chunks with embeddings
- **Query**: Search for similar vectors (cosine similarity)
- **Get**: Retrieve documents by ID
- **Delete**: Remove documents (e.g., by source)

---

### 5. RAG Service ↔ LLM Interaction

**How They Work Together:**
```python
# RAG Service uses LLM
class RAGService:
    def __init__(self, embedding_service):
        # Initialize LLM (Ollama or OpenAI)
        if config.LLM_PROVIDER == "ollama":
            self.llm = ChatOllama(model="gemma3:latest")
        else:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    def generate_answer(self, query, context_docs, scores):
        # Build prompt
        messages = [
            SystemMessage(content="You are a helpful assistant..."),
            HumanMessage(content=f"""
                Context: {context_docs}
                Question: {query}
            """)
        ]
        
        # Call LLM
        response = self.llm.invoke(messages)
        return response.content
```

**LLM Options:**

**Option 1: Ollama (Local)**
```
RAG Service → Ollama API (localhost:11434)
  • Model: gemma3:latest (or llama3.1:8b)
  • Runs locally
  • No API costs
  • Private (data stays local)
```

**Option 2: OpenAI (Cloud)**
```
RAG Service → OpenAI API (api.openai.com)
  • Model: gpt-3.5-turbo or gpt-4
  • Cloud-based
  • Requires API key
  • More powerful
```

**Prompt Structure:**
```
System: "You are a helpful assistant that answers questions 
         based on provided context..."

Context from documentation:
[Document 1 - Relevance: 0.85]
<chunk text>

[Document 2 - Relevance: 0.72]
<chunk text>

Question: <user question>

Please provide an answer based on the context above.
```

---

### 6. FastAPI ↔ Gap Detector Interaction

**How They Work Together:**
```python
# FastAPI calls Gap Detector
gap = gap_detector.detect_gap(
    query=request.question,
    answer=rag_result["answer"],
    similarity_scores=rag_result["similarity_scores"],
    retrieved_documents=rag_result["retrieved_documents"],
    metadatas=rag_result["metadatas"]
)

# Gap Detector analyzes and returns KnowledgeGap or None
if gap:
    # Gap detected - saved to gaps.json
    # Returns gap object
else:
    # No gap - returns None
```

**Gap Detector Storage:**
```python
# Gap Detector saves to gaps.json
class GapDetectorService:
    def save_gaps(self):
        data = {
            "gaps": {gap_id: gap.dict() for gap_id, gap in self.gaps.items()},
            "query_history": self.query_history
        }
        with open("data/gaps.json", "w") as f:
            json.dump(data, f)
```

---

### 7. Streamlit ↔ Gap Analysis Display

**How Gap Analysis Works:**
```python
# Streamlit fetches gaps
def fetch_gaps(limit=1000):
    response = requests.get(
        "http://localhost:8000/gaps",
        params={"limit": limit}
    )
    return response.json()

# FastAPI returns gaps
@app.get("/gaps")
async def get_knowledge_gaps():
    gaps = gap_detector.get_all_gaps()
    return [gap.dict() for gap in gaps]

# Streamlit displays
gaps = fetch_gaps()
df = pd.DataFrame(gaps)
st.dataframe(df)  # Display in table
```

**Data Flow:**
```
Gap Detector (gaps.json)
    ↓
FastAPI /gaps endpoint
    ↓
Streamlit fetch_gaps()
    ↓
Display in Gap Analysis page
```

---

## 🔄 Complete Interaction Sequence

### Example: User Asks Question

```
1. USER (Streamlit UI)
   Types: "What are key fields in orders table?"
   ↓
2. STREAMLIT
   requests.post("http://localhost:8000/query", {...})
   ↓
3. FASTAPI
   @app.post("/query") receives request
   ↓
4. RAG SERVICE
   rag_service.query(question)
   ↓
5. EMBEDDING SERVICE
   embedding_service.search(question)
   ↓
6. CHROMADB
   collection.query(query_embeddings=[...])
   Returns: documents, distances, metadatas
   ↓
7. EMBEDDING SERVICE
   Returns results to RAG Service
   ↓
8. RAG SERVICE
   Builds context, calls llm.invoke()
   ↓
9. LLM (Ollama/OpenAI)
   Generates answer from context
   Returns: "Based on documentation, orders table contains..."
   ↓
10. RAG SERVICE
    Returns: {answer, sources, scores, ...}
    ↓
11. FASTAPI
    Calls gap_detector.detect_gap(...)
    ↓
12. GAP DETECTOR
    Analyzes: answer quality, similarity scores, etc.
    Detects gap → Saves to gaps.json
    Returns: gap object
    ↓
13. FASTAPI
    Builds response: {answer, is_gap: true, gap_reason: ...}
    ↓
14. STREAMLIT
    Receives response, displays answer + gap indicator
    ↓
15. USER
    Sees answer and knows a gap was detected
```

---

## 📦 Data Flow Between Components

### Document Ingestion Flow

```
Local Files/Confluence
    ↓
Ingestion Service
    ↓
Chunk Documents
    ↓
Embedding Service
    ↓
Generate Embeddings
    ↓
ChromaDB
    Store: embeddings + chunks + metadata
```

### Query Flow

```
User Question
    ↓
FastAPI /query
    ↓
RAG Service
    ↓
Embedding Service → ChromaDB (search)
    ↓
RAG Service → LLM (generate)
    ↓
Gap Detector (analyze)
    ↓
FastAPI (response)
    ↓
Streamlit (display)
```

### Gap Analysis Flow

```
Gap Detector (gaps.json)
    ↓
FastAPI /gaps
    ↓
Streamlit fetch_gaps()
    ↓
Display in table/charts
```

---

## 🎯 Key Interaction Patterns

### 1. **Request-Response Pattern**
- Streamlit makes HTTP requests
- FastAPI processes and responds
- Synchronous communication

### 2. **Service Dependency Pattern**
- RAG Service depends on Embedding Service
- Embedding Service depends on ChromaDB
- Services are injected (dependency injection)

### 3. **Shared State Pattern**
- Gap Detector maintains gaps.json
- Both query and analysis use same storage
- Real-time updates across UI

### 4. **Lazy Initialization Pattern**
- Services initialize only when needed
- Handles missing API keys gracefully
- Optional services don't break app

### 5. **RAG Pattern**
- Retrieve: Search ChromaDB
- Augment: Add context to prompt
- Generate: LLM creates answer

---

## 🔍 Gap Analysis: Two Methods

### Method 1: Real-Time Detection (During Queries)

```
Every Query → Gap Detection
    ↓
Analyze: answer quality, similarity, sources
    ↓
If gap detected → Save to gaps.json
    ↓
Appears in Gap Analysis table
```

**When It Happens:**
- User asks question in Query Interface
- System processes query
- Gap detected automatically
- Saved immediately

### Method 2: Bulk Analysis (Cross-Document)

```
All Documents → Extract Entities
    ↓
Compare Documents
    ↓
Find: inconsistencies, missing info, undefined terms
    ↓
Save gaps to gaps.json
    ↓
Appears in Gap Analysis table
```

**When It Happens:**
- User clicks "Analyze All Confluence Data"
- System processes all documents
- CrossDocumentAnalyzer finds gaps
- All gaps saved at once

**Both Methods:**
- Use same GapDetectorService
- Save to same gaps.json
- Display in same Gap Analysis table

---

## 💡 Summary: How Everything Connects

1. **Streamlit** = User Interface (what users see and interact with)
2. **FastAPI** = API Server (routes requests, coordinates services)
3. **RAG Service** = Brain (retrieves + generates answers)
4. **Embedding Service** = Search Engine (finds similar content)
5. **ChromaDB** = Memory (stores all document vectors)
6. **LLM** = Answer Generator (creates natural language answers)
7. **Gap Detector** = Quality Inspector (finds documentation problems)

**The Flow:**
- User asks question → Streamlit → FastAPI → RAG → Embedding → ChromaDB
- ChromaDB returns docs → RAG → LLM → Answer
- Answer analyzed → Gap Detector → gaps.json
- Gaps displayed → Streamlit Gap Analysis page

All components work together to create an intelligent documentation system that answers questions and automatically identifies what needs to be documented better.
