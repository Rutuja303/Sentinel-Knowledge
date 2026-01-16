from typing import List, Dict, Set, Optional
from app.services.embeddings import EmbeddingService
import re
from collections import defaultdict


class CrossDocumentAnalyzer:
    """Analyzes documents directly to find knowledge gaps without generating questions"""
    
    def __init__(self, embedding_service: EmbeddingService, confluence_docs: Dict):
        self.embedding_service = embedding_service
        self.confluence_docs = confluence_docs
        self.documents_by_title = defaultdict(list)
        self.documents_by_id = {}
        
        # Organize documents by title and ID
        for i, metadata in enumerate(confluence_docs.get("metadatas", [])):
            # Try multiple fields to get the title - check title, page_title, name, filename, etc.
            title = (metadata.get("title") or 
                    metadata.get("page_title") or 
                    metadata.get("name") or 
                    metadata.get("filename") or 
                    metadata.get("file_name") or
                    metadata.get("document_title") or
                    metadata.get("document") or
                    f"Page {metadata.get('page_id', 'Unknown')}")
            page_id = metadata.get("page_id")
            doc_content = confluence_docs.get("documents", [])[i] if i < len(confluence_docs.get("documents", [])) else ""
            
            self.documents_by_title[title].append({
                "content": doc_content,
                "metadata": metadata,
                "page_id": page_id
            })
            if page_id:
                self.documents_by_id[page_id] = {
                    "title": title,
                    "content": doc_content,
                    "metadata": metadata
                }
    
    def extract_entities_from_documents(self) -> Dict[str, Dict]:
        """Extract entities, concepts, and structured information from each document"""
        entities = {}
        
        for title, docs in self.documents_by_title.items():
            # Combine all chunks for this document
            full_content = " ".join([d["content"] for d in docs])
            metadata = docs[0]["metadata"] if docs else {}
            
            entities[title] = {
                "content": full_content,
                "metadata": metadata,
                "page_id": metadata.get("page_id"),
                "url": metadata.get("url"),
                "space": metadata.get("space"),
                "space_name": metadata.get("space_name"),
                # Extract structured information
                "marts": self._extract_marts(full_content),
                "schemas": self._extract_schemas(full_content),
                "tables": self._extract_tables(full_content),
                "entities": self._extract_entities(full_content),
                "definitions": self._extract_definitions(full_content),
                "lists": self._extract_lists(full_content)
            }
        
        return entities
    
    def _extract_marts(self, content: str) -> List[str]:
        """Extract mart names from content"""
        marts = []
        # Look for patterns like "sales mart", "marketing mart", etc.
        patterns = [
            r"(\w+)\s+mart",
            r"mart[:\s]+(\w+)",
            r"##\s+(\w+\s+Mart)",
            r"\*\*(\w+)\s+mart\*\*"
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            marts.extend([m.lower() if isinstance(m, str) else m[0].lower() if isinstance(m, tuple) else str(m).lower() for m in matches])
        
        # Also check table rows for mart names
        lines = content.split('\n')
        for line in lines:
            if '|' in line and 'mart' in line.lower():
                parts = [p.strip() for p in line.split('|')]
                if parts and parts[0] and 'mart' not in parts[0].lower():
                    marts.append(parts[0].lower())
        
        return list(set(marts))
    
    def _extract_schemas(self, content: str) -> List[str]:
        """Extract schema names from content"""
        schemas = []
        # Look for patterns like "analytics_sales schema", "**schema_name schema**"
        patterns = [
            r"\*\*([a-z_]+)\s+schema\*\*",
            r"##\s+(\w+\s+Mart)",
            r"schema[:\s]+([a-z_]+)"
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            schemas.extend([m.lower() if isinstance(m, str) else str(m).lower() for m in matches])
        
        return list(set(schemas))
    
    def _extract_tables(self, content: str) -> List[str]:
        """Extract table/model names from content"""
        tables = []
        # Look for backtick-wrapped table names
        pattern = r"`([a-z_]+)`"
        matches = re.findall(pattern, content, re.IGNORECASE)
        tables.extend([m.lower() for m in matches])
        return list(set(tables))
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract general entities (capitalized terms, important concepts)"""
        entities = []
        # Look for capitalized terms that might be entities
        pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
        matches = re.findall(pattern, content)
        # Filter out common words
        common_words = {"The", "This", "That", "These", "Those", "How", "What", "When", "Where", "Why"}
        entities.extend([m for m in matches if m not in common_words and len(m) > 3])
        return list(set(entities[:20]))  # Limit to top 20
    
    def _extract_definitions(self, content: str) -> Dict[str, str]:
        """Extract definitions (term: description patterns)"""
        definitions = {}
        # Look for patterns like "Term: description" or "**Term**: description"
        patterns = [
            r"\*\*([^:]+)\*\*:\s*([^\n]+)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):\s*([^\n]+)"
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    definitions[match[0].strip()] = match[1].strip()
        return definitions
    
    def _extract_lists(self, content: str) -> List[List[str]]:
        """Extract list items (bulleted or numbered lists)"""
        lists = []
        lines = content.split('\n')
        current_list = []
        for line in lines:
            stripped = line.strip()
            # Check for list markers
            if re.match(r'^[-*•]\s+', stripped) or re.match(r'^\d+\.\s+', stripped):
                item = re.sub(r'^[-*•\d.]\s+', '', stripped)
                if item:
                    current_list.append(item)
            elif current_list:
                lists.append(current_list)
                current_list = []
        if current_list:
            lists.append(current_list)
        return lists
    
    def find_knowledge_gaps(self, document_entities: Dict[str, Dict], unique_pages: Dict) -> List[Dict]:
        """Find knowledge gaps by comparing documents directly"""
        gaps = []
        
        # Example: Compare Business marts with Mart Schemas
        business_marts_doc = None
        mart_schemas_doc = None
        
        for title, data in document_entities.items():
            if "business marts" in title.lower():
                business_marts_doc = data
            elif "mart schemas" in title.lower() or "mart schema" in title.lower():
                mart_schemas_doc = data
        
        # Gap 1: Missing schema definitions
        if business_marts_doc and mart_schemas_doc:
            business_marts_list = business_marts_doc.get("marts", [])
            schemas_list = mart_schemas_doc.get("schemas", [])
            
            # Extract mart names from business marts (from table)
            business_marts_content = business_marts_doc.get("content", "")
            marts_from_table = self._extract_marts_from_table(business_marts_content)
            
            # Extract schema names (mart names from schema headings)
            schema_marts = []
            for schema in schemas_list:
                # Schema names like "analytics_sales" -> "sales"
                if "_" in schema:
                    schema_marts.append(schema.split("_")[-1])
                else:
                    schema_marts.append(schema)
            
            # Find marts mentioned but not defined
            missing_schemas = []
            for mart in marts_from_table:
                if mart not in schema_marts and mart not in [s.lower() for s in schema_marts]:
                    missing_schemas.append(mart)
            
            if missing_schemas:
                # Extract source title with fallback logic
                business_marts_metadata = business_marts_doc.get("metadata", {})
                business_marts_title = (business_marts_metadata.get("title") or 
                                       business_marts_metadata.get("page_title") or 
                                       business_marts_metadata.get("name") or
                                       business_marts_metadata.get("filename") or
                                       "Business marts")
                
                mart_schemas_metadata = mart_schemas_doc.get("metadata", {})
                mart_schemas_title = (mart_schemas_metadata.get("title") or 
                                     mart_schemas_metadata.get("page_title") or 
                                     mart_schemas_metadata.get("name") or
                                     mart_schemas_metadata.get("filename") or
                                     "Mart Schemas")
                
                gaps.append({
                    "gap_description": f"Missing schema definitions: {', '.join([m.capitalize() for m in missing_schemas])} mart(s) are listed in 'Business marts' but do not have schema definitions in 'Mart Schemas'",
                    "gap_type": "incomplete_knowledge",
                    "severity": "high",
                    "source_documents": [business_marts_title, mart_schemas_title],
                    "missing_items": missing_schemas,
                    "source_page_id": business_marts_doc.get("page_id"),
                    "source_page_title": business_marts_title
                })
        
        # Gap 2: Check for inconsistencies in counts
        if business_marts_doc:
            business_marts_content = business_marts_doc.get("content", "")
            marts_count = len(self._extract_marts_from_table(business_marts_content))
            if mart_schemas_doc:
                schemas_count = len(mart_schemas_doc.get("schemas", []))
                if marts_count != schemas_count:
                    # Extract source title with fallback logic
                    business_marts_metadata = business_marts_doc.get("metadata", {})
                    business_marts_title = (business_marts_metadata.get("title") or 
                                           business_marts_metadata.get("page_title") or 
                                           business_marts_metadata.get("name") or
                                           business_marts_metadata.get("filename") or
                                           "Business marts")
                    
                    mart_schemas_metadata = mart_schemas_doc.get("metadata", {})
                    mart_schemas_title = (mart_schemas_metadata.get("title") or 
                                         mart_schemas_metadata.get("page_title") or 
                                         mart_schemas_metadata.get("name") or
                                         mart_schemas_metadata.get("filename") or
                                         "Mart Schemas")
                    
                    gaps.append({
                        "gap_description": f"Inconsistent mart count: 'Business marts' lists {marts_count} marts but 'Mart Schemas' only defines {schemas_count} schemas",
                        "gap_type": "consistency_gap",
                        "severity": "high",
                        "source_documents": [business_marts_title, mart_schemas_title],
                        "source_page_id": business_marts_doc.get("page_id"),
                        "source_page_title": business_marts_title
                    })
        
        # Gap 3: Check for entities mentioned but not defined
        for title, data in document_entities.items():
            entities = data.get("entities", [])
            definitions = data.get("definitions", {})
            
            # Check if important entities are defined
            important_entities = [e for e in entities if len(e.split()) <= 3]  # Simple entities
            undefined_entities = []
            for entity in important_entities[:10]:  # Check top 10
                if entity not in definitions and not any(entity.lower() in def_key.lower() for def_key in definitions.keys()):
                    # Check if it's mentioned in other documents
                    mentioned_elsewhere = False
                    for other_title, other_data in document_entities.items():
                        if other_title != title:
                            other_content = other_data.get("content", "").lower()
                            if entity.lower() in other_content:
                                mentioned_elsewhere = True
                                break
                    
                    if mentioned_elsewhere:
                        undefined_entities.append(entity)
            
            if undefined_entities:
                # Extract source title with fallback logic
                doc_metadata = data.get("metadata", {})
                source_title = (doc_metadata.get("title") or 
                               doc_metadata.get("page_title") or 
                               doc_metadata.get("name") or
                               doc_metadata.get("filename") or
                               title)  # Use the title from the loop if metadata doesn't have it
                
                gaps.append({
                    "gap_description": f"Undefined entities in '{source_title}': {', '.join(undefined_entities[:5])} are mentioned but not clearly defined",
                    "gap_type": "incomplete_knowledge",
                    "severity": "medium",
                    "source_documents": [source_title],
                    "missing_items": undefined_entities[:5],
                    "source_page_id": data.get("page_id"),
                    "source_page_title": source_title
                })
        
        return gaps
    
    def _extract_marts_from_table(self, content: str) -> List[str]:
        """Extract mart names from table in Business marts page"""
        marts = []
        lines = content.split('\n')
        in_table = False
        
        for line in lines:
            if 'Mart| Business Owner' in line or 'mart|' in line.lower():
                in_table = True
                continue
            if line.strip().startswith('---'):
                continue
            if in_table and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if parts and parts[0] and parts[0].lower() not in ['mart', '']:
                    mart_name = parts[0].strip().lower()
                    # Clean up the mart name
                    mart_name = re.sub(r'\s+', ' ', mart_name)
                    marts.append(mart_name)
        
        return list(set(marts))
