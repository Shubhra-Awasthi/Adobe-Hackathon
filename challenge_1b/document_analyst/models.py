"""
Data models for the Intelligent Document Analyst.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Document:
    """Represents a processed PDF document."""
    filename: str
    text: str
    pages: int
    metadata: Dict[str, Any]
    
    
@dataclass(frozen=True)
class Chunk:
    """Represents a text chunk from a document."""
    text: str
    source_doc: str
    start_page: int
    end_page: int
    section_title: Optional[str] = None
    font_info: Optional[str] = None  # Changed to string for hashability
    

@dataclass
class ScoredSentence:
    """Represents a sentence with its relevance score."""
    text: str
    score: float
    

@dataclass
class ScoredChunk:
    """Represents a chunk with its relevance score and top sentences."""
    chunk: Chunk
    score: float
    top_sentences: List[ScoredSentence]
    

@dataclass
class AnalysisResult:
    """Final analysis result containing all metadata and scored chunks."""
    metadata: Dict[str, Any]
    results: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "metadata": self.metadata,
            "results": self.results
        }