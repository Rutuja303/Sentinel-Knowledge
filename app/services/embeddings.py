import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from app.utils.config import config
import warnings
import logging
import os

# Completely disable ChromaDB telemetry to avoid errors
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_DISABLED"] = "True"

# Suppress ChromaDB telemetry warnings and errors
logging.getLogger("chromadb.telemetry").setLevel(logging.CRITICAL)
logging.getLogger("chromadb").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")
warnings.filterwarnings("ignore", message=".*telemetry.*")
warnings.filterwarnings("ignore", message=".*capture.*")

# Monkey patch to disable telemetry capture if it exists
try:
    import chromadb.telemetry.events as telemetry_events
    if hasattr(telemetry_events, 'capture'):
        def noop_capture(*args, **kwargs):
            pass
        telemetry_events.capture = noop_capture
except:
    pass


class EmbeddingService:
    """Service for managing vector embeddings and ChromaDB"""
    
    def __init__(self):
        config.validate()
        import os
        
        # Initialize embeddings based on provider
        if config.LLM_PROVIDER == "ollama":
            from langchain_ollama import OllamaEmbeddings
            self.embeddings = OllamaEmbeddings(
                model=config.OLLAMA_EMBEDDING_MODEL,
                base_url=config.OLLAMA_BASE_URL
            )
        else:  # OpenAI
            from langchain_openai import OpenAIEmbeddings
            os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
            self.embeddings = OpenAIEmbeddings(
                model=config.OPENAI_EMBEDDING_MODEL
            )
        
        # Initialize ChromaDB with telemetry disabled
        # Disable telemetry to avoid errors
        import os
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        os.environ["CHROMA_TELEMETRY_DISABLED"] = "True"
        
        try:
            self.client = chromadb.PersistentClient(
                path=config.CHROMA_DB_PATH,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        except Exception as e:
            # Fallback: try without settings
            print(f"Warning: ChromaDB initialization with settings failed: {e}")
            self.client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[str], metadatas: List[Dict], ids: List[str]):
        """Add document chunks to the vector store"""
        # Generate embeddings
        embeddings_list = self.embeddings.embed_documents(chunks)
        
        # Add to ChromaDB (suppress telemetry errors)
        try:
            self.collection.add(
                embeddings=embeddings_list,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            # Suppress telemetry-related errors
            if "telemetry" in str(e).lower() or "capture()" in str(e):
                # Retry without telemetry
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.collection.add(
                        embeddings=embeddings_list,
                        documents=chunks,
                        metadatas=metadatas,
                        ids=ids
                    )
            else:
                raise
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """Search for similar documents across ALL documents in the collection (all files)"""
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in ChromaDB across ALL documents (not limited to one file)
        # The collection contains all ingested documents from all sources
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results  # Get top n_results from entire collection
            )
        except Exception as e:
            # Suppress telemetry-related errors
            if "telemetry" in str(e).lower() or "capture()" in str(e):
                # Retry without telemetry
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results
                    )
            else:
                raise
        
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "ids": results["ids"][0] if results["ids"] else [],
            "distances": results["distances"][0] if results["distances"] else []
        }
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name
        }
    
    def get_all_documents(self, limit: int = 100) -> Dict:
        """Get all documents from the collection with metadata"""
        try:
            results = self.collection.get(limit=limit)
            return {
                "documents": results.get("documents", []),
                "metadatas": results.get("metadatas", []),
                "ids": results.get("ids", [])
            }
        except Exception as e:
            # Suppress telemetry errors
            if "telemetry" in str(e).lower() or "capture()" in str(e):
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    results = self.collection.get(limit=limit)
                    return {
                        "documents": results.get("documents", []),
                        "metadatas": results.get("metadatas", []),
                        "ids": results.get("ids", [])
                    }
            print(f"Error getting documents: {e}")
            return {"documents": [], "metadatas": [], "ids": []}
    
    def get_confluence_documents(self, limit: int = 50000) -> Dict:
        """Get ALL documents from Confluence source (not just one file)"""
        try:
            # Get total count first
            total_count = self.collection.count()
            print(f"📊 Total documents in collection: {total_count}")
            
            # Get all documents (suppress telemetry errors)
            # Use a large limit to get all documents
            actual_limit = min(limit, total_count) if total_count > 0 else limit
            try:
                all_results = self.collection.get(limit=actual_limit)
            except Exception as e:
                # Suppress telemetry errors
                if "telemetry" in str(e).lower() or "capture()" in str(e):
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        all_results = self.collection.get(limit=actual_limit)
                else:
                    raise
            
            # Filter for Confluence documents from ALL files
            confluence_docs = []
            confluence_metadatas = []
            confluence_ids = []
            
            for i, metadata in enumerate(all_results.get("metadatas", [])):
                if metadata.get("source") == "confluence":
                    confluence_docs.append(all_results.get("documents", [])[i])
                    confluence_metadatas.append(metadata)
                    confluence_ids.append(all_results.get("ids", [])[i])
            
            print(f"📄 Found {len(confluence_docs)} Confluence document chunks from all pages")
            
            return {
                "documents": confluence_docs,
                "metadatas": confluence_metadatas,
                "ids": confluence_ids
            }
        except Exception as e:
            print(f"Error getting Confluence documents: {e}")
            return {"documents": [], "metadatas": [], "ids": []}
    
    def delete_collection(self):
        """Delete the collection (for reset/testing)"""
        self.client.delete_collection(name="knowledge_base")
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
