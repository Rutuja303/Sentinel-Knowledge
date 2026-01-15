from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
from pathlib import Path
import warnings
import logging
import os

# Disable ChromaDB telemetry to avoid errors
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_DISABLED"] = "True"
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")

from app.models.schemas import QueryRequest, QueryResponse, KnowledgeGap
from app.services.ingestion import DocumentIngestionService
from app.services.confluence_ingestion import ConfluenceIngestionService
from app.services.embeddings import EmbeddingService
from app.services.rag import RAGService
from app.services.gap_detector import GapDetectorService
from app.services.question_generator import QuestionGeneratorService
from app.utils.config import config
from pydantic import BaseModel
from typing import Optional, List

# Initialize services (lazy initialization to handle missing API keys gracefully)
embedding_service = None
rag_service = None
question_generator = None
gap_detector = GapDetectorService()
ingestion_service = DocumentIngestionService()

# Initialize Confluence service (optional, only if configured)
confluence_service = None

def initialize_services():
    """Initialize services that require API keys"""
    global embedding_service, rag_service, question_generator, confluence_service
    
    try:
        if embedding_service is None:
            config.validate()  # This will raise if OPENAI_API_KEY is missing
            embedding_service = EmbeddingService()
            rag_service = RAGService(embedding_service)
            question_generator = QuestionGeneratorService(embedding_service)
    except ValueError as e:
        print(f"⚠️  {str(e)}")
        print("   Please add your OPENAI_API_KEY to the .env file")
        print("   Get your key from: https://platform.openai.com/api-keys")
    
    # Initialize Confluence service (optional)
    try:
        if config.CONFLUENCE_URL and config.CONFLUENCE_USERNAME and config.CONFLUENCE_API_TOKEN:
            if confluence_service is None:
                confluence_service = ConfluenceIngestionService()
    except Exception as e:
        print(f"⚠️  Confluence integration not available: {str(e)}")
        print("   Set CONFLUENCE_URL, CONFLUENCE_USERNAME, and CONFLUENCE_API_TOKEN in .env to enable")


class ConfluenceIngestRequest(BaseModel):
    space_key: Optional[str] = None
    limit: int = 1000

class AnalyzeConfluenceRequest(BaseModel):
    num_questions: int = 10

app = FastAPI(
    title="AI Knowledge Gap Detector",
    description="RAG-powered Q&A system with knowledge gap detection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    initialize_services()
    print("🚀 AI Knowledge Gap Detector API started")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Knowledge Gap Detector API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    if embedding_service is None:
        initialize_services()
    
    if embedding_service is None:
        return {
            "status": "unhealthy",
            "error": "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file",
            "vector_store": {"total_documents": 0}
        }
    
    stats = embedding_service.get_collection_stats()
    return {
        "status": "healthy",
        "vector_store": stats
    }


@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """Query the knowledge base and detect gaps"""
    if embedding_service is None or rag_service is None:
        initialize_services()
        if embedding_service is None or rag_service is None:
            raise HTTPException(
                status_code=503,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file. Get your key from: https://platform.openai.com/api-keys"
            )
    
    try:
        # Perform RAG query
        rag_result = rag_service.query(request.question)
        
        # Extract source information from context if available
        source_page_id = None
        source_page_title = None
        source_document = None
        
        if request.context:
            source_page_id = request.context.get("source_page_id")
            source_page_title = request.context.get("source_page_title")
            source_document = request.context.get("source_document")
        else:
            # Try to extract from retrieved documents metadata
            if rag_result.get("metadatas") and len(rag_result["metadatas"]) > 0:
                first_meta = rag_result["metadatas"][0]
                source_page_id = first_meta.get("page_id")
                source_page_title = first_meta.get("title")
                source_document = first_meta.get("filename")
        
        # Detect gaps with source information (pass metadatas for advanced detection)
        gap = gap_detector.detect_gap(
            query=request.question,
            answer=rag_result["answer"],
            similarity_scores=rag_result["similarity_scores"],
            retrieved_documents=rag_result["retrieved_documents"],
            user_id=request.user_id,
            source_page_id=source_page_id,
            source_page_title=source_page_title,
            source_document=source_document,
            metadatas=rag_result.get("metadatas", [])
        )
        
        # Build response
        response = QueryResponse(
            answer=rag_result["answer"],
            sources=rag_result["sources"],
            confidence_score=rag_result["confidence_score"],
            is_gap=gap is not None,
            gap_reason=gap.gap_type if gap else None,
            similarity_scores=rag_result["similarity_scores"]
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/ingest")
async def ingest_documents():
    """Ingest all documents from the documents directory"""
    if embedding_service is None:
        initialize_services()
        if embedding_service is None:
            raise HTTPException(
                status_code=503,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
            )
    
    try:
        results = ingestion_service.ingest_directory()
        
        # Add to vector store
        total_chunks = 0
        for result in results:
            chunks = result["chunks"]
            metadatas = [
                {
                    "filename": result["filename"],
                    "file_type": result["file_type"],
                    "chunk_index": i
                }
                for i in range(len(chunks))
            ]
            ids = [f"{result['filename']}_{i}" for i in range(len(chunks))]
            
            embedding_service.add_documents(chunks, metadatas, ids)
            total_chunks += len(chunks)
        
        return {
            "message": "Documents ingested successfully",
            "files_processed": len(results),
            "total_chunks": total_chunks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting documents: {str(e)}")


@app.post("/ingest/file")
async def ingest_single_file(file: UploadFile = File(...)):
    """Ingest a single uploaded file"""
    if embedding_service is None:
        initialize_services()
        if embedding_service is None:
            raise HTTPException(
                status_code=503,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
            )
    
    try:
        # Save uploaded file temporarily
        upload_path = Path(config.DOCUMENTS_PATH) / file.filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Ingest the file
        result = ingestion_service.ingest_file(upload_path)
        
        # Add to vector store
        chunks = result["chunks"]
        metadatas = [
            {
                "filename": result["filename"],
                "file_type": result["file_type"],
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]
        ids = [f"{result['filename']}_{i}" for i in range(len(chunks))]
        
        embedding_service.add_documents(chunks, metadatas, ids)
        
        return {
            "message": "File ingested successfully",
            "filename": result["filename"],
            "chunks": len(chunks)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting file: {str(e)}")


@app.get("/gaps", response_model=List[KnowledgeGap])
async def get_knowledge_gaps(severity: str = None, limit: int = 1000):
    """Get detected knowledge gaps from the entire collection"""
    try:
        if severity:
            gaps = gap_detector.get_gaps_by_severity(severity)
        else:
            # Get all gaps, not just top ones, to show entire collection
            gaps = gap_detector.get_all_gaps()
            # Sort by priority (severity * occurrence_count)
            gaps = sorted(
                gaps,
                key=lambda g: (3 if g.severity == "high" else 2 if g.severity == "medium" else 1) * g.occurrence_count,
                reverse=True
            )
            # Apply limit
            gaps = gaps[:limit]
        
        # Convert to dict for JSON serialization (Pydantic v2 uses model_dump)
        try:
            return [gap.model_dump() if hasattr(gap, 'model_dump') else gap.dict() for gap in gaps]
        except:
            # Fallback for older Pydantic versions
            return [gap.dict() for gap in gaps]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving gaps: {str(e)}")


@app.get("/gaps/stats")
async def get_gap_statistics():
    """Get statistics about knowledge gaps"""
    try:
        stats = gap_detector.get_query_statistics()
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")


@app.delete("/gaps/{gap_id}")
async def delete_gap(gap_id: str):
    """Delete a specific knowledge gap"""
    try:
        if gap_id in gap_detector.gaps:
            del gap_detector.gaps[gap_id]
            gap_detector.save_gaps()
            return {"message": f"Gap {gap_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Gap not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting gap: {str(e)}")


# Confluence Integration Endpoints

@app.get("/confluence/spaces")
async def get_confluence_spaces():
    """Get all accessible Confluence spaces"""
    if not confluence_service:
        raise HTTPException(
            status_code=503,
            detail="Confluence integration not configured. Set CONFLUENCE_URL, CONFLUENCE_USERNAME, and CONFLUENCE_API_TOKEN in .env"
        )
    
    try:
        spaces = confluence_service.get_all_spaces()
        return {"spaces": spaces, "count": len(spaces)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Confluence spaces: {str(e)}")


@app.get("/confluence/spaces/{space_key}/pages")
async def get_confluence_space_pages(space_key: str, limit: int = 100):
    """Get pages from a specific Confluence space"""
    if not confluence_service:
        raise HTTPException(
            status_code=503,
            detail="Confluence integration not configured"
        )
    
    try:
        pages = confluence_service.get_all_pages_from_space(space_key, limit)
        return {
            "space_key": space_key,
            "pages": [
                {
                    "id": p["id"],
                    "title": p["title"],
                    "url": p["url"],
                    "last_modified": p["last_modified"],
                    "author": p["author"]
                }
                for p in pages
            ],
            "count": len(pages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pages from space {space_key}: {str(e)}")


@app.post("/ingest/confluence")
async def ingest_confluence(request: ConfluenceIngestRequest = ConfluenceIngestRequest()):
    """Ingest pages from Confluence"""
    if not confluence_service:
        raise HTTPException(
            status_code=503,
            detail="Confluence integration not configured. Set CONFLUENCE_URL, CONFLUENCE_USERNAME, and CONFLUENCE_API_TOKEN in .env"
        )
    
    try:
        if request.space_key:
            # Ingest specific space
            ingested_pages = confluence_service.ingest_space(request.space_key, request.limit)
        else:
            # Ingest all spaces
            ingested_pages = confluence_service.ingest_all_spaces(request.limit)
        
        # Prepare chunks for embedding
        prepared_chunks = confluence_service.prepare_for_embedding(ingested_pages)
        
        # Add to vector store
        if embedding_service is None:
            initialize_services()
            if embedding_service is None:
                raise HTTPException(
                    status_code=503,
                    detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
                )
        
        total_chunks = 0
        for chunk_data in prepared_chunks:
            metadatas = [{
                "source": "confluence",
                "page_id": chunk_data["page_id"],
                "title": chunk_data["title"],
                "url": chunk_data["url"],
                "space": chunk_data["space"],
                "space_name": chunk_data["space_name"],
                "author": chunk_data["author"],
                "chunk_index": chunk_data["chunk_index"],
                **chunk_data["metadata"]
            }]
            ids = [f"confluence_{chunk_data['page_id']}_{chunk_data['chunk_index']}"]
            
            embedding_service.add_documents([chunk_data["chunk"]], metadatas, ids)
            total_chunks += 1
        
        # Get unique pages count
        unique_pages = len(set(p["page_id"] for p in ingested_pages))
        
        return {
            "message": "Confluence pages ingested successfully",
            "pages_processed": unique_pages,
            "total_chunks": total_chunks,
            "space_key": request.space_key or "all_spaces"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting Confluence pages: {str(e)}")


@app.get("/confluence/pages/{page_id}")
async def get_confluence_page(page_id: str):
    """Get a specific Confluence page by ID"""
    if not confluence_service:
        raise HTTPException(
            status_code=503,
            detail="Confluence integration not configured"
        )
    
    try:
        page = confluence_service.get_page_content(page_id)
        return page
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Confluence page: {str(e)}")


@app.post("/ingest/confluence/page/{page_id}")
async def ingest_single_confluence_page(page_id: str):
    """Ingest a single Confluence page by ID"""
    if not confluence_service:
        raise HTTPException(
            status_code=503,
            detail="Confluence integration not configured"
        )
    
    try:
        # Get page content
        page = confluence_service.get_page_content(page_id)
        
        # Prepare for embedding
        ingested_page = {
            "source": "confluence",
            "page_id": page["id"],
            "title": page["title"],
            "content": page["content"],
            "url": page["url"],
            "space": page["space"],
            "space_name": page["space_name"],
            "author": page["author"],
            "last_modified": page["last_modified"],
            "metadata": {
                "confluence_page_id": page["id"],
                "confluence_url": page["url"],
                "space_key": page["space"],
                "version": page["version"]
            }
        }
        
        # Prepare chunks for embedding
        prepared_chunks = confluence_service.prepare_for_embedding([ingested_page])
        
        # Add to vector store
        if embedding_service is None:
            initialize_services()
            if embedding_service is None:
                raise HTTPException(
                    status_code=503,
                    detail="Embedding service not configured. Please set OPENAI_API_KEY or configure Ollama in .env file"
                )
        
        total_chunks = 0
        for chunk_data in prepared_chunks:
            metadatas = [{
                "source": "confluence",
                "page_id": chunk_data["page_id"],
                "title": chunk_data["title"],
                "url": chunk_data["url"],
                "space": chunk_data["space"],
                "space_name": chunk_data["space_name"],
                "author": chunk_data["author"],
                "chunk_index": chunk_data["chunk_index"],
                **chunk_data["metadata"]
            }]
            ids = [f"confluence_{chunk_data['page_id']}_{chunk_data['chunk_index']}"]
            
            embedding_service.add_documents([chunk_data["chunk"]], metadatas, ids)
            total_chunks += 1
        
        return {
            "message": "Confluence page ingested successfully",
            "page_id": page_id,
            "title": page["title"],
            "total_chunks": total_chunks,
            "space": page["space"],
            "url": page["url"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting Confluence page: {str(e)}")


@app.post("/analyze/confluence/all")
async def analyze_all_confluence_data(request: AnalyzeConfluenceRequest = AnalyzeConfluenceRequest()):
    """Analyze all Confluence data - automatically fetches fresh data, ingests it, then analyzes"""
    if not confluence_service:
        raise HTTPException(
            status_code=503,
            detail="Confluence integration not configured. Set CONFLUENCE_URL, CONFLUENCE_USERNAME, and CONFLUENCE_API_TOKEN in .env"
        )
    
    if embedding_service is None or rag_service is None:
        initialize_services()
        if embedding_service is None or rag_service is None:
            raise HTTPException(
                status_code=503,
                detail="Embedding service not configured"
            )
    
    try:
        # Step 1: Delete existing Confluence documents to refresh
        print("🔄 Refreshing Confluence data...")
        deleted_count = embedding_service.delete_confluence_documents()
        print(f"   Deleted {deleted_count} old Confluence documents")
        
        # Step 2: Fetch fresh data from Confluence
        print("📥 Fetching fresh data from Confluence...")
        ingested_pages = confluence_service.ingest_all_spaces(limit_per_space=1000)
        
        if not ingested_pages:
            raise HTTPException(
                status_code=404,
                detail="No Confluence pages found. Please check your Confluence access and space permissions."
            )
        
        print(f"   Fetched {len(ingested_pages)} pages from Confluence")
        
        # Step 3: Prepare and ingest into vector store
        print("💾 Ingesting fresh data into vector store...")
        prepared_chunks = confluence_service.prepare_for_embedding(ingested_pages)
        
        total_chunks = 0
        for chunk_data in prepared_chunks:
            metadatas = [{
                "source": "confluence",
                "page_id": chunk_data["page_id"],
                "title": chunk_data["title"],
                "url": chunk_data["url"],
                "space": chunk_data["space"],
                "space_name": chunk_data["space_name"],
                "author": chunk_data["author"],
                "chunk_index": chunk_data["chunk_index"],
                **chunk_data["metadata"]
            }]
            ids = [f"confluence_{chunk_data['page_id']}_{chunk_data['chunk_index']}"]
            
            embedding_service.add_documents([chunk_data["chunk"]], metadatas, ids)
            total_chunks += 1
        
        print(f"   Ingested {total_chunks} chunks from {len(ingested_pages)} pages")
        
        # Step 4: Get the ingested documents for analysis
        confluence_docs = embedding_service.get_confluence_documents(limit=50000)
        
        if not confluence_docs.get("documents"):
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve ingested Confluence data for analysis."
            )
        
        # Get unique pages info from ALL files
        unique_pages = {}
        unique_files = set()
        for metadata in confluence_docs.get("metadatas", []):
            page_id = metadata.get("page_id")
            if page_id and page_id not in unique_pages:
                unique_pages[page_id] = {
                    "title": metadata.get("title", "Untitled"),
                    "url": metadata.get("url", ""),
                    "space": metadata.get("space", ""),
                    "space_name": metadata.get("space_name", "")
                }
            # Track unique files/pages - check multiple fields
            title = metadata.get("title") or metadata.get("page_title") or metadata.get("name")
            if title:
                unique_files.add(title)
            # Also check filename
            filename = metadata.get("filename") or metadata.get("file_name")
            if filename:
                unique_files.add(filename)
        
        print(f"📊 Analyzing {len(unique_pages)} unique Confluence pages from {len(unique_files)} unique files")
        print(f"📄 Total document chunks to analyze: {len(confluence_docs.get('documents', []))}")
        print(f"📋 Unique files/pages found: {', '.join(list(unique_files)[:10])}{'...' if len(unique_files) > 10 else ''}")
        
        # Generate questions based on all Confluence content (reduce default to speed up)
        from app.services.question_generator import QuestionGeneratorService
        question_gen = QuestionGeneratorService(embedding_service)
        
        # Get num_questions from request
        num_questions = request.num_questions
        # Limit questions to avoid timeout (max 15 for efficiency)
        actual_num_questions = min(num_questions, 15)
        analysis_questions = question_gen.generate_questions_for_confluence(actual_num_questions)
        
        # Analyze each question and detect gaps (with timeout protection)
        gaps_detected = []
        questions_processed = 0
        
        for i, question in enumerate(analysis_questions):
            try:
                print(f"🔍 Analyzing question {i+1}/{len(analysis_questions)}: {question[:60]}...")
                # Query the knowledge base (searches across ALL documents, not just one file)
                rag_result = rag_service.query(question)
                
                # Log which sources were found (should be from multiple files)
                if rag_result.get("metadatas"):
                    sources_found = set()
                    for meta in rag_result["metadatas"]:
                        # Check for Confluence sources
                        if meta.get("source") == "confluence":
                            title = meta.get("title")
                            if title:
                                sources_found.add(title)
                        # Check for file sources
                        filename = meta.get("filename")
                        if filename:
                            sources_found.add(filename)
                    if sources_found:
                        print(f"   📄 Found sources from {len(sources_found)} file(s): {', '.join(list(sources_found)[:5])}{'...' if len(sources_found) > 5 else ''}")
                    else:
                        print(f"   ⚠️  No source information found in retrieved documents")
                        # Debug: show what metadata we actually have
                        if rag_result["metadatas"]:
                            print(f"   🔍 Debug - Metadata keys: {list(rag_result['metadatas'][0].keys())}")
                            print(f"   🔍 Debug - First metadata: {rag_result['metadatas'][0]}")
                
                # Extract source page/document info from retrieved documents
                # Check all retrieved documents to find sources from multiple files
                source_page_id = None
                source_page_title = None
                source_document = None
                
                # Track all unique sources found
                all_sources = []
                
                if rag_result.get("metadatas") and len(rag_result["metadatas"]) > 0:
                    # Log first metadata to debug
                    if i == 0:
                        print(f"   🔍 Sample metadata keys: {list(rag_result['metadatas'][0].keys()) if rag_result['metadatas'] else 'None'}")
                    
                    # Check all metadata to find sources from different files
                    for meta in rag_result["metadatas"]:
                        # Try multiple ways to extract source information
                        title = None
                        filename = None
                        
                        # Method 1: Confluence source
                        if meta.get("source") == "confluence":
                            title = meta.get("title") or meta.get("page_title") or meta.get("name")
                            if title and title not in all_sources:
                                all_sources.append(title)
                            if not source_page_id:
                                source_page_id = meta.get("page_id") or meta.get("id")
                                source_page_title = title
                        
                        # Method 2: Regular file source
                        filename = meta.get("filename") or meta.get("file_name") or meta.get("document")
                        if filename and filename not in all_sources:
                            all_sources.append(filename)
                        if not source_document and filename:
                            source_document = filename
                        
                        # Method 3: Fallback - use title if available (might be from any source)
                        if not source_page_title and not source_document:
                            fallback_title = meta.get("title") or meta.get("name") or meta.get("document_title")
                            if fallback_title:
                                if meta.get("source") == "confluence":
                                    source_page_title = fallback_title
                                else:
                                    source_document = fallback_title
                                if fallback_title not in all_sources:
                                    all_sources.append(fallback_title)
                
                # If multiple sources found, log them
                if len(all_sources) > 1:
                    print(f"   ✅ Found sources from {len(all_sources)} different files: {', '.join(all_sources[:3])}{'...' if len(all_sources) > 3 else ''}")
                elif len(all_sources) == 1:
                    print(f"   ⚠️  Only found source from 1 file: {all_sources[0]}")
                else:
                    print(f"   ❌ No source information found in metadata")
                
                # Ensure we have at least one source
                if not source_page_title and not source_document:
                    # Try to extract from question or use a default
                    print(f"   ⚠️  Warning: No source found for question, using fallback")
                    # Don't set to None, let it be None so gap detector can handle it
                
                # Detect gaps (pass metadatas for advanced detection)
                gap = gap_detector.detect_gap(
                    query=question,
                    answer=rag_result["answer"],
                    similarity_scores=rag_result["similarity_scores"],
                    retrieved_documents=rag_result["retrieved_documents"],
                    source_page_id=source_page_id,
                    source_page_title=source_page_title,
                    source_document=source_document,
                    metadatas=rag_result.get("metadatas", [])
                )
                
                if gap:
                    # Ensure we have source information - use the best available
                    final_source_title = source_page_title or source_document
                    if not final_source_title and all_sources:
                        # Use first source found if we have any
                        final_source_title = all_sources[0]
                    
                    gaps_detected.append({
                        "query": question,
                        "gap_type": gap.gap_type,
                        "severity": gap.severity,
                        "confidence_score": rag_result["confidence_score"],
                        "source_page_title": source_page_title if source_page_title else (final_source_title if final_source_title else None),
                        "source_document": source_document if source_document else (final_source_title if not source_page_title and final_source_title else None)
                    })
                    
                    # Log gap detection with source
                    print(f"   ✅ Gap detected: {gap.gap_type} (severity: {gap.severity}) - Source: {final_source_title or 'Unknown'}")
                
                questions_processed += 1
                
            except Exception as e:
                # Continue processing other questions even if one fails
                print(f"Error processing question {i+1}: {str(e)}")
                continue
        
        print(f"✅ Analysis complete: {questions_processed} questions analyzed, {len(gaps_detected)} gaps detected")
        print(f"📊 Analyzed {len(unique_pages)} unique pages from {len(unique_files)} unique files")
        
        return {
            "message": "Confluence data analysis completed",
            "total_confluence_pages": len(unique_pages),
            "total_confluence_files": len(unique_files),
            "total_confluence_chunks": len(confluence_docs.get("documents", [])),
            "questions_analyzed": questions_processed,
            "gaps_detected": len(gaps_detected),
            "analysis_questions": analysis_questions[:questions_processed],
            "gaps": gaps_detected
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing Confluence data: {str(e)}")




@app.get("/suggested-questions", response_model=List[str])
async def get_suggested_questions(num_questions: int = 15):
    """Get suggested questions based on knowledge base content"""
    if embedding_service is None or question_generator is None:
        initialize_services()
        if embedding_service is None or question_generator is None:
            # Return fallback questions if API key not configured
            fallback_questions = [
                "How do we handle deployment rollbacks?",
                "What is our incident response procedure?",
                "How do we troubleshoot service failures?",
                "What are the steps for database migrations?",
                "How do we handle payment gateway failures?",
                "What is the process for code reviews?",
                "How do we manage API rate limits?",
                "What happens during a security breach?",
                "How do we scale our infrastructure?",
                "What is our disaster recovery plan?"
            ]
            return fallback_questions[:num_questions]
    
    try:
        questions = question_generator.generate_questions(num_questions=num_questions)
        return questions
    except Exception as e:
        # Return fallback on error
        fallback_questions = [
            "How do we handle deployment rollbacks?",
            "What is our incident response procedure?",
            "How do we troubleshoot service failures?",
            "What are the steps for database migrations?",
            "How do we handle payment gateway failures?"
        ]
        return fallback_questions[:num_questions]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
