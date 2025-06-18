"""
Analysis Result Model

This module defines the AnalysisResult class, which represents the result of analyzing
an academic paper for AI-generated content, hallucinations, and misunderstandings.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class ContentIssue:
    """
    Represents an issue identified in the content of a paper.
    """
    
    issue_type: str
    """Type of issue (e.g., 'ai_generated', 'hallucination', 'misunderstanding')."""
    
    section: str
    """Section of the paper where the issue was found."""
    
    score: float
    """Confidence score for the issue (0.0 to 1.0)."""
    
    details: str = ""
    """Detailed description of the issue."""
    
    evidence: str = ""
    """Evidence supporting the identification of the issue."""


@dataclass
class AnalysisResult:
    """
    Represents the result of analyzing an academic paper.
    """
    
    paper_id: str
    """ID of the analyzed paper."""
    
    source: str
    """Source of the paper (e.g., 'arxiv', 'pubmed')."""
    
    title: str
    """Title of the paper."""
    
    success: bool
    """Whether the analysis was successful."""
    
    authors: List[str] = field(default_factory=list)
    """List of authors."""
    
    publication_date: Optional[datetime] = None
    """Publication date of the paper."""
    
    error: str = ""
    """Error message if analysis failed."""
    
    issues: List[ContentIssue] = field(default_factory=list)
    """List of identified issues."""
    
    section_scores: Dict[str, Dict[str, float]] = field(default_factory=dict)
    """Scores for each section of the paper."""
    
    overall_scores: Dict[str, float] = field(default_factory=dict)
    """Overall scores for the paper."""
    
    verdict: Optional[str] = None
    """Overall verdict ('legitimate', 'questionable', 'suspicious')."""
    
    recommendations: List[str] = field(default_factory=list)
    """Recommendations based on the analysis."""
    
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    """Timestamp of when the analysis was performed."""
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the analysis result to a dictionary.
        
        Returns:
            Dictionary representation of the analysis result
        """
        return {
            "paper_id": self.paper_id,
            "source": self.source,
            "title": self.title,
            "success": self.success,
            "authors": self.authors,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "error": self.error if not self.success else "",
            "issues": [
                {
                    "issue_type": issue.issue_type,
                    "section": issue.section,
                    "score": issue.score,
                    "details": issue.details,
                    "evidence": issue.evidence
                }
                for issue in self.issues
            ],
            "section_scores": self.section_scores,
            "overall_scores": self.overall_scores,
            "verdict": self.verdict,
            "recommendations": self.recommendations,
            "analysis_timestamp": self.analysis_timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """
        Create an AnalysisResult instance from a dictionary.
        
        Args:
            data: Dictionary containing analysis result data
            
        Returns:
            AnalysisResult instance
        """
        # Handle publication date
        pub_date = data.get("publication_date")
        if pub_date and isinstance(pub_date, str):
            try:
                pub_date = datetime.fromisoformat(pub_date)
            except ValueError:
                pub_date = None
        
        # Handle analysis timestamp
        timestamp = data.get("analysis_timestamp")
        if timestamp and isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        # Create issues
        issues = []
        for issue_data in data.get("issues", []):
            issues.append(ContentIssue(
                issue_type=issue_data["issue_type"],
                section=issue_data["section"],
                score=issue_data["score"],
                details=issue_data.get("details", ""),
                evidence=issue_data.get("evidence", "")
            ))
        
        return cls(
            paper_id=data["paper_id"],
            source=data["source"],
            title=data["title"],
            success=data["success"],
            authors=data.get("authors", []),
            publication_date=pub_date,
            error=data.get("error", ""),
            issues=issues,
            section_scores=data.get("section_scores", {}),
            overall_scores=data.get("overall_scores", {}),
            verdict=data.get("verdict"),
            recommendations=data.get("recommendations", []),
            analysis_timestamp=timestamp
        )
    
    def get_issue_count(self, issue_type: Optional[str] = None) -> int:
        """
        Get the count of issues of a specific type.
        
        Args:
            issue_type: Type of issue to count (None for all issues)
            
        Returns:
            Count of issues
        """
        if issue_type:
            return sum(1 for issue in self.issues if issue.issue_type == issue_type)
        return len(self.issues)
    
    def has_issues(self) -> bool:
        """
        Check if the analysis result has any issues.
        
        Returns:
            True if there are issues, False otherwise
        """
        return len(self.issues) > 0
    
    def get_max_score(self, score_type: str) -> float:
        """
        Get the maximum score of a specific type across all sections.
        
        Args:
            score_type: Type of score to get
            
        Returns:
            Maximum score
        """
        max_score = 0.0
        for section_scores in self.section_scores.values():
            score = section_scores.get(score_type, 0.0)
            max_score = max(max_score, score)
        return max_score