from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for querying the knowledge base"""
    question: str = Field(..., description="The question to ask")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    context: Optional[Dict] = Field(None, description="Additional context")


class QueryResponse(BaseModel):
    """Response model for query results"""
    answer: str = Field(..., description="The generated answer")
    sources: List[str] = Field(default_factory=list, description="Source documents used")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the answer")
    is_gap: bool = Field(False, description="Whether this represents a knowledge gap")
    gap_reason: Optional[str] = Field(None, description="Reason for gap detection")
    similarity_scores: List[float] = Field(default_factory=list, description="Similarity scores of retrieved docs")
    timestamp: datetime = Field(default_factory=datetime.now)


class KnowledgeGap(BaseModel):
    """Model representing a detected knowledge gap"""
    id: str = Field(..., description="Unique identifier for the gap")
    query: str = Field(..., description="The question that revealed the gap")
    gap_type: str = Field(..., description="Type of gap: low_similarity, repeated_query, uncertainty, empty_retrieval")
    severity: str = Field(..., description="Severity: high, medium, low")
    occurrence_count: int = Field(1, description="Number of times this gap was detected")
    first_detected: datetime = Field(default_factory=datetime.now)
    last_detected: datetime = Field(default_factory=datetime.now)
    users_affected: List[str] = Field(default_factory=list, description="Users who encountered this gap")
    suggested_topic: Optional[str] = Field(None, description="Suggested documentation topic")


class DocumentMetadata(BaseModel):
    """Metadata for ingested documents"""
    filename: str
    file_type: str
    size: int
    chunks: int
    ingested_at: datetime = Field(default_factory=datetime.now)
    owner: Optional[str] = None
