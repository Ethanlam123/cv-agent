from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from typing_extensions import TypedDict


class CVSection(BaseModel):
    """Represents a section of a CV with its content and metadata."""
    name: str
    content: str
    position: int
    confidence: float = 0.0


class AnalysisScore(BaseModel):
    """Scoring for different aspects of CV analysis."""
    overall_score: float
    section_scores: Dict[str, float]
    ats_compatibility: float
    keyword_density: float
    formatting_score: float
    content_quality: float


class Improvement(BaseModel):
    """Represents a specific improvement suggestion."""
    section: str
    type: str  # 'content', 'format', 'keyword', 'structure'
    original_text: str
    improved_text: str
    reasoning: str
    priority: str  # 'high', 'medium', 'low'
    confidence: float


class CVState(TypedDict):
    """State management for CV processing workflow."""
    # Input data
    original_cv: str
    file_format: str  # 'pdf', 'docx', 'txt'
    target_role: Optional[str]
    target_industry: Optional[str]
    
    # Parsed content
    parsed_sections: Dict[str, CVSection]
    raw_text: str
    
    # Analysis results
    analysis_scores: Optional[AnalysisScore]
    identified_gaps: List[str]
    
    # Improvements
    suggested_improvements: List[Improvement]
    applied_improvements: List[Improvement]
    
    # Output
    enhanced_cv: Optional[str]
    enhancement_summary: Optional[str]
    
    # Metadata
    processing_errors: List[str]
    processing_time: Optional[float]
    model_used: Optional[str]