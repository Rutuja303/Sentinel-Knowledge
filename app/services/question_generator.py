from typing import List, Dict
from langchain_core.messages import HumanMessage, SystemMessage
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
                temperature=0.7,  # Higher temperature for more creative questions
                timeout=120.0  # 2 minute timeout per LLM call
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
    
    def generate_questions_for_page(self, page_id: str, num_questions: int = 5) -> List[str]:
        """Generate questions specifically for a Confluence page"""
        try:
            # Get all documents and filter by page_id
            all_results = self.embedding_service.collection.get(limit=1000)
            
            # Filter documents from this specific page
            page_documents = []
            page_title = ""
            for i, metadata in enumerate(all_results.get("metadatas", [])):
                if metadata.get("page_id") == page_id:
                    doc = all_results.get("documents", [])[i]
                    if doc:
                        page_documents.append(doc)
                    if not page_title and metadata.get("title"):
                        page_title = metadata.get("title", "")
            
            if not page_documents:
                # Fallback if page not found
                return self._get_fallback_questions()[:num_questions]
            
            # Get sample content from this page
            samples = [doc[:300] for doc in page_documents[:5] if doc]
            
            samples_text = "\n".join([f"- {s}" for s in samples])
            
            # Generate questions based on this page's content
            prompt = f"""Based on the following content from a Confluence page titled "{page_title}", generate {num_questions} relevant questions that users might ask about this page.

Page Content Samples:
{samples_text}

Generate {num_questions} specific questions that:
1. Are directly related to the content shown
2. Cover different aspects of the page (procedures, concepts, troubleshooting)
3. Are phrased naturally as users would ask them
4. Are specific to this page's content

Return only the questions, one per line, without numbering or bullets."""

            messages = [
                SystemMessage(content="You are a helpful assistant that generates relevant questions based on documentation content."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm(messages)
            questions = [q.strip() for q in response.content.split('\n') if q.strip()]
            
            # Clean up questions
            cleaned_questions = []
            for q in questions:
                q = q.lstrip('0123456789.-) ').strip()
                if q and len(q) > 10:
                    cleaned_questions.append(q)
            
            # If we got fewer questions, add some generic ones
            if len(cleaned_questions) < num_questions:
                generic = [
                    f"What is covered in {page_title}?",
                    f"How does {page_title} work?",
                    f"What are the key points in {page_title}?",
                    f"Can you explain {page_title}?",
                    f"What procedures are described in {page_title}?"
                ]
                for gq in generic:
                    if len(cleaned_questions) < num_questions:
                        cleaned_questions.append(gq)
            
            return cleaned_questions[:num_questions]
        
        except Exception as e:
            print(f"Error generating questions for page: {e}")
            return self._get_fallback_questions()[:num_questions]
    
    def generate_questions_for_confluence(self, num_questions: int = 20) -> List[str]:
        """Generate questions based on ALL Confluence content"""
        try:
            # Get ALL Confluence documents (increased limit to ensure we get everything)
            confluence_docs = self.embedding_service.get_confluence_documents(limit=50000)
            
            if not confluence_docs.get("documents"):
                return self._get_fallback_questions()[:num_questions]
            
            print(f"📊 Generating questions from {len(confluence_docs.get('documents', []))} Confluence document chunks")
            
            # Get unique page titles from ALL documents
            page_titles = set()
            for metadata in confluence_docs.get("metadatas", []):
                if metadata.get("title"):
                    page_titles.add(metadata.get("title"))
            
            print(f"📄 Found {len(page_titles)} unique Confluence pages")
            
            # Get sample content from ALL Confluence documents (more samples for better coverage)
            samples = []
            # Sample from different parts of the collection for better coverage
            total_docs = len(confluence_docs.get("documents", []))
            sample_indices = [0, total_docs // 4, total_docs // 2, 3 * total_docs // 4, total_docs - 1] if total_docs > 5 else list(range(total_docs))
            
            for idx in sample_indices[:20]:  # Get up to 20 samples
                if idx < total_docs:
                    doc = confluence_docs.get("documents", [])[idx]
                    if doc:
                        sample = doc[:300].strip()
                        if sample:
                            samples.append(sample)
            
            if not samples:
                return self._get_fallback_questions()[:num_questions]
            
            # Include ALL page titles (not just first 20) to ensure questions cover all files
            all_titles = list(page_titles)
            titles_text = "\n".join([f"- {title}" for title in all_titles[:50]])  # Show up to 50 titles
            if len(all_titles) > 50:
                titles_text += f"\n... and {len(all_titles) - 50} more pages"
            
            samples_text = "\n".join([f"- {s}" for s in samples[:15]])  # More samples
            
            # Generate questions focused on cross-document consistency and completeness checks
            prompt = f"""Based on the following Confluence pages and content, generate {num_questions} questions that check for documentation gaps and inconsistencies.

IMPORTANT: Focus on questions that detect:
1. Missing information: Things mentioned in one document but not defined/explained in another
2. Inconsistencies: Conflicting information between documents
3. Incomplete coverage: Items listed in one place but missing details elsewhere

DO NOT generate logical reasoning questions or questions that require engineering judgment.

Confluence Pages ({len(all_titles)} total pages):
{titles_text}

Sample Content from various pages:
{samples_text}

Generate {num_questions} questions that:
1. Check if items mentioned in one document are fully defined in another (e.g., "Are all marts listed in Business marts page also defined in Mart Schemas?")
2. Verify consistency of information across documents (e.g., "Do the mart names match between Business marts and Mart Schemas?")
3. Check for missing definitions or explanations (e.g., "Is the sentiment mart schema defined?")
4. Verify completeness of cross-references between documents
5. Check for conflicting information about the same topic

Examples of GOOD questions:
- "Are all 4 marts from Business marts page defined in Mart Schemas?"
- "What marts are mentioned in Business marts but missing schema definitions?"
- "Do the refresh cadences in Business marts match the implementation details elsewhere?"

Examples of BAD questions (DO NOT generate these):
- "How do core dimensions relate to business goals?" (logical reasoning)
- "What is the purpose of X?" (general question)
- "How does Y work?" (requires engineering judgment)

Return only the questions, one per line, without numbering or bullets."""

            messages = [
                SystemMessage(content="You are a helpful assistant that generates relevant questions based on documentation content."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm(messages)
            questions = [q.strip() for q in response.content.split('\n') if q.strip()]
            
            # Clean up questions
            cleaned_questions = []
            for q in questions:
                q = q.lstrip('0123456789.-) ').strip()
                if q and len(q) > 10:
                    cleaned_questions.append(q)
            
            # If we got fewer questions, add fallbacks
            if len(cleaned_questions) < num_questions:
                fallbacks = self._get_fallback_questions()
                for fq in fallbacks:
                    if fq not in cleaned_questions and len(cleaned_questions) < num_questions:
                        cleaned_questions.append(fq)
            
            return cleaned_questions[:num_questions]
        
        except Exception as e:
            print(f"Error generating questions for Confluence: {e}")
            return self._get_fallback_questions()[:num_questions]
    
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
