import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from app.utils.config import config


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
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[str], metadatas: List[Dict], ids: List[str]):
        """Add document chunks to the vector store"""
        # Generate embeddings
        embeddings_list = self.embeddings.embed_documents(chunks)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings_list,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
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
            print(f"Error getting documents: {e}")
            return {"documents": [], "metadatas": [], "ids": []}
    
    def delete_collection(self):
        """Delete the collection (for reset/testing)"""
        self.client.delete_collection(name="knowledge_base")
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
