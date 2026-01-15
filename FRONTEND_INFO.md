# 🎨 Frontend Information

## Frontend Location

The frontend is a **Streamlit Dashboard** running at:

### 🌐 **http://localhost:8501**

---

## Frontend Details

- **Technology:** Streamlit (Python web framework)
- **Location:** `dashboard/app.py`
- **Port:** 8501
- **URL:** http://localhost:8501

---

## How to Access

### Option 1: Browser
Simply open your browser and go to:
```
http://localhost:8501
```

### Option 2: Auto-open
Streamlit usually opens automatically in your default browser when started.

### Option 3: Command Line
```bash
open http://localhost:8501  # macOS
# or
xdg-open http://localhost:8501  # Linux
```

---

## Frontend Features

The dashboard has **3 main views**:

1. **Dashboard Tab**
   - Overview of knowledge gaps
   - Statistics and metrics
   - Top gaps visualization
   - Charts and graphs

2. **Query Interface Tab**
   - Interactive Q&A interface
   - Ask questions about your knowledge base
   - Real-time gap detection
   - Confidence scores

3. **Gap Analysis Tab**
   - Detailed gap breakdown
   - Filterable gap list
   - Charts by type and severity
   - Export capabilities

---

## Starting the Frontend

If the frontend is not running, start it with:

```bash
cd /Users/consultadd/Desktop/Sentinel-knowledge/Sentinel-Knowledge
source venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

---

## Frontend Configuration

The frontend connects to the backend API at:
- **Backend URL:** http://localhost:8000
- **Configured in:** `dashboard/app.py` (line 10: `API_BASE_URL`)

---

## Troubleshooting

### Frontend not loading?
1. Check if Streamlit is running:
   ```bash
   ps aux | grep streamlit
   ```

2. Check if port 8501 is available:
   ```bash
   lsof -i :8501
   ```

3. Restart the frontend:
   ```bash
   pkill -f streamlit
   streamlit run dashboard/app.py --server.port 8501
   ```

### Can't connect to backend?
- Make sure the FastAPI server is running on port 8000
- Check: `curl http://localhost:8000/health`

### Dashboard shows errors?
- Check browser console (F12)
- Verify backend is accessible
- Check Streamlit logs

---

## Architecture

```
┌─────────────────┐
│  Streamlit      │  Port 8501
│  Dashboard      │  (Frontend)
│  (Frontend)     │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│  FastAPI        │  Port 8000
│  Backend        │  (Backend)
│  (API)          │
└─────────────────┘
```

---

## Quick Links

- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
