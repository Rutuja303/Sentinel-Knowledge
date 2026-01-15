# How to Start the Application

## ✅ Prerequisites Checklist

Before starting, make sure you have:

1. ✅ **Python 3.9+** installed
2. ✅ **OpenAI API Key** (REQUIRED)
   - Get from: https://platform.openai.com/api-keys
   - Add to `.env` file: `OPENAI_API_KEY=sk-your-key-here`
3. ✅ **Confluence API Token** (OPTIONAL - only if using Confluence)
   - Get from: https://id.atlassian.com/manage-profile/security/api-tokens
   - Add to `.env` file

## 🚀 Starting the Application

### Step 1: Setup (First Time Only)

```bash
cd /Users/consultadd/Desktop/Sentinel-knowledge/Sentinel-Knowledge

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### Step 2: Configure API Keys

Edit the `.env` file and add your OpenAI API key:

```bash
nano .env
# Or use your preferred editor

# Change this line:
OPENAI_API_KEY=your_openai_api_key_here
# To:
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Start the FastAPI Backend

**Terminal 1:**
```bash
cd /Users/consultadd/Desktop/Sentinel-knowledge/Sentinel-Knowledge
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
🚀 AI Knowledge Gap Detector API started
```

### Step 4: Start the Streamlit Dashboard

**Terminal 2:**
```bash
cd /Users/consultadd/Desktop/Sentinel-knowledge/Sentinel-Knowledge
source venv/bin/activate
streamlit run dashboard/app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

## 🧪 Testing the Application

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Ingest Example Document
```bash
curl -X POST http://localhost:8000/ingest
```

### Test 3: Query the Knowledge Base
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the deployment process?"}'
```

## 📝 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## ⚠️ Troubleshooting

### "OPENAI_API_KEY is required"
→ Make sure you've added your API key to `.env` file
→ Restart the server after adding the key

### "Module not found"
→ Make sure virtual environment is activated: `source venv/bin/activate`
→ Install dependencies: `pip install -r requirements.txt`

### "Port 8000 already in use"
→ Change the port: `uvicorn app.main:app --port 8001`
→ Or kill the process using port 8000

### "Cannot connect to API" (Dashboard)
→ Make sure the FastAPI server is running first
→ Check the API is accessible: `curl http://localhost:8000/health`

## 🎯 Quick Commands

```bash
# Start API
source venv/bin/activate && uvicorn app.main:app --reload

# Start Dashboard
source venv/bin/activate && streamlit run dashboard/app.py

# Check if running
curl http://localhost:8000/health

# View logs
tail -f /tmp/sentinel_api.log  # if using background mode
```

## 📚 Next Steps

1. **Add Documents**: Place files in `data/documents/` or use `/ingest/file` endpoint
2. **Ingest Confluence**: Use `/ingest/confluence` endpoint (if configured)
3. **Query**: Use the dashboard or `/query` endpoint
4. **View Gaps**: Check the dashboard's "Gap Analysis" tab
