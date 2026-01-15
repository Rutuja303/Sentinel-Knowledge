# 🔑 API Keys & Setup Summary

## Required API Keys

### 1. **OpenAI API Key** ⚠️ REQUIRED

**Status:** ❌ **MUST ADD TO .env FILE**

**How to Get:**
1. Visit: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**Add to .env:**
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

**Why Needed:**
- Generates embeddings (vector representations)
- Powers the AI responses (GPT-3.5-turbo)
- **Cannot run without this**

**Cost:** ~$0.10-1.00 for typical hackathon demo

---

### 2. **Confluence API Token** ✅ OPTIONAL

**Status:** Only needed if you want to ingest from Confluence

**How to Get:**
1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token

**Add to .env:**
```env
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-token-here
```

**Why Needed:**
- To fetch pages from Confluence
- Only if using Confluence integration

**Cost:** Free (uses your existing Confluence account)

---

## 📋 Current .env File Status

Your `.env` file has been created with placeholder values. You need to:

1. **Open `.env` file:**
   ```bash
   nano .env
   # or use your preferred editor
   ```

2. **Replace `your_openai_api_key_here` with your actual OpenAI API key**

3. **Optional:** Add Confluence credentials if using Confluence

---

## ✅ Application Status

✅ **Application code is ready**
✅ **Dependencies installed**
✅ **Server can start** (tested successfully)
❌ **Needs OpenAI API key** to function

---

## 🚀 Quick Start Commands

```bash
# 1. Add your OpenAI API key to .env
nano .env

# 2. Start the API server
cd /Users/consultadd/Desktop/Sentinel-knowledge/Sentinel-Knowledge
source venv/bin/activate
uvicorn app.main:app --reload

# 3. In another terminal, start the dashboard
source venv/bin/activate
streamlit run dashboard/app.py
```

---

## 📚 Documentation Files

- **API_KEYS_GUIDE.md** - Detailed guide for getting API keys
- **START_APPLICATION.md** - Step-by-step startup instructions
- **README.md** - Complete project documentation
- **CONFLUENCE_SETUP.md** - Confluence integration guide

---

## ⚠️ Important Notes

1. **Never commit `.env` file** to git (it's in .gitignore)
2. **Keep API keys secret** - don't share publicly
3. **OpenAI key is required** - app won't work without it
4. **Confluence is optional** - app works fine without it

---

## 🎯 What You Need Right Now

**Minimum to run:**
- ✅ OpenAI API key (get from https://platform.openai.com/api-keys)
- ✅ Add it to `.env` file
- ✅ Start the server

**For full functionality:**
- ✅ OpenAI API key
- ✅ Confluence credentials (optional)
- ✅ Some documents to ingest (or use Confluence)

---

## 💡 Test After Adding API Key

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","vector_store":{"total_documents":0,...}}
```

If you see an error about API key, double-check your `.env` file!
