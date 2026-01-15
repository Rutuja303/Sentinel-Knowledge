# Quick Start: Confluence Integration

## 5-Minute Setup

### 1. Get API Token (2 minutes)

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token

### 2. Add to .env (1 minute)

```bash
# Edit .env file
nano .env

# Add these lines:
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=paste_your_token_here
```

### 3. Restart API (1 minute)

```bash
# Stop the API (Ctrl+C) and restart
uvicorn app.main:app --reload
```

### 4. Test & Ingest (1 minute)

```bash
# List your Confluence spaces
curl http://localhost:8000/confluence/spaces

# Ingest from a space (replace YOUR_SPACE_KEY)
curl -X POST http://localhost:8000/ingest/confluence \
  -H "Content-Type: application/json" \
  -d '{"space_key": "YOUR_SPACE_KEY"}'
```

## Done! 🎉

Your Confluence pages are now in the knowledge base. Ask questions:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is our deployment process?"}'
```

## Finding Your Space Key

1. Go to your Confluence space
2. Look at the URL: `https://your-domain.atlassian.net/wiki/spaces/SPACE_KEY/...`
3. The `SPACE_KEY` is the part after `/spaces/`

Or use the API:
```bash
curl http://localhost:8000/confluence/spaces
```

## Troubleshooting

**"Confluence integration not configured"**
→ Check all 3 variables are in .env and restart API

**"401 Unauthorized"**
→ Check your API token and username are correct

**"No spaces found"**
→ Check your account has access to Confluence spaces
