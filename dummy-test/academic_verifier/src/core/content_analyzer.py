"""
Content Analyzer Module

This module is responsible for analyzing academic papers to detect AI-generated content,
hallucinations, and misunderstandings using the TRSHR API.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..api.trshr_client import TRSHRClient
from ..models.paper import Paper
from ..models.analysis_result import AnalysisResult, ContentIssue
from ..utils.text_processor import extract_sections, clean_text

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """
    Analyzes academic papers for AI-generated content, hallucinations, and misunderstandings.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the content analyzer.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.analysis_config = config.get("analysis", {})
        
        # Initialize TRSHR API client
        self.trshr_client = TRSHRClient(config)
        
        # Get analysis thresholds
        self.thresholds = self.analysis_config.get("thresholds", {
            "ai_generated": 0.85,
            "hallucination": 0.75,
            "misunderstanding": 0.65
        })
        
        # Get batch processing settings
        self.batch_size = self.analysis_config.get("batch_size", 10)
        self.max_concurrent = self.analysis_config.get("max_concurrent", 5)
        
        # Get model settings
        self.models = self.analysis_config.get("models", {
            "primary": "trshr-academic-v2",
            "fallback": "trshr-standard-v1"
        })
        
        # Get feature flags
        self.features = self.analysis_config.get("features", {
            "citation_check": True,
            "methodology_analysis": True,
            "statistical_validation": True,
            "reference_verification": True,
            "cross_paper_comparison": True
        })
    
    def analyze_batch(self, papers: List[Paper]) -> List[AnalysisResult]:
        """
        Analyze a batch of papers.
        
        Args:
            papers: List of papers to analyze
            
        Returns:
            List of analysis results
        """
        logger.info(f"Analyzing batch of {len(papers)} papers")
        
        results = []
        
        # Process papers in batches
        for i in range(0, len(papers), self.batch_size):
            batch = papers[i:i + self.batch_size]
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            
            # Log progress
            logger.info(f"Processed {min(i + self.batch_size, len(papers))}/{len(papers)} papers")
        
        return results
    
    def _process_batch(self, papers: List[Paper]) -> List[AnalysisResult]:
        """
        Process a batch of papers concurrently.
        
        Args:
            papers: Batch of papers to process
            
        Returns:
            List of analysis results
        """
        results = []
        
        # Use ThreadPoolExecutor for concurrent processing
        max_workers = min(len(papers), self.max_concurrent)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_paper = {
                executor.submit(self.analyze_paper, paper): paper
                for paper in papers
            }
            
            for future in as_completed(future_to_paper):
                paper = future_to_paper[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing paper {paper.id}: {str(e)}")
                    # Create a failed analysis result
                    results.append(AnalysisResult(
                        paper_id=paper.id,
                        source=paper.source,
                        title=paper.title,
                        success=False,
                        error=str(e)
                    ))
        
        return results
    
    def analyze_paper(self, paper: Paper) -> AnalysisResult:
        """
        Analyze a single paper for AI-generated content, hallucinations, and misunderstandings.
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Analysis result
        """
        logger.info(f"Analyzing paper: {paper.title} (ID: {paper.id})")
        
        try:
            # Extract sections from the paper
            sections = extract_sections(paper.content)
            
            # Initialize analysis result
            result = AnalysisResult(
                paper_id=paper.id,
                source=paper.source,
                title=paper.title,
                authors=paper.authors,
                publication_date=paper.publication_date,
                success=True
            )
            
            # Analyze each section
            for section_name, section_text in sections.items():
                # Clean text
                cleaned_text = clean_text(section_text)
                
                # Skip empty sections
                if not cleaned_text:
                    continue
                
                # Analyze with TRSHR API
                try:
                    analysis = self.trshr_client.analyze_text(
                        text=cleaned_text,
                        model=self.models["primary"],
                        features=self.features
                    )
                except Exception as e:
                    logger.warning(f"Error with primary model, trying fallback: {str(e)}")
                    # Try fallback model
                    analysis = self.trshr_client.analyze_text(
                        text=cleaned_text,
                        model=self.models["fallback"],
                        features=self.features
                    )
                
                # Process analysis results
                self._process_section_analysis(result, section_name, analysis)
                
                # Small delay to avoid overwhelming API
                time.sleep(0.1)
            
            # Calculate overall scores
            self._calculate_overall_scores(result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing paper {paper.id}: {str(e)}")
            raise
    
    def _process_section_analysis(
        self, 
        result: AnalysisResult, 
        section_name: str, 
        analysis: Dict[str, Any]
    ) -> None:
        """
        Process analysis results for a paper section.
        
        Args:
            result: Analysis result to update
            section_name: Name of the section
            analysis: Analysis data from TRSHR API
        """
        # Extract scores
        ai_score = analysis.get("ai_generated_score", 0.0)
        hallucination_score = analysis.get("hallucination_score", 0.0)
        misunderstanding_score = analysis.get("misunderstanding_score", 0.0)
        
        # Add section scores to result
        result.section_scores[section_name] = {
            "ai_generated": ai_score,
            "hallucination": hallucination_score,
            "misunderstanding": misunderstanding_score
        }
        
        # Check for issues based on thresholds
        if ai_score >= self.thresholds["ai_generated"]:
            result.issues.append(ContentIssue(
                issue_type="ai_generated",
                section=section_name,
                score=ai_score,
                details=analysis.get("ai_generated_details", "")
            ))
        
        if hallucination_score >= self.thresholds["hallucination"]:
            result.issues.append(ContentIssue(
                issue_type="hallucination",
                section=section_name,
                score=hallucination_score,
                details=analysis.get("hallucination_details", "")
            ))
        
        if misunderstanding_score >= self.thresholds["misunderstanding"]:
            result.issues.append(ContentIssue(
                issue_type="misunderstanding",
                section=section_name,
                score=misunderstanding_score,
                details=analysis.get("misunderstanding_details", "")
            ))
        
        # Add any specific issues identified by the API
        for issue in analysis.get("identified_issues", []):
            result.issues.append(ContentIssue(
                issue_type=issue.get("type", "unknown"),
                section=section_name,
                score=issue.get("confidence", 0.0),
                details=issue.get("details", ""),
                evidence=issue.get("evidence", "")
            ))
    
    def _calculate_overall_scores(self, result: AnalysisResult) -> None:
        """
        Calculate overall scores for the paper.
        
        Args:
            result: Analysis result to update
        """
        if not result.section_scores:
            return
        
        # Calculate weighted average for each score type
        section_weights = {
            "abstract": 1.5,
            "introduction": 1.0,
            "methodology": 2.0,
            "results": 2.0,
            "discussion": 1.5,
            "conclusion": 1.0
        }
        
        total_weight = 0
        weighted_scores = {
            "ai_generated": 0.0,
            "hallucination": 0.0,
            "misunderstanding": 0.0
        }
        
        for section, scores in result.section_scores.items():
            weight = section_weights.get(section.lower(), 1.0)
            total_weight += weight
            
            for score_type, score in scores.items():
                weighted_scores[score_type] += score * weight
        
        # Normalize by total weight
        if total_weight > 0:
            for score_type in weighted_scores:
                weighted_scores[score_type] /= total_weight
        
        result.overall_scores = weighted_scores
        
        # Determine overall verdict
        if (weighted_scores["ai_generated"] >= self.thresholds["ai_generated"] or
            weighted_scores["hallucination"] >= self.thresholds["hallucination"] or
            weighted_scores["misunderstanding"] >= self.thresholds["misunderstanding"]):
            result.verdict = "suspicious"
        elif (weighted_scores["ai_generated"] >= self.thresholds["ai_generated"] * 0.8 or
              weighted_scores["hallucination"] >= self.thresholds["hallucination"] * 0.8 or
              weighted_scores["misunderstanding"] >= self.thresholds["misunderstanding"] * 0.8):
            result.verdict = "questionable"
        else:
            result.verdict = "legitimate"