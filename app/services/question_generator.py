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
        """Generate suggested questions based on ALL knowledge base content"""
        try:
            # Get ALL documents from the knowledge base (not just limited sample)
            all_docs = self.embedding_service.get_all_documents(limit=1000)
            
            if not all_docs.get("documents") or len(all_docs.get("documents", [])) == 0:
                print("⚠️  No documents in knowledge base for question generation")
                return []
            
            # Get topics from ALL documents (increased limit)
            topics = self.get_document_topics(limit=100)
            samples = self.get_sample_content(limit=30)  # More samples for better coverage
            
            if not topics and not samples:
                print("⚠️  No topics or samples found for question generation")
                return []
            
            # Build comprehensive context for question generation
            # Include all unique topics
            unique_topics = list(set([t['title'] for t in topics]))
            topics_text = "\n".join([f"- {title}" for title in unique_topics[:50]])
            if len(unique_topics) > 50:
                topics_text += f"\n... and {len(unique_topics) - 50} more topics"
            
            # Include diverse samples from different parts of the collection
            samples_text = "\n".join([f"- {s}" for s in samples[:20]])
            
            print(f"📊 Generating {num_questions} questions from {len(unique_topics)} unique topics and {len(samples)} content samples")
            
            # Generate questions using LLM with comprehensive context
            prompt = f"""Based on the following documentation topics and content samples from our knowledge base, generate {num_questions} relevant questions that users might ask.

Documentation Topics ({len(unique_topics)} total):
{topics_text}

Sample Content from various documents:
{samples_text}

Generate {num_questions} diverse, practical questions that:
1. Are based EXCLUSIVELY on the actual topics and content shown above
2. Cover different aspects (how-to, what-is, troubleshooting, procedures, configuration)
3. Are phrased naturally as users would ask them
4. Are specific and actionable
5. Reference specific topics, processes, or concepts from the documentation
6. Cover different files/topics, not just one area

IMPORTANT: Only generate questions based on the topics and content provided. Do not use generic questions.

Return only the questions, one per line, without numbering or bullets."""

            messages = [
                SystemMessage(content="You are a helpful assistant that generates relevant questions based ONLY on the provided documentation topics and content. Never use generic or fallback questions."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm(messages)
            questions = [q.strip() for q in response.content.split('\n') if q.strip()]
            
            # Clean up questions (remove numbering, bullets, etc.)
            cleaned_questions = []
            for q in questions:
                # Remove leading numbers, bullets, dashes
                q = q.lstrip('0123456789.-) ').strip()
                # Remove question marks if at start (some LLMs add them)
                if q.startswith('?'):
                    q = q[1:].strip()
                if q and len(q) > 10:  # Filter out very short or empty questions
                    cleaned_questions.append(q)
            
            # Return what we have (don't add fallbacks - only use actual generated questions)
            if len(cleaned_questions) > 0:
                print(f"✅ Generated {len(cleaned_questions)} questions from knowledge base content")
                return cleaned_questions[:num_questions]
            else:
                print("⚠️  No valid questions generated")
                return []
        
        except Exception as e:
            print(f"❌ Error generating questions: {e}")
            import traceback
            traceback.print_exc()
            # Return empty list instead of fallback - let user know they need data
            return []
    
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
            
            # Generate questions based on ALL Confluence content from ALL files
            prompt = f"""Based on the following Confluence pages and content from your knowledge base, generate {num_questions} relevant questions that users might ask about this documentation.

IMPORTANT: Generate questions that cover DIFFERENT files/pages, not just one file. Ensure questions are distributed across all the pages listed below.

Confluence Pages ({len(all_titles)} total pages):
{titles_text}

Sample Content from various pages:
{samples_text}

Generate {num_questions} diverse questions that:
1. Cover different topics across ALL the Confluence pages (not just one page)
2. Include questions from at least {min(5, len(all_titles))} different pages/files
3. Include how-to questions, what-is questions, troubleshooting questions
4. Are phrased naturally as users would ask them
5. Are specific and actionable
6. Cover potential gaps in documentation across multiple files

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
