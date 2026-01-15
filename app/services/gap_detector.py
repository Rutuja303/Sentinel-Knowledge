import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from app.models.schemas import KnowledgeGap
from app.utils.config import config


class GapDetectorService:
    """Service for detecting knowledge gaps"""
    
    def __init__(self, storage_path: str = "./data/gaps.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.gaps: Dict[str, KnowledgeGap] = {}
        self.query_history: List[Dict] = []
        self.load_gaps()
    
    def load_gaps(self):
        """Load gaps from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for gap_id, gap_data in data.get("gaps", {}).items():
                        self.gaps[gap_id] = KnowledgeGap(**gap_data)
                    self.query_history = data.get("query_history", [])
            except Exception as e:
                print(f"Error loading gaps: {e}")
    
    def save_gaps(self):
        """Save gaps to storage"""
        try:
            data = {
                "gaps": {gap_id: gap.dict() for gap_id, gap in self.gaps.items()},
                "query_history": self.query_history
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving gaps: {e}")
    
    def detect_gap(
        self,
        query: str,
        answer: str,
        similarity_scores: List[float],
        retrieved_documents: List[str],
        user_id: Optional[str] = None,
        source_page_id: Optional[str] = None,
        source_page_title: Optional[str] = None,
        source_document: Optional[str] = None
    ) -> Optional[KnowledgeGap]:
        """Detect if a query represents a knowledge gap"""
        
        # Record query in history
        self.query_history.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "similarity_scores": similarity_scores,
            "num_documents": len(retrieved_documents)
        })
        
        gap_type = None
        severity = "low"
        reason = None
        
        # Detection Rule 1: Low similarity scores
        if similarity_scores:
            max_similarity = max(similarity_scores)
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
            
            if max_similarity < config.MIN_SIMILARITY_SCORE:
                gap_type = "low_similarity"
                severity = "high" if max_similarity < 0.2 else "medium"
                reason = f"Low similarity score: {max_similarity:.2f} (threshold: {config.MIN_SIMILARITY_SCORE})"
        
        # Detection Rule 2: Empty retrieval
        if not retrieved_documents or len(retrieved_documents) == 0:
            gap_type = "empty_retrieval"
            severity = "high"
            reason = "No relevant documents found"
        
        # Detection Rule 3: Uncertainty phrases in answer
        answer_lower = answer.lower()
        for phrase in config.UNCERTAINTY_PHRASES:
            if phrase.lower() in answer_lower:
                gap_type = "uncertainty"
                severity = "medium"
                reason = f"Answer contains uncertainty phrase: '{phrase}'"
                break
        
        # Detection Rule 4: Repeated queries
        similar_queries = [
            q for q in self.query_history[-50:]  # Check last 50 queries
            if self._are_similar_queries(query, q["query"])
        ]
        
        if len(similar_queries) >= config.REPEATED_QUERY_THRESHOLD:
            gap_type = "repeated_query"
            severity = "high"
            reason = f"Query asked {len(similar_queries)} times without good answer"
        
        # If gap detected, create or update gap record
        if gap_type:
            gap_id = self._generate_gap_id(query, gap_type)
            
            if gap_id in self.gaps:
                # Update existing gap
                gap = self.gaps[gap_id]
                gap.occurrence_count += 1
                gap.last_detected = datetime.now()
                if user_id and user_id not in gap.users_affected:
                    gap.users_affected.append(user_id)
            else:
                # Create new gap
                gap = KnowledgeGap(
                    id=gap_id,
                    query=query,
                    gap_type=gap_type,
                    severity=severity,
                    occurrence_count=1,
                    first_detected=datetime.now(),
                    last_detected=datetime.now(),
                    users_affected=[user_id] if user_id else [],
                    suggested_topic=self._suggest_topic(query),
                    source_page_id=source_page_id,
                    source_page_title=source_page_title,
                    source_document=source_document
                )
                self.gaps[gap_id] = gap
            
            self.save_gaps()
            return gap
        
        return None
    
    def _are_similar_queries(self, q1: str, q2: str) -> bool:
        """Check if two queries are similar (simple implementation)"""
        # Simple similarity: check if they share significant words
        words1 = set(q1.lower().split())
        words2 = set(q2.lower().split())
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "how", "what", "when", "where", "who", "why"}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        if not words1 or not words2:
            return False
        
        # Check overlap
        overlap = len(words1 & words2) / len(words1 | words2)
        return overlap > 0.5  # 50% word overlap
    
    def _generate_gap_id(self, query: str, gap_type: str) -> str:
        """Generate a unique ID for a gap"""
        import hashlib
        key = f"{gap_type}:{query.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()[:12]
    
    def _suggest_topic(self, query: str) -> str:
        """Suggest a documentation topic based on the query"""
        # Simple extraction: take key words from query
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "how", "what", "when", "where", "who", "why", "do", "does", "did"}
        words = [w for w in query.lower().split() if w not in stop_words]
        if words:
            return " ".join(words[:5]).title()
        return "General Documentation"
    
    def get_all_gaps(self) -> List[KnowledgeGap]:
        """Get all detected gaps"""
        return list(self.gaps.values())
    
    def get_gaps_by_severity(self, severity: str) -> List[KnowledgeGap]:
        """Get gaps filtered by severity"""
        return [gap for gap in self.gaps.values() if gap.severity == severity]
    
    def get_top_gaps(self, limit: int = 10) -> List[KnowledgeGap]:
        """Get top gaps by occurrence count"""
        gaps = sorted(
            self.gaps.values(),
            key=lambda g: (g.occurrence_count, 1 if g.severity == "high" else 0.5 if g.severity == "medium" else 0),
            reverse=True
        )
        return gaps[:limit]
    
    def get_query_statistics(self) -> Dict:
        """Get statistics about queries"""
        total_queries = len(self.query_history)
        total_gaps = len(self.gaps)
        
        gap_types = {}
        for gap in self.gaps.values():
            gap_types[gap.gap_type] = gap_types.get(gap.gap_type, 0) + 1
        
        return {
            "total_queries": total_queries,
            "total_gaps": total_gaps,
            "gap_rate": total_gaps / total_queries if total_queries > 0 else 0,
            "gap_types": gap_types,
            "severity_breakdown": {
                "high": len(self.get_gaps_by_severity("high")),
                "medium": len(self.get_gaps_by_severity("medium")),
                "low": len(self.get_gaps_by_severity("low"))
            }
        }
