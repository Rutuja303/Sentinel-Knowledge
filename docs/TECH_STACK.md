# Technology Stack - Sentinel Knowledge

## 🤖 AI Models & LLMs

| Tool/Model | What It Is | Why We Use It |
|------------|------------|---------------|
| **llama3.1:8b** | 8-billion parameter open-source LLM from Meta | Free, runs locally via Ollama, generates answers from retrieved context |
| **nomic-embed-text** | Text embedding model (768 dimensions) | Converts documents and queries into searchable vectors for similarity matching |
| **gpt-3.5-turbo** | OpenAI's cloud-based LLM (alternative) | Paid alternative when OpenAI API is preferred over local Ollama |
| **text-embedding-ada-002** | OpenAI's embedding model (1536 dimensions) | Alternative embedding model when using OpenAI instead of Ollama |

## 🛠️ AI/ML Frameworks & Tools

| Tool | What It Is | Why We Use It |
|------|------------|---------------|
| **LangChain** | Python framework for building LLM applications | Provides RAG pipeline, LLM integration, and standardized interfaces for embeddings |
| **Ollama** | Local LLM runtime and API server | Enables free, local execution of LLMs without cloud API costs |
| **OpenAI API** | Cloud-based LLM service (alternative) | Provides access to GPT models when local execution isn't preferred |
| **langchain-ollama** | LangChain integration for Ollama | Connects LangChain to Ollama for local LLM execution |
| **langchain-openai** | LangChain integration for OpenAI | Connects LangChain to OpenAI API for cloud LLM execution |
| **langchain-community** | Community integrations for LangChain | Provides additional embeddings and LLM integrations |

## 💾 Databases & Storage

| Tool | What It Is | Why We Use It |
|------|------------|---------------|
| **ChromaDB** | Open-source vector database | Stores document embeddings for fast similarity search and retrieval |
| **JSON Files** | Simple file-based storage | Stores gap detection records and query history (lightweight, no DB setup needed) |

## 🌐 Backend Framework & APIs

| Tool | What It Is | Why We Use It |
|------|------------|---------------|
| **FastAPI** | Modern Python web framework | Builds REST API endpoints for querying, ingestion, and gap management |
| **Pydantic** | Data validation library | Validates API request/response schemas and configuration |
| **Uvicorn** | ASGI web server | Runs the FastAPI application with hot-reload support |
| **atlassian-python-api** | Python client for Atlassian APIs | Fetches pages and spaces from Confluence for document ingestion |
| **requests** | HTTP library | Makes API calls to Confluence, OpenAI, and internal endpoints |

## 🎨 Frontend Framework & Visualization

| Tool | What It Is | Why We Use It |
|------|------------|---------------|
| **Streamlit** | Python web app framework | Creates interactive dashboard for querying, gap analysis, and visualization |
| **Plotly** | Interactive visualization library | Generates charts and graphs for gap analytics (pie charts, bar charts, etc.) |
| **Pandas** | Data manipulation library | Processes gap data, filters, and prepares data for visualization |

## 📄 Document Processing

| Tool | What It Is | Why We Use It |
|------|------------|---------------|
| **PyPDF2** | PDF parsing library | Extracts text from PDF documents for ingestion |
| **python-docx** | Word document parser | Extracts text from DOCX files for ingestion |
| **BeautifulSoup4** | HTML/XML parser | Parses HTML content from Confluence pages |
| **html2text** | HTML to text converter | Converts Confluence HTML content to plain text for processing |

## 🔧 Utilities & Configuration

| Tool | What It Is | Why We Use It |
|------|------------|---------------|
| **python-dotenv** | Environment variable loader | Loads API keys and configuration from `.env` file securely |
| **email-validator** | Email validation library | Validates email formats in configuration (Pydantic dependency) |

## 📊 Summary by Category

### AI/ML Stack
- **LLMs**: llama3.1:8b (default), gpt-3.5-turbo (alternative)
- **Embeddings**: nomic-embed-text (default), text-embedding-ada-002 (alternative)
- **Framework**: LangChain
- **Runtime**: Ollama (local) or OpenAI API (cloud)

### Data Storage
- **Vector DB**: ChromaDB (embeddings)
- **File Storage**: JSON (gap records)

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Validation**: Pydantic

### Frontend
- **Framework**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas

### Document Processing
- **PDF**: PyPDF2
- **DOCX**: python-docx
- **HTML**: BeautifulSoup4, html2text
- **Confluence**: atlassian-python-api

---

## 🎯 Why This Stack?

### Free & Open Source
- Ollama + llama3.1:8b = No API costs
- ChromaDB = Free vector database
- All core tools are open-source

### Local Execution
- Runs entirely on your machine
- No data sent to external APIs (with Ollama)
- Privacy-friendly

### Flexible
- Can switch between Ollama and OpenAI
- Supports multiple document formats
- Extensible architecture

### Production-Ready
- FastAPI for scalable APIs
- Streamlit for quick dashboards
- ChromaDB for efficient vector search
