# 🦙 Ollama Quick Start

## Recommended Models for This Project

### ✅ LLM Model: `llama3.1:8b`
- **Best for**: RAG/knowledge base Q&A
- **Size**: ~4.7GB
- **Speed**: Fast
- **Quality**: High

### ✅ Embedding Model: `nomic-embed-text`
- **Best for**: Vector embeddings
- **Size**: ~274MB
- **Dimensions**: 768
- **Purpose**: Specifically designed for embeddings

## Quick Setup (5 minutes)

### 1. Install Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.ai
```

### 2. Start Ollama
```bash
ollama serve
```

### 3. Pull Models
```bash
# Pull LLM model
ollama pull llama3.1:8b

# Pull embedding model
ollama pull nomic-embed-text
```

### 4. Configure .env
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### 5. Run Application
```bash
# Make sure Ollama is running
ollama serve

# Start the API
uvicorn app.main:app --reload
```

## Verify Installation

```bash
# Check if models are available
ollama list

# Test LLM
ollama run llama3.1:8b "Hello"

# Test if Ollama is running
curl http://localhost:11434/api/tags
```

## That's It! 🎉

Your application now uses free, local LLM models. No API keys needed!
