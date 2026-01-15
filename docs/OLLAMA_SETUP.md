# 🦙 Ollama Setup Guide

## Overview

This project now supports **Ollama** (free, local LLM) as an alternative to OpenAI. Ollama runs models locally on your machine, so it's completely free and private!

## Recommended Models

### For LLM (Question Answering)
- **`llama3.1:8b`** ⭐ **RECOMMENDED**
  - Best balance of quality and speed
  - Good for RAG/knowledge base Q&A
  - ~4.7GB download

- **Alternative options:**
  - `llama3:8b` - Slightly older but still good
  - `mistral:7b` - Good for technical content
  - `llama3.1:70b` - Better quality but slower (requires more RAM)

### For Embeddings
- **`nomic-embed-text`** ⭐ **RECOMMENDED**
  - Specifically designed for embeddings
  - Works perfectly with RAG systems
  - ~274MB download
  - 768-dimensional embeddings

## Installation

### Step 1: Install Ollama

**macOS:**
```bash
brew install ollama
# or download from https://ollama.ai
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from: https://ollama.ai/download

### Step 2: Start Ollama

```bash
ollama serve
```

This starts Ollama on `http://localhost:11434`

### Step 3: Pull Required Models

```bash
# Pull the LLM model
ollama pull llama3.1:8b

# Pull the embedding model
ollama pull nomic-embed-text
```

### Step 4: Verify Installation

```bash
# Test LLM
ollama run llama3.1:8b "Hello, how are you?"

# Test embeddings (if supported)
ollama run nomic-embed-text "test"
```

## Configuration

### Update `.env` file:

```env
# LLM Provider (ollama or openai)
LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# OpenAI (not needed if using Ollama)
# OPENAI_API_KEY=
```

## Model Comparison

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `llama3.1:8b` | 4.7GB | Fast | High | **Recommended** |
| `llama3.1:70b` | 40GB | Slow | Very High | Best quality |
| `mistral:7b` | 4.1GB | Fast | High | Technical docs |
| `nomic-embed-text` | 274MB | Fast | High | Embeddings |

## Usage

Once configured, the application will automatically use Ollama:

1. **Start Ollama:**
   ```bash
   ollama serve
   ```

2. **Start the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **The system will:**
   - Use `nomic-embed-text` for generating embeddings
   - Use `llama3.1:8b` for answering questions
   - Work completely offline and free!

## Troubleshooting

### "Connection refused" error
- Make sure Ollama is running: `ollama serve`
- Check the port: `curl http://localhost:11434/api/tags`

### Model not found
- Pull the model: `ollama pull llama3.1:8b`
- Verify: `ollama list`

### Slow performance
- Use smaller model: `llama3.1:8b` instead of `70b`
- Ensure you have enough RAM (8GB+ recommended)
- Close other applications

### Embedding errors
- Make sure `nomic-embed-text` is pulled: `ollama pull nomic-embed-text`
- Check Ollama logs for errors

## Switching Between Ollama and OpenAI

You can easily switch providers by changing `.env`:

**For Ollama:**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

**For OpenAI:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_LLM_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
```

## Benefits of Ollama

✅ **Free** - No API costs  
✅ **Private** - Data stays on your machine  
✅ **Fast** - No network latency  
✅ **Offline** - Works without internet  
✅ **Customizable** - Use any Ollama model  

## Next Steps

1. Install Ollama
2. Pull the models
3. Update `.env` file
4. Start Ollama: `ollama serve`
5. Run the application!
