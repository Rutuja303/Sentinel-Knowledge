from typing import List, Dict
from langchain.schema import HumanMessage, SystemMessage
from app.services.embeddings import EmbeddingService
from app.utils.config import config
import os


class QuestionGeneratorService:
    """Service for generating suggested questions based on knowledge base content"""
    
    def __init__(self, embedding_service: EmbeddingService):
        config.validate()
        
        self.embedding_service = embedding_service
        
        # Initialize LLM based on provider
        if config.LLM_PROVIDER == "ollama":
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=config.OLLAMA_LLM_MODEL,
                base_url=config.OLLAMA_BASE_URL,
                temperature=0.7  # Higher temperature for more creative questions
            )
        else:  # OpenAI
            from langchain_openai import ChatOpenAI
            os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
            self.llm = ChatOpenAI(
                model=config.OPENAI_LLM_MODEL,
                temperature=0.7
            )
    
    def get_document_topics(self, limit: int = 50) -> List[Dict]:
        """Extract topics/titles from documents in the knowledge base"""
        try:
            # Check if collection has documents
            if self.embedding_service.collection.count() == 0:
                return []
            
            # Get all documents from the collection
            results = self.embedding_service.collection.get(
                limit=limit
            )
            
            topics = []
            seen_titles = set()
            
            for metadata in results.get("metadatas", []):
                # Extract title from metadata
                title = metadata.get("title") or metadata.get("filename", "Unknown")
                
                # Avoid duplicates
                if title not in seen_titles and title != "Unknown":
                    seen_titles.add(title)
                    topics.append({
                        "title": title,
                        "source": metadata.get("source", "unknown"),
                        "url": metadata.get("url"),
                        "space": metadata.get("space"),
                        "space_name": metadata.get("space_name")
                    })
            
            return topics
        except Exception as e:
            print(f"Error getting document topics: {e}")
            return []
    
    def get_sample_content(self, limit: int = 20) -> List[str]:
        """Get sample content snippets from the knowledge base"""
        try:
            # Check if collection has documents
            if self.embedding_service.collection.count() == 0:
                return []
            
            results = self.embedding_service.collection.get(
                limit=limit
            )
            
            samples = []
            for doc in results.get("documents", []):
                # Take first 200 characters as a sample
                if doc:
                    sample = doc[:200].strip()
                    if sample:
                        samples.append(sample)
            
            return samples
        except Exception as e:
            print(f"Error getting sample content: {e}")
            return []
    
    def generate_questions(self, num_questions: int = 15) -> List[str]:
        """Generate suggested questions based on knowledge base content"""
        try:
            # Get topics and sample content
            topics = self.get_document_topics(limit=30)
            samples = self.get_sample_content(limit=10)
            
            if not topics and not samples:
                # Fallback to generic questions if no content
                return self._get_fallback_questions()
            
            # Build context for question generation
            topics_text = "\n".join([f"- {t['title']}" for t in topics[:20]])
            samples_text = "\n".join([f"- {s}" for s in samples[:5]])
            
            # Generate questions using LLM
            prompt = f"""Based on the following documentation topics and content samples from our knowledge base, generate {num_questions} relevant questions that users might ask.

Documentation Topics:
{topics_text}

Sample Content:
{samples_text}

Generate {num_questions} diverse, practical questions that:
1. Are based on the actual topics and content shown
2. Cover different aspects (how-to, what-is, troubleshooting, procedures)
3. Are phrased naturally as users would ask them
4. Are specific and actionable

Return only the questions, one per line, without numbering or bullets."""

            messages = [
                SystemMessage(content="You are a helpful assistant that generates relevant questions based on documentation topics."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm(messages)
            questions = [q.strip() for q in response.content.split('\n') if q.strip()]
            
            # Clean up questions (remove numbering, bullets, etc.)
            cleaned_questions = []
            for q in questions:
                # Remove leading numbers, bullets, dashes
                q = q.lstrip('0123456789.-) ').strip()
                if q and len(q) > 10:  # Filter out very short or empty questions
                    cleaned_questions.append(q)
            
            # If we got fewer questions than requested, add fallbacks
            if len(cleaned_questions) < num_questions:
                fallbacks = self._get_fallback_questions()
                for fq in fallbacks:
                    if fq not in cleaned_questions and len(cleaned_questions) < num_questions:
                        cleaned_questions.append(fq)
            
            return cleaned_questions[:num_questions]
        
        except Exception as e:
            print(f"Error generating questions: {e}")
            # Return fallback questions on error
            return self._get_fallback_questions()
    
    def _get_fallback_questions(self) -> List[str]:
        """Fallback questions when content analysis fails"""
        return [
            "How do we handle deployment rollbacks?",
            "What is our incident response procedure?",
            "How do we troubleshoot service failures?",
            "What are the steps for database migrations?",
            "How do we handle payment gateway failures?",
            "What is the process for code reviews?",
            "How do we manage API rate limits?",
            "What happens during a security breach?",
            "How do we scale our infrastructure?",
            "What is our disaster recovery plan?",
            "How do we handle customer data requests?",
            "What are the steps for releasing a new feature?",
            "How do we monitor system performance?",
            "What is our backup and restore procedure?",
            "How do we handle third-party API integrations?"
        ]
