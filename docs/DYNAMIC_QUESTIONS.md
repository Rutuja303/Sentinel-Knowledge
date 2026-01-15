# 🤖 Dynamic Question Generation

## Overview

The suggested questions in the Query Interface are now **dynamically generated** based on your actual knowledge base content (from Confluence or local documents), not hardcoded!

## How It Works

### 1. Content Analysis
- **Extracts topics** from document titles and metadata
- **Samples content** from your knowledge base
- **Identifies key themes** from Confluence pages and documents

### 2. AI-Powered Generation
- Uses GPT to generate relevant questions based on:
  - Document titles/topics
  - Content samples
  - Knowledge base themes
- Creates diverse, practical questions users would actually ask

### 3. Smart Caching
- Questions are cached for 5 minutes
- Regenerates when new content is ingested
- Falls back to generic questions if no content is available

## API Endpoint

### GET `/suggested-questions`

**Parameters:**
- `num_questions` (optional, default: 15) - Number of questions to generate

**Response:**
```json
[
  "How do we handle deployment rollbacks?",
  "What is our incident response procedure?",
  "How do we troubleshoot service failures?",
  ...
]
```

**Example:**
```bash
curl http://localhost:8000/suggested-questions?num_questions=10
```

## Features

### ✅ Content-Based
- Questions are generated from **your actual documentation**
- Relevant to your specific knowledge base
- Covers topics that actually exist in your docs

### ✅ Intelligent Generation
- Uses AI to create natural, user-friendly questions
- Covers different question types:
  - How-to questions
  - What-is questions
  - Troubleshooting questions
  - Procedure questions

### ✅ Fallback Support
- If no content is available, shows generic questions
- If API key is missing, shows fallback questions
- Always provides useful suggestions

## Usage in Dashboard

The dashboard automatically:
1. Fetches suggested questions when you open Query Interface
2. Shows a loading spinner while generating
3. Displays questions in a 3-column grid
4. Updates when new content is ingested

## How to Get Better Questions

1. **Ingest More Content**
   - Add documents to `data/documents/`
   - Ingest from Confluence spaces
   - More content = better questions

2. **Use Descriptive Titles**
   - Document titles are used to generate questions
   - Clear, descriptive titles help generate better questions

3. **Ingest Diverse Content**
   - Mix of procedures, guides, FAQs
   - Different topics and domains
   - More variety = more diverse questions

## Technical Details

### QuestionGeneratorService

Located in: `app/services/question_generator.py`

**Key Methods:**
- `get_document_topics()` - Extracts topics from metadata
- `get_sample_content()` - Gets content samples
- `generate_questions()` - Uses LLM to generate questions
- `_get_fallback_questions()` - Fallback when content unavailable

### Integration

- **Backend:** `/suggested-questions` endpoint in `app/main.py`
- **Frontend:** `fetch_suggested_questions()` in `dashboard/app.py`
- **Caching:** 5-minute cache to reduce API calls

## Example Flow

1. User ingests Confluence pages about "Deployment Procedures"
2. System extracts topics: "Deployment", "Rollback", "CI/CD"
3. AI generates questions like:
   - "How do we handle deployment rollbacks?"
   - "What is our CI/CD process?"
   - "How do we deploy to production?"
4. Questions appear in Query Interface
5. User clicks a question → auto-fills → clicks Query → gets answer!

## Benefits

✅ **Relevant** - Questions match your actual content  
✅ **Dynamic** - Updates as you add more content  
✅ **Intelligent** - AI generates natural questions  
✅ **User-Friendly** - One-click to use suggested questions  
✅ **Efficient** - Cached to reduce API calls  

## Next Steps

After you provide API keys and ingest content:
1. Questions will automatically be generated
2. They'll be based on your Confluence pages and documents
3. They'll update as you add more content
4. Users can click to use them instantly!
