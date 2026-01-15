# API Keys & Development Setup Guide

## 🔑 Required API Keys

### 1. **OpenAI API Key** (REQUIRED - Core Functionality)

**Why needed:**
- For generating embeddings (vector representations of text)
- For generating answers using GPT-3.5-turbo
- Core functionality - cannot run without this

**How to get:**
1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. **Important:** Save it immediately - you won't see it again!

**Cost:** Pay-as-you-go (very affordable for testing)
- Embeddings: ~$0.0001 per 1K tokens
- GPT-3.5-turbo: ~$0.002 per 1K tokens

**Free tier:** $5 credit for new accounts

---

### 2. **Confluence API Token** (OPTIONAL - Only if using Confluence)

**Why needed:**
- To fetch pages from your Confluence instance
- Only required if you want to ingest Confluence content

**How to get:**
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "Knowledge Gap Detector")
4. Copy the token
5. **Important:** Save it immediately - you won't see it again!

**Also need:**
- Your Confluence URL (e.g., `https://your-domain.atlassian.net`)
- Your Confluence username (your email)

**Cost:** Free (uses your existing Confluence account)

---

## 📋 Summary

| API Key | Required? | Purpose | Cost |
|---------|-----------|---------|------|
| **OpenAI API Key** | ✅ **YES** | Embeddings & LLM | Pay-as-you-go |
| **Confluence API Token** | ❌ Optional | Confluence integration | Free |

---

## 🚀 Quick Setup

1. **Get OpenAI API Key** (5 minutes)
   - Visit: https://platform.openai.com/api-keys
   - Create account if needed
   - Create API key
   - Copy to `.env` file

2. **Get Confluence Token** (Optional, 3 minutes)
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   - Create token
   - Copy to `.env` file

3. **Add to .env file:**
   ```env
   OPENAI_API_KEY=sk-your-key-here
   CONFLUENCE_URL=https://your-domain.atlassian.net
   CONFLUENCE_USERNAME=your-email@example.com
   CONFLUENCE_API_TOKEN=your-token-here
   ```

---

## 💰 Cost Estimation

For a typical hackathon demo:
- **Embeddings:** ~$0.10 - $0.50 (one-time ingestion)
- **Queries:** ~$0.01 - $0.05 per 100 queries
- **Total for demo:** Usually under $1

---

## 🔒 Security Notes

- **Never commit `.env` file** to git (it's in .gitignore)
- **Don't share API keys** publicly
- **Rotate keys** if exposed
- **Use environment variables** in production

---

## ❓ Troubleshooting

**"OPENAI_API_KEY is required"**
→ Add your OpenAI API key to `.env` file

**"Invalid API key"**
→ Check the key is correct (starts with `sk-`)
→ Make sure there are no extra spaces

**"Insufficient quota"**
→ Check your OpenAI account has credits
→ New accounts get $5 free credit

**Confluence errors**
→ Check URL format (should end with `.atlassian.net` or `.atlassian.com`)
→ Verify username is your email
→ Make sure API token is correct
