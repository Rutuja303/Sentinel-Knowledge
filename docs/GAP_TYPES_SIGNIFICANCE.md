# Gap Types Significance in Sentinel Knowledge

## Overview

Our RAG (Retrieval Augmented Generation) system uses **4 gap detection rules** to identify different types of documentation problems. Each gap type serves a specific purpose in maintaining and improving your knowledge base.

---

## 1. 🔍 **low_similarity** - Weak Documentation Coverage

### How It Works
- **Detection Method**: Vector similarity search returns documents, but similarity scores are below the threshold (default: 0.3)
- **Technical Process**: 
  1. Query is converted to an embedding vector
  2. System searches for similar document embeddings
  3. If best match has similarity < 0.3, gap is detected

### Why It's Significant

**Identifies Partial Gaps:**
- Documentation exists but is **poorly discoverable** or uses different terminology
- Content may be there but not easily found through semantic search
- Indicates need for better keywords, synonyms, or clearer explanations

**Real-World Example:**
- User asks: "How do I configure the database connection?"
- System finds: Documentation about "DB setup" (similarity: 0.25)
- **Gap detected**: Content exists but terminology mismatch makes it hard to find

**Business Impact:**
- Users can't find existing documentation
- Support team gets repeated questions about documented topics
- Knowledge base appears incomplete even when content exists

**Action Items:**
- Add synonyms and alternative keywords to existing docs
- Improve document titles and headings
- Add examples that match common query patterns
- Enhance metadata and tags

---

## 2. 🔄 **repeated_query** - Frequently Asked Questions

### How It Works
- **Detection Method**: Tracks query history and detects when similar questions are asked 3+ times
- **Technical Process**:
  1. Each query is stored in query history
  2. System compares new queries with past queries
  3. If similar query appears 3+ times, gap is detected

### Why It's Significant

**Identifies User Pain Points:**
- Shows what questions users are **actually asking** repeatedly
- Reveals topics that confuse users or are poorly documented
- Highlights areas where users struggle despite existing documentation

**Real-World Example:**
- Multiple users ask: "How do I reset my password?" (asked 5 times)
- **Gap detected**: This is a common question that needs clear, easily accessible documentation

**Business Impact:**
- Reduces support ticket volume by creating FAQs
- Improves user experience by addressing common questions
- Identifies training needs and documentation priorities
- Shows which topics need the most attention

**Action Items:**
- Create dedicated FAQ section
- Add step-by-step guides for common tasks
- Improve discoverability of existing documentation
- Create quick reference guides

---

## 3. ❓ **uncertainty** - Unclear or Incomplete Documentation

### How It Works
- **Detection Method**: Analyzes LLM-generated answers for uncertainty phrases
- **Technical Process**:
  1. RAG system generates answer from retrieved documents
  2. System checks answer for phrases like "I'm not sure", "I don't have information", "unable to locate"
  3. If uncertainty phrases found, gap is detected

### Why It's Significant

**Identifies Quality Issues:**
- Documentation exists but is **vague, incomplete, or unclear**
- LLM cannot confidently answer despite having context
- Shows where information needs more detail or clarification

**Real-World Example:**
- User asks: "What are the system requirements?"
- System finds: Documentation that says "requires some memory and storage"
- LLM answers: "I'm not sure about the exact requirements..."
- **Gap detected**: Documentation exists but lacks specific details

**Business Impact:**
- Users get incomplete or unhelpful answers
- Reduces trust in the knowledge base
- Leads to follow-up questions and support tickets
- Indicates documentation quality issues

**Action Items:**
- Add specific details, numbers, and examples
- Clarify vague statements
- Complete partial documentation
- Add troubleshooting sections
- Include edge cases and exceptions

---

## 4. 🚫 **empty_retrieval** - Complete Documentation Gap

### How It Works
- **Detection Method**: Vector search returns zero documents for the query
- **Technical Process**:
  1. Query is converted to embedding
  2. System searches entire knowledge base
  3. If no documents found (empty results), gap is detected

### Why It's Significant

**Identifies Critical Missing Information:**
- Topic **doesn't exist** in the knowledge base at all
- Highest priority gap - users have no information available
- Shows critical areas requiring new documentation

**Real-World Example:**
- User asks: "How do I integrate with the new API v2?"
- System searches: No documents found
- **Gap detected**: Complete documentation gap - API v2 documentation doesn't exist

**Business Impact:**
- Users cannot find answers at all
- Highest support ticket volume
- Blocks user progress and adoption
- Critical for product success

**Action Items:**
- Create new documentation from scratch
- Prioritize based on gap frequency and severity
- Add comprehensive guides and tutorials
- Include examples and use cases

---

## How They Work Together

### Comprehensive Coverage
The 4 gap types work together to provide **complete coverage** of documentation problems:

1. **empty_retrieval** → Find what's completely missing
2. **low_similarity** → Find what exists but is hard to discover
3. **uncertainty** → Find what exists but is unclear
4. **repeated_query** → Find what users need most

### Priority Matrix

| Gap Type | Severity | Priority | Action Urgency |
|----------|----------|----------|----------------|
| empty_retrieval | High | Critical | Immediate - Create new docs |
| repeated_query | High | High | Urgent - Create FAQ/guides |
| low_similarity | Medium | Medium | Important - Enhance existing |
| uncertainty | Medium | Medium | Important - Clarify existing |

---

## Technical Implementation

### RAG Flow with Gap Detection

```
User Query
    ↓
[Vector Search] → Similarity Scores
    ↓
[Document Retrieval] → Retrieved Documents
    ↓
[LLM Generation] → Answer + Confidence
    ↓
[Gap Detection] → 4 Rules Applied
    ↓
Gap Type Identified → Stored in Database
```

### Detection Rules Priority

1. **empty_retrieval** checked first (most critical)
2. **low_similarity** checked if documents found
3. **uncertainty** checked in generated answer
4. **repeated_query** checked against query history

---

## Benefits for Your Project

### 1. **Proactive Documentation Management**
- Identify gaps before users complain
- Prioritize documentation work based on data
- Track documentation quality over time

### 2. **User-Centric Approach**
- Focus on what users actually ask
- Address real pain points, not assumptions
- Improve user experience systematically

### 3. **Efficient Resource Allocation**
- Know exactly what to document
- Prioritize high-impact gaps
- Measure documentation improvement

### 4. **Continuous Improvement**
- Track gap resolution over time
- Measure documentation coverage
- Identify recurring patterns

---

## Conclusion

Each gap type serves a unique purpose in identifying and resolving documentation problems. Together, they provide a comprehensive view of your knowledge base health and help you systematically improve documentation quality and coverage.
