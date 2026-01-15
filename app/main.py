from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
from pathlib import Path

from app.models.schemas import QueryRequest, QueryResponse, KnowledgeGap
from app.services.ingestion import DocumentIngestionService
from app.services.confluence_ingestion import ConfluenceIngestionService
from app.services.embeddings import EmbeddingService
from app.services.rag import RAGService
from app.services.gap_detector import GapDetectorService
from app.utils.config import config
from pydantic import BaseModel
from typing import Optional

# Initialize services (lazy initialization to handle missing API keys gracefully)
embedding_service = None
rag_service = None
gap_detector = GapDetectorService()
ingestion_service = DocumentIngestionService()

# Initialize Confluence service (optional, only if configured)
confluence_service = None

def initialize_services():
    """Initialize services that require API keys"""
    global embedding_service, rag_service, confluence_service
    
    try:
        if embedding_service is None:
            config.validate()  # This will raise if OPENAI_API_KEY is missing
            embedding_service = EmbeddingService()
            rag_service = RAGService(embedding_service)
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
        
        # Detect gaps
        gap = gap_detector.detect_gap(
            query=request.question,
            answer=rag_result["answer"],
            similarity_scores=rag_result["similarity_scores"],
            retrieved_documents=rag_result["retrieved_documents"],
            user_id=request.user_id
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
async def get_knowledge_gaps(severity: str = None, limit: int = 20):
    """Get detected knowledge gaps"""
    try:
        if severity:
            gaps = gap_detector.get_gaps_by_severity(severity)
        else:
            gaps = gap_detector.get_top_gaps(limit)
        
        return gaps
    
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
