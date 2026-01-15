# Confluence Integration Setup Guide

## Overview

The AI Knowledge Gap Detector can directly ingest content from your Confluence instance, making it easy to analyze your existing documentation and identify knowledge gaps.

## Prerequisites

- A Confluence account (Cloud or Server/Data Center)
- Admin or appropriate permissions to access the spaces you want to ingest
- An API token for authentication

## Step 1: Get Your Confluence API Token

1. **Go to Atlassian Account Settings:**
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   - Log in with your Confluence account

2. **Create API Token:**
   - Click "Create API token"
   - Give it a label (e.g., "Knowledge Gap Detector")
   - Click "Create"
   - **Copy the token immediately** (you won't see it again!)

## Step 2: Find Your Confluence URL

Your Confluence URL format depends on your instance:

- **Cloud:** `https://your-domain.atlassian.net` or `https://your-domain.atlassian.com`
- **Server/Data Center:** `https://confluence.your-domain.com`

## Step 3: Configure the Application

Add these variables to your `.env` file:

```env
# Confluence Configuration
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your_api_token_here

# Optional: Specific space to ingest (leave empty to ingest all)
CONFLUENCE_SPACE_KEY=YOUR_SPACE_KEY
```

## Step 4: Verify Connection

Start the API server and test the connection:

```bash
# Start the API
uvicorn app.main:app --reload

# Test connection (in another terminal)
curl http://localhost:8000/confluence/spaces
```

If successful, you'll see a list of accessible Confluence spaces.

## Step 5: Ingest Confluence Content

### Option A: Ingest from a Specific Space

```bash
# First, get list of spaces to find the space key
curl http://localhost:8000/confluence/spaces

# Ingest from a specific space
curl -X POST http://localhost:8000/ingest/confluence \
  -H "Content-Type: application/json" \
  -d '{
    "space_key": "YOUR_SPACE_KEY",
    "limit": 1000
  }'
```

### Option B: Ingest from All Spaces

```bash
curl -X POST http://localhost:8000/ingest/confluence \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 1000
  }'
```

### Option C: Using Python

```python
import requests

# List spaces
spaces = requests.get("http://localhost:8000/confluence/spaces").json()
print(f"Found {spaces['count']} spaces")

# Ingest from a space
response = requests.post(
    "http://localhost:8000/ingest/confluence",
    json={"space_key": "YOUR_SPACE_KEY", "limit": 1000}
)
print(response.json())
```

## Step 6: Query Your Confluence Content

Once ingested, you can query the knowledge base:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is our deployment process?"}'
```

The system will search through your Confluence pages and local documents to answer questions.

## API Endpoints Reference

### Get All Spaces
```bash
GET /confluence/spaces
```
Returns list of all accessible Confluence spaces.

### Get Pages from a Space
```bash
GET /confluence/spaces/{space_key}/pages?limit=100
```
Returns pages from a specific space.

### Get Specific Page
```bash
GET /confluence/pages/{page_id}
```
Returns content of a specific Confluence page.

### Ingest Confluence
```bash
POST /ingest/confluence
Body: {
  "space_key": "OPTIONAL_SPACE_KEY",  # Omit to ingest all spaces
  "limit": 1000  # Max pages per space
}
```

## Troubleshooting

### Error: "Confluence integration not configured"
**Solution:** Make sure all three Confluence variables are set in `.env`:
- `CONFLUENCE_URL`
- `CONFLUENCE_USERNAME`
- `CONFLUENCE_API_TOKEN`

### Error: "401 Unauthorized"
**Solution:** 
- Check that your API token is correct
- Verify your username (email) is correct
- Make sure the token hasn't expired

### Error: "403 Forbidden"
**Solution:**
- You don't have permission to access the requested space
- Check your Confluence permissions
- Try a different space key

### Error: "Connection timeout"
**Solution:**
- Check your Confluence URL is correct
- Verify network connectivity
- For Server/DC, ensure the instance is accessible

### No pages found
**Solution:**
- Verify the space key is correct
- Check that the space has pages
- Try listing spaces first: `GET /confluence/spaces`

## Best Practices

1. **Start Small:** Ingest one space first to test
2. **Set Limits:** Use the `limit` parameter to control ingestion size
3. **Regular Updates:** Re-ingest periodically to get latest content
4. **Space Selection:** Only ingest relevant spaces to avoid noise
5. **Monitor Usage:** Large ingestions may take time and use API quota

## Security Notes

- **Never commit `.env` file** to version control
- **Rotate API tokens** regularly
- **Use least privilege:** Create a dedicated Confluence user with minimal permissions if possible
- **Monitor API usage:** Confluence API has rate limits

## Advanced: Scheduled Ingestion

You can set up a cron job or scheduled task to regularly ingest Confluence:

```bash
# Example cron job (runs daily at 2 AM)
0 2 * * * cd /path/to/Sentinel-Knowledge && source venv/bin/activate && curl -X POST http://localhost:8000/ingest/confluence -H "Content-Type: application/json" -d '{"limit": 1000}'
```

Or use a Python script:

```python
import requests
import schedule
import time

def ingest_confluence():
    response = requests.post(
        "http://localhost:8000/ingest/confluence",
        json={"limit": 1000}
    )
    print(f"Ingestion completed: {response.json()}")

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(ingest_confluence)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Support

For issues or questions:
1. Check the main README.md
2. Review API documentation at `http://localhost:8000/docs`
3. Check application logs for detailed error messages
