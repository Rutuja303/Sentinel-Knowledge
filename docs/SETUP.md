# Detailed Setup Guide

## Step-by-Step Setup Instructions

### 1. Prerequisites Check

```bash
# Check Python version (needs 3.9+)
python3 --version

# If not installed, install Python 3.9+ from python.org
```

### 2. Clone and Navigate

```bash
cd /Users/consultadd/Desktop/Sentinel-knowledge/Sentinel-Knowledge
```

### 3. Run Setup Script

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Set up .env file template

### 4. Configure Environment

```bash
# Edit .env file
nano .env  # or use vim, code, etc.

# Add your OpenAI API key:
OPENAI_API_KEY=sk-your-actual-key-here
```

**Get OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy and paste into .env

### 5. Add Documents

Place your documents in `data/documents/`:
- PDF files (.pdf)
- Word documents (.docx)
- Text files (.txt)
- Markdown files (.md, .markdown)

Example:
```bash
cp ~/Documents/my-sop.pdf data/documents/
cp ~/Documents/runbook.docx data/documents/
```

### 6. Start the Backend

**Terminal 1:**
```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 7. Start the Dashboard

**Terminal 2:**
```bash
# Activate virtual environment
source venv/bin/activate

# Start Streamlit
streamlit run dashboard/app.py
```

Dashboard will open automatically in your browser at http://localhost:8501

### 8. Ingest Documents

**Option A: Via API (using curl)**
```bash
curl -X POST http://localhost:8000/ingest
```

**Option B: Via Dashboard**
- Go to the Query Interface
- Use the API endpoints shown in the sidebar

**Option C: Via Python**
```python
import requests
response = requests.post("http://localhost:8000/ingest")
print(response.json())
```

### 9. Test the System

**Test 1: Ask a question about your documents**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the deployment process?"}'
```

**Test 2: Ask about something NOT in your docs**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do we handle alien invasions?"}'
```

This should trigger a gap detection!

**Test 3: Check gaps**
```bash
curl http://localhost:8000/gaps
```

### 10. View Dashboard

Open http://localhost:8501 and explore:
- Dashboard: See overview and top gaps
- Query Interface: Ask questions interactively
- Gap Analysis: Detailed gap breakdown

## Troubleshooting

### Issue: "OPENAI_API_KEY is required"
**Solution:** Make sure you've added your API key to `.env` file

### Issue: "Cannot connect to API"
**Solution:** Make sure the FastAPI server is running on port 8000

### Issue: "No module named 'langchain'"
**Solution:** 
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Documents not being ingested
**Solution:** 
- Check file format is supported (PDF, DOCX, TXT, MD)
- Check file is in `data/documents/` directory
- Check API logs for errors

### Issue: No gaps detected
**Solution:**
- Make sure you're asking questions NOT in your documents
- Lower `MIN_SIMILARITY_SCORE` in `.env` (try 0.2)
- Ask the same question multiple times to trigger repeated query detection

## Next Steps

1. Add more documents to your knowledge base
2. Ask various questions to populate gap data
3. Review the dashboard to identify documentation needs
4. Use gap insights to prioritize documentation work

## Production Deployment

For production:
1. Set `ENVIRONMENT=production` in `.env`
2. Use a production WSGI server (e.g., Gunicorn)
3. Set up proper authentication
4. Use a production database instead of JSON files
5. Set up monitoring and logging
