# AI Knowledge Gap Detector

**"Your company doesn't know what it doesn't know — until now."**

## 🎯 Overview

An intelligent system that not only answers questions using RAG (Retrieval Augmented Generation) but also detects and flags knowledge gaps when it cannot properly answer questions. This helps organizations identify missing documentation, single-owner knowledge risks, and areas that need better coverage.

## ✨ Key Features

- **RAG-Powered Q&A**: Answers questions using your company's documentation
- **Gap Detection**: Automatically identifies missing or weak knowledge areas
- **Real-time Dashboard**: Visualizes knowledge gaps, repeated queries, and documentation risks
- **Multi-format Support**: Ingests PDFs, DOCX, TXT, Markdown files
- **Confluence Integration**: Direct integration with Confluence to ingest pages and spaces
- **Query Analytics**: Tracks unanswered questions and identifies patterns

## 🏗️ Architecture

```
┌─────────────────┐
│  Document       │
│  Ingestion      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │
│  (ChromaDB)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│  RAG System     │──────▶│  Gap Detection  │
│  (Retrieval +   │      │  Engine         │
│   Generation)   │      └────────┬────────┘
└────────┬────────┘               │
         │                        ▼
         ▼              ┌─────────────────┐
┌─────────────────┐     │   Dashboard     │
│  Chat Interface │     │   (Streamlit)  │
└─────────────────┘     └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Confluence account (optional, for Confluence integration)

### Installation

**Option 1: Automated Setup (Recommended)**
```bash
# Clone the repository
git clone <repo-url>
cd Sentinel-Knowledge

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Edit .env and add your OPENAI_API_KEY
nano .env  # or use your preferred editor
```

**Option 2: Manual Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Application

**Step 1: Start the FastAPI Backend**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start the API server
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Step 2: Start the Streamlit Dashboard** (in a new terminal)
```bash
# Activate virtual environment
source venv/bin/activate

# Start the dashboard
streamlit run dashboard/app.py

# Dashboard will open in your browser at http://localhost:8501
```

**Step 3: Ingest Documents**

**Option A: Local Files**
```bash
# Place your documents (PDF, DOCX, TXT, MD) in data/documents/
curl -X POST http://localhost:8000/ingest

# Or upload a single file
curl -X POST -F "file=@your-document.pdf" http://localhost:8000/ingest/file
```

**Option B: Confluence Integration**
```bash
# Get list of Confluence spaces
curl http://localhost:8000/confluence/spaces

# Ingest from a specific space
curl -X POST http://localhost:8000/ingest/confluence \
  -H "Content-Type: application/json" \
  -d '{"space_key": "YOUR_SPACE_KEY", "limit": 1000}'

# Ingest from all spaces
curl -X POST http://localhost:8000/ingest/confluence \
  -H "Content-Type: application/json" \
  -d '{"limit": 1000}'
```

### First Query Example

```bash
# Query the knowledge base
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do we handle deployment rollbacks?"}'
```

Or use the Streamlit dashboard's Query Interface!

## 📋 Project Structure

```
Sentinel-Knowledge/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/              # Data models
│   ├── services/
│   │   ├── ingestion.py     # Document ingestion
│   │   ├── embeddings.py    # Vector embeddings
│   │   ├── rag.py          # RAG system
│   │   └── gap_detector.py # Gap detection logic
│   └── utils/
├── dashboard/
│   └── app.py              # Streamlit dashboard
├── data/
│   └── documents/          # Place documents here
├── .env.example
├── requirements.txt
└── README.md
```

## 🔍 How Gap Detection Works

The system uses four detection rules to identify knowledge gaps:

1. **Low Similarity Score**: When retrieved documents have similarity scores below the threshold (default: 0.3)
   - High severity if max similarity < 0.2
   - Medium severity if max similarity < 0.3

2. **Repeated Queries**: Same or similar questions asked multiple times (default: 3+) without good answers
   - Uses word overlap analysis to detect similar queries
   - Tracks occurrence count and affected users

3. **Uncertainty Phrases**: AI responses contain uncertainty indicators
   - Phrases like "I'm not sure", "I don't have information", "I cannot find"
   - Configurable via `UNCERTAINTY_PHRASES` in `.env`

4. **Empty Retrieval**: No relevant documents found for the query
   - Highest severity gap type
   - Indicates complete absence of documentation

Each detected gap includes:
- Query that revealed the gap
- Gap type and severity
- Occurrence count
- Affected users
- Suggested documentation topic

## 📊 Dashboard Features

The Streamlit dashboard provides three main views:

### 1. Dashboard
- **Key Metrics**: Total queries, knowledge gaps, gap rate, high severity gaps
- **Visualizations**: Gap type distribution, severity breakdown
- **Top Gaps**: List of most critical knowledge gaps with details

### 2. Query Interface
- Interactive Q&A interface
- Real-time gap detection
- Confidence scores and similarity metrics
- Source document citations

### 3. Gap Analysis
- Filterable gap list (by severity)
- Detailed gap information table
- Charts: Gaps by type, top queries by occurrence
- Export capabilities

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check and vector store stats |
| `/query` | POST | Query knowledge base |
| `/ingest` | POST | Ingest all documents from data/documents/ |
| `/ingest/file` | POST | Upload and ingest a single file |
| `/ingest/confluence` | POST | Ingest pages from Confluence |
| `/confluence/spaces` | GET | Get all accessible Confluence spaces |
| `/confluence/spaces/{key}/pages` | GET | Get pages from a specific space |
| `/confluence/pages/{id}` | GET | Get a specific Confluence page |
| `/gaps` | GET | Get knowledge gaps (with optional filters) |
| `/gaps/stats` | GET | Get gap statistics |
| `/gaps/{gap_id}` | DELETE | Delete a specific gap |

See interactive API docs at `http://localhost:8000/docs` when the server is running.

## 📝 Usage Examples

### Example 1: Detecting a Knowledge Gap

```python
import requests

# Ask a question about something not in your docs
response = requests.post("http://localhost:8000/query", json={
    "question": "How do we handle payment gateway failures?",
    "user_id": "user123"
})

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Is Gap: {result['is_gap']}")
print(f"Confidence: {result['confidence_score']}")
```

### Example 2: Checking Knowledge Gaps

```python
# Get all high severity gaps
gaps = requests.get("http://localhost:8000/gaps?severity=high").json()

for gap in gaps:
    print(f"Query: {gap['query']}")
    print(f"Type: {gap['gap_type']}")
    print(f"Occurrences: {gap['occurrence_count']}")
    print(f"Suggested Topic: {gap['suggested_topic']}")
```

### Example 3: Ingesting Documents

```python
# Ingest all documents from data/documents/
response = requests.post("http://localhost:8000/ingest")
print(response.json())

# Or upload a single file
with open("my-doc.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/ingest/file", files=files)
    print(response.json())
```

## ⚙️ Configuration

Edit `.env` to customize. See [Configuration Guide](./docs/SETUP.md#configuration) for details.

**Quick Configuration:**
```env
# LLM Provider (ollama = free, openai = paid)
LLM_PROVIDER=ollama

# Ollama (Free & Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Confluence Integration (Optional)
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your_confluence_api_token
CONFLUENCE_SPACE_KEY=  # Optional: specific space key (e.g., HR, SOP, ENG)
```

**For detailed configuration, see:**
- [Ollama Setup](./docs/OLLAMA_SETUP.md) - Free local LLM
- [Confluence Setup](./docs/CONFLUENCE_SETUP.md) - Confluence integration
- [API Keys Guide](./docs/API_KEYS_GUIDE.md) - All API keys needed

## 🧪 Testing the System

1. **Add some test documents** to `data/documents/`
2. **Ingest them**: `POST /ingest`
3. **Ask a well-documented question**: Should get a good answer
4. **Ask about something not documented**: Should detect a gap
5. **Check the dashboard**: See the gap appear in real-time

## 🛠️ Development Status

✅ **MVP Complete** - Core functionality implemented:
- ✅ Document ingestion (PDF, DOCX, TXT, MD)
- ✅ Vector embeddings with ChromaDB
- ✅ RAG system with OpenAI
- ✅ Gap detection (4 detection rules)
- ✅ FastAPI backend
- ✅ Streamlit dashboard
- ✅ Query analytics

## 📚 Documentation

All detailed documentation is available in the [`docs/`](./docs/) directory:

- **[API Keys Guide](./docs/API_KEYS_GUIDE.md)** - How to get and configure API keys
- **[Setup Guide](./docs/SETUP.md)** - Detailed setup instructions
- **[Quick Start](./docs/QUICKSTART.md)** - 5-minute quick start guide
- **[Ollama Setup](./docs/OLLAMA_SETUP.md)** - Free local LLM setup
- **[Confluence Setup](./docs/CONFLUENCE_SETUP.md)** - Confluence integration guide
- **[Confluence Space Key Examples](./docs/CONFLUENCE_SPACE_KEY_EXAMPLE.md)** - Space key reference
- **[Dashboard Features](./docs/DASHBOARD_FEATURES.md)** - Dashboard functionality
- **[Dynamic Questions](./docs/DYNAMIC_QUESTIONS.md)** - How question generation works
- **[Troubleshooting](./docs/CONFLUENCE_TROUBLESHOOTING.md)** - Common issues and solutions

## 🚧 Future Enhancements

- [ ] Support for more document formats (Excel, PowerPoint)
- [ ] Multi-user authentication
- [ ] Email notifications for high-severity gaps
- [x] Integration with Confluence ✅
- [ ] Advanced analytics and reporting
- [ ] Export gaps to CSV/PDF
- [ ] Slack/Teams integration

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT

## 🙏 Acknowledgments

Built for hackathon demonstration. Inspired by the need to make knowledge gaps visible and actionable.
