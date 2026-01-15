# 🚀 Application is Running!

## ✅ Services Status

### FastAPI Backend
- **URL:** http://localhost:8000
- **Status:** ✅ Running
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Streamlit Dashboard
- **URL:** http://localhost:8501
- **Status:** ✅ Running
- **Auto-opens in browser**

---

## ⚠️ Important: Add Your API Key

The application is running, but you need to add your **OpenAI API Key** to make it fully functional.

### Quick Steps:

1. **Get your OpenAI API Key:**
   - Visit: https://platform.openai.com/api-keys
   - Create a new key if needed
   - Copy the key (starts with `sk-`)

2. **Add to .env file:**
   ```bash
   nano .env
   # Change this line:
   OPENAI_API_KEY=your_openai_api_key_here
   # To:
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. **Restart the servers:**
   - Stop the current servers (Ctrl+C in their terminals)
   - Restart using the commands below

---

## 🔧 Managing the Servers

### To Stop the Servers:

```bash
# Find and kill the processes
pkill -f "uvicorn app.main:app"
pkill -f "streamlit run dashboard/app.py"
```

### To Restart the Servers:

**Terminal 1 - FastAPI:**
```bash
cd /Users/consultadd/Desktop/Sentinel-knowledge/Sentinel-Knowledge
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Streamlit:**
```bash
cd /Users/consultadd/Desktop/Sentinel-knowledge/Sentinel-Knowledge
source venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

---

## 🧪 Test the Application

### 1. Check Health (should work even without API key):
```bash
curl http://localhost:8000/health
```

### 2. View API Documentation:
Open in browser: http://localhost:8000/docs

### 3. Test Query (requires API key):
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the deployment process?"}'
```

### 4. Access Dashboard:
Open in browser: http://localhost:8501

---

## 📊 Current Status

- ✅ **FastAPI Server:** Running on port 8000
- ✅ **Streamlit Dashboard:** Running on port 8501
- ⚠️ **OpenAI API Key:** Not configured (add to .env)
- ⚠️ **Confluence:** Not configured (optional)

---

## 🎯 Next Steps

1. **Add OpenAI API Key** to `.env` file
2. **Restart servers** after adding the key
3. **Ingest documents:**
   ```bash
   curl -X POST http://localhost:8000/ingest
   ```
4. **Start querying** via dashboard or API

---

## 💡 Tips

- The servers are running in the background
- Check logs if you encounter issues
- API docs at `/docs` show all available endpoints
- Dashboard provides a user-friendly interface

---

## 🆘 Troubleshooting

**Can't access the servers?**
- Check if ports 8000 and 8501 are available
- Verify the processes are running: `ps aux | grep uvicorn`

**API key errors?**
- Make sure `.env` file has the correct key
- Restart the servers after updating `.env`
- Check key format (should start with `sk-`)

**Dashboard not connecting?**
- Make sure FastAPI server is running first
- Check browser console for errors
- Verify API is accessible: `curl http://localhost:8000/health`
