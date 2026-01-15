import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import pickle
import os
from app.utils.config import config


class InMemoryEmbeddingService:
    """
    In-Memory Embedding Service
    
    Stores embeddings and text chunks in memory (RAM) for fast access.
    Optionally saves to disk for persistence.
    """
    
    def __init__(self, persist_to_disk: bool = True, persist_path: str = "./data/embeddings_cache"):
        config.validate()
        import os as os_module
        
        # Initialize embeddings based on provider
        if config.LLM_PROVIDER == "ollama":
            from langchain_ollama import OllamaEmbeddings
            self.embeddings = OllamaEmbeddings(
                model=config.OLLAMA_EMBEDDING_MODEL,
                base_url=config.OLLAMA_BASE_URL
            )
            self.embedding_dim = 768  # nomic-embed-text dimension
        else:  # OpenAI
            from langchain_openai import OpenAIEmbeddings
            os_module.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
            self.embeddings = OpenAIEmbeddings(
                model=config.OPENAI_EMBEDDING_MODEL
            )
            self.embedding_dim = 1536  # text-embedding-ada-002 dimension
        
        # In-memory storage
        self.embeddings_dict: Dict[str, np.ndarray] = {}  # {id: embedding_vector}
        self.texts_dict: Dict[str, str] = {}  # {id: text_chunk}
        self.metadata_dict: Dict[str, Dict] = {}  # {id: metadata}
        self.ids_list: List[str] = []  # Maintain order
        
        # Persistence settings
        self.persist_to_disk = persist_to_disk
        self.persist_path = Path(persist_path)
        if self.persist_to_disk:
            self.persist_path.mkdir(parents=True, exist_ok=True)
            # Try to load existing embeddings
            self._load_from_disk()
    
    def _load_from_disk(self):
        """Load embeddings from disk if they exist"""
        embeddings_file = self.persist_path / "embeddings.npy"
        data_file = self.persist_path / "data.pkl"
        
        if embeddings_file.exists() and data_file.exists():
            try:
                # Load embeddings (stored as numpy array with IDs as index)
                embeddings_data = np.load(embeddings_file, allow_pickle=True).item()
                self.embeddings_dict = embeddings_data
                
                # Load texts and metadata
                with open(data_file, "rb") as f:
                    data = pickle.load(f)
                    self.texts_dict = data.get("texts", {})
                    self.metadata_dict = data.get("metadata", {})
                    self.ids_list = data.get("ids", [])
                
                print(f"✅ Loaded {len(self.ids_list)} embeddings from disk")
            except Exception as e:
                print(f"⚠️  Error loading embeddings from disk: {e}")
                print("   Starting with empty embeddings")
    
    def _save_to_disk(self):
        """Save embeddings to disk for persistence"""
        if not self.persist_to_disk:
            return
        
        try:
            # Save embeddings
            embeddings_file = self.persist_path / "embeddings.npy"
            np.save(embeddings_file, self.embeddings_dict, allow_pickle=True)
            
            # Save texts and metadata
            data_file = self.persist_path / "data.pkl"
            with open(data_file, "wb") as f:
                pickle.dump({
                    "texts": self.texts_dict,
                    "metadata": self.metadata_dict,
                    "ids": self.ids_list
                }, f)
            
            print(f"💾 Saved {len(self.ids_list)} embeddings to disk")
        except Exception as e:
            print(f"⚠️  Error saving embeddings to disk: {e}")
    
    def add_documents(self, chunks: List[str], metadatas: List[Dict], ids: List[str]):
        """Add document chunks to the in-memory store"""
        # Generate embeddings
        embeddings_list = self.embeddings.embed_documents(chunks)
        
        # Store in memory
        for i, (chunk, embedding, metadata, doc_id) in enumerate(zip(chunks, embeddings_list, metadatas, ids)):
            # Convert to numpy array
            embedding_array = np.array(embedding, dtype=np.float32)
            
            # Store
            self.embeddings_dict[doc_id] = embedding_array
            self.texts_dict[doc_id] = chunk
            self.metadata_dict[doc_id] = metadata
            
            if doc_id not in self.ids_list:
                self.ids_list.append(doc_id)
        
        # Save to disk if persistence enabled
        if self.persist_to_disk:
            self._save_to_disk()
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """Search for similar documents using in-memory vector search"""
        if not self.embeddings_dict:
            return {
                "documents": [],
                "metadatas": [],
                "ids": [],
                "distances": []
            }
        
        # Generate query embedding
        query_embedding = np.array(self.embeddings.embed_query(query), dtype=np.float32)
        
        # Get all embeddings as a matrix
        ids_array = np.array(self.ids_list)
        embeddings_matrix = np.array([self.embeddings_dict[id] for id in self.ids_list])
        
        # Calculate cosine similarity
        # Normalize query embedding
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        
        # Normalize all embeddings
        embeddings_norm = embeddings_matrix / (np.linalg.norm(embeddings_matrix, axis=1, keepdims=True) + 1e-10)
        
        # Calculate cosine similarity (dot product of normalized vectors)
        similarities = np.dot(embeddings_norm, query_norm)
        
        # Get top N results (highest similarity = lowest distance)
        top_indices = np.argsort(similarities)[::-1][:n_results]
        
        # Convert similarity to distance (1 - similarity for cosine distance)
        distances = 1 - similarities[top_indices]
        
        # Get results
        top_ids = ids_array[top_indices].tolist()
        documents = [self.texts_dict[id] for id in top_ids]
        metadatas = [self.metadata_dict[id] for id in top_ids]
        
        return {
            "documents": documents,
            "metadatas": metadatas,
            "ids": top_ids,
            "distances": distances.tolist()
        }
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        total_size_mb = sum(
            embedding.nbytes for embedding in self.embeddings_dict.values()
        ) / (1024 * 1024)
        
        return {
            "total_documents": len(self.ids_list),
            "collection_name": "in_memory_knowledge_base",
            "memory_usage_mb": round(total_size_mb, 2),
            "embedding_dimension": self.embedding_dim
        }
    
    def get_all_documents(self, limit: int = 100) -> Dict:
        """Get all documents from the collection with metadata"""
        ids_to_return = self.ids_list[:limit]
        return {
            "documents": [self.texts_dict[id] for id in ids_to_return],
            "metadatas": [self.metadata_dict[id] for id in ids_to_return],
            "ids": ids_to_return
        }
    
    def delete_collection(self):
        """Clear all in-memory data"""
        self.embeddings_dict.clear()
        self.texts_dict.clear()
        self.metadata_dict.clear()
        self.ids_list.clear()
        
        # Delete disk files if they exist
        if self.persist_to_disk:
            embeddings_file = self.persist_path / "embeddings.npy"
            data_file = self.persist_path / "data.pkl"
            if embeddings_file.exists():
                embeddings_file.unlink()
            if data_file.exists():
                data_file.unlink()
    
    def get_memory_usage(self) -> Dict:
        """Get detailed memory usage statistics"""
        embedding_size = sum(
            embedding.nbytes for embedding in self.embeddings_dict.values()
        )
        text_size = sum(
            len(text.encode('utf-8')) for text in self.texts_dict.values()
        )
        metadata_size = len(pickle.dumps(self.metadata_dict))
        
        total_mb = (embedding_size + text_size + metadata_size) / (1024 * 1024)
        
        return {
            "embeddings_mb": round(embedding_size / (1024 * 1024), 2),
            "texts_mb": round(text_size / (1024 * 1024), 2),
            "metadata_mb": round(metadata_size / (1024 * 1024), 2),
            "total_mb": round(total_mb, 2),
            "total_documents": len(self.ids_list)
        }
