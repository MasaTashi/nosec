"""
Paper Model

This module defines the Paper class, which represents an academic paper.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Paper:
    """
    Represents an academic paper.
    """
    
    id: str
    """Unique identifier for the paper."""
    
    source: str
    """Source of the paper (e.g., 'arxiv', 'pubmed')."""
    
    title: str
    """Title of the paper."""
    
    authors: List[str] = field(default_factory=list)
    """List of authors."""
    
    abstract: str = ""
    """Abstract of the paper."""
    
    content: str = ""
    """Full content of the paper."""
    
    publication_date: Optional[datetime] = None
    """Publication date of the paper."""
    
    doi: Optional[str] = None
    """Digital Object Identifier."""
    
    url: Optional[str] = None
    """URL to the paper."""
    
    keywords: List[str] = field(default_factory=list)
    """Keywords associated with the paper."""
    
    references: List[str] = field(default_factory=list)
    """References cited in the paper."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata."""
    
    def __post_init__(self):
        """Validate and clean up data after initialization."""
        # Ensure title is a string
        if not isinstance(self.title, str):
            self.title = str(self.title)
        
        # Ensure authors is a list
        if not isinstance(self.authors, list):
            self.authors = [str(self.authors)]
        
        # Ensure content is a string
        if not isinstance(self.content, str):
            self.content = str(self.content)
    
    @property
    def citation(self) -> str:
        """
        Get a citation string for the paper.
        
        Returns:
            Citation string
        """
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += " et al."
        
        year = self.publication_date.year if self.publication_date else "n.d."
        
        return f"{authors_str} ({year}). {self.title}."
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the paper to a dictionary.
        
        Returns:
            Dictionary representation of the paper
        """
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "doi": self.doi,
            "url": self.url,
            "keywords": self.keywords,
            "references": self.references,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paper':
        """
        Create a Paper instance from a dictionary.
        
        Args:
            data: Dictionary containing paper data
            
        Returns:
            Paper instance
        """
        # Handle publication date
        pub_date = data.get("publication_date")
        if pub_date and isinstance(pub_date, str):
            try:
                pub_date = datetime.fromisoformat(pub_date)
            except ValueError:
                pub_date = None
        
        return cls(
            id=data["id"],
            source=data["source"],
            title=data["title"],
            authors=data.get("authors", []),
            abstract=data.get("abstract", ""),
            content=data.get("content", ""),
            publication_date=pub_date,
            doi=data.get("doi"),
            url=data.get("url"),
            keywords=data.get("keywords", []),
            references=data.get("references", []),
            metadata=data.get("metadata", {})
        )