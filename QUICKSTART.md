# 🚀 Quick Start Guide (5 Minutes)

## Prerequisites
- Python 3.9+ installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Setup (2 minutes)

```bash
# 1. Run setup script
./setup.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Add your OpenAI API key to .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

## Run (2 minutes)

**Terminal 1 - Start API:**
```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Start Dashboard:**
```bash
source venv/bin/activate
streamlit run dashboard/app.py
```

## Test (1 minute)

1. **Add a test document:**
   ```bash
   echo "Our deployment process involves three steps: build, test, and deploy." > data/documents/deployment.txt
   ```

2. **Ingest it:**
   ```bash
   curl -X POST http://localhost:8000/ingest
   ```

3. **Ask a question (should work):**
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the deployment process?"}'
   ```

4. **Ask about something NOT in docs (should detect gap):**
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "How do we handle database migrations?"}'
   ```

5. **View gaps in dashboard:**
   - Open http://localhost:8501
   - Go to "Dashboard" tab
   - See the detected gap!

## What You Need

### For Hackathon Demo:

1. **Sample Documents** (add to `data/documents/`):
   - A few SOPs or runbooks
   - Some project documentation
   - FAQs or guides

2. **Demo Flow:**
   - Show answering a well-documented question ✅
   - Show detecting a gap for missing topic ⚠️
   - Show dashboard with top gaps 📊
   - Explain the business value 💼

### Key Talking Points:

- **Problem**: Companies don't know what they don't know
- **Solution**: AI that learns from what it CAN'T answer
- **Impact**: Prevents incidents, reduces bus factor, improves onboarding
- **Differentiator**: Not just RAG - it detects gaps in real-time

## Common Commands

```bash
# Check API health
curl http://localhost:8000/health

# Get all gaps
curl http://localhost:8000/gaps

# Get gap statistics
curl http://localhost:8000/gaps/stats

# Upload a file
curl -X POST -F "file=@document.pdf" http://localhost:8000/ingest/file
```

## Troubleshooting

**API not starting?**
- Check if port 8000 is available
- Make sure .env has OPENAI_API_KEY

**Dashboard not connecting?**
- Make sure API is running first
- Check http://localhost:8000/health

**No gaps detected?**
- Ask questions about topics NOT in your documents
- Lower MIN_SIMILARITY_SCORE in .env to 0.2
- Ask the same question 3+ times
