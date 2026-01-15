from typing import Dict, List, Tuple
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.embeddings import EmbeddingService
from app.utils.config import config


class RAGService:
    """RAG (Retrieval Augmented Generation) Service"""
    
    def __init__(self, embedding_service: EmbeddingService):
        config.validate()
        self.embedding_service = embedding_service
        import os
        
        # Initialize LLM based on provider
        if config.LLM_PROVIDER == "ollama":
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=config.OLLAMA_LLM_MODEL,
                base_url=config.OLLAMA_BASE_URL,
                temperature=0.1,
                timeout=120.0  # 2 minute timeout per LLM call
            )
        else:  # OpenAI
            from langchain_openai import ChatOpenAI
            os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
            self.llm = ChatOpenAI(
                model=config.OPENAI_LLM_MODEL,
                temperature=0.1
            )
        
        # System prompt for the LLM
        self.system_prompt = """You are a helpful assistant that answers questions based on the provided context from company documentation.
        
Rules:
1. Only answer based on the provided context
2. If the context doesn't contain enough information, say so clearly
3. Be concise and accurate
4. Cite which document/section you're using when possible
5. If you're uncertain, explicitly state your uncertainty"""
    
    def retrieve(self, query: str, n_results: int = 10) -> Tuple[List[str], List[float], List[Dict]]:
        """Retrieve relevant documents for a query (searches across ALL documents in knowledge base)"""
        # Search across ALL documents in the knowledge base (not limited to one file)
        # Increased n_results to get more diverse sources from different files
        results = self.embedding_service.search(query, n_results=n_results)
        
        documents = results["documents"]
        distances = results["distances"]
        metadatas = results["metadatas"]
        
        # Convert distances to similarity scores (cosine distance -> similarity)
        # Lower distance = higher similarity
        similarity_scores = [1 - dist for dist in distances]
        
        return documents, similarity_scores, metadatas
    
    def generate_answer(self, query: str, context_docs: List[str], similarity_scores: List[float]) -> str:
        """Generate an answer using the retrieved context"""
        # Build context string
        context_parts = []
        for i, (doc, score) in enumerate(zip(context_docs, similarity_scores), 1):
            context_parts.append(f"[Document {i} - Relevance: {score:.2f}]\n{doc}\n")
        
        context = "\n---\n".join(context_parts)
        
        # Create prompt
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Context from documentation:
{context}

Question: {query}

Please provide an answer based on the context above. If the context doesn't contain enough information to answer the question, please state that clearly.""")
        ]
        
        # Generate response with timeout handling
        try:
            response = self.llm.invoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            # If LLM call fails, return a basic response
            print(f"LLM generation error: {e}")
            return "I encountered an error while generating a response. Please try again."
    
    def query(self, question: str, n_results: int = 10) -> Dict:
        """Complete RAG query: retrieve + generate (searches across ALL files)"""
        # Retrieve relevant documents from ALL files (increased n_results for better coverage)
        documents, similarity_scores, metadatas = self.retrieve(question, n_results)
        
        # Generate answer
        answer = self.generate_answer(question, documents, similarity_scores)
        
        # Extract source filenames
        sources = [meta.get("filename", "Unknown") for meta in metadatas]
        
        # Calculate average confidence (based on similarity scores)
        avg_confidence = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence_score": avg_confidence,
            "similarity_scores": similarity_scores,
            "retrieved_documents": documents,
            "metadatas": metadatas
        }
