"""
Report Generator Module

This module is responsible for generating reports based on the analysis results
of academic papers.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import jinja2

from ..models.analysis_result import AnalysisResult
from ..utils.file_utils import ensure_directory

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates reports based on analysis results.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the report generator.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.report_config = config.get("reports", {})
        self.storage_config = config.get("storage", {})
        
        # Get report formats
        self.formats = self.report_config.get("formats", ["json", "html"])
        
        # Get report content options
        self.include_metadata = self.report_config.get("include_metadata", True)
        self.include_analysis_details = self.report_config.get("include_analysis_details", True)
        self.include_confidence_scores = self.report_config.get("include_confidence_scores", True)
        self.include_recommendations = self.report_config.get("include_recommendations", True)
        
        # Set up Jinja2 environment for HTML templates
        template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def generate(
        self, 
        results: List[AnalysisResult], 
        output_dir: Optional[str] = None
    ) -> str:
        """
        Generate reports based on analysis results.
        
        Args:
            results: List of analysis results
            output_dir: Output directory for reports (optional)
            
        Returns:
            Path to the generated report directory
        """
        if not results:
            logger.warning("No analysis results to generate report from")
            return ""
        
        # Set output directory
        if not output_dir:
            reports_dir = self.storage_config.get("reports_dir", "data/reports")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_dir = os.path.join(reports_dir, timestamp)
        
        # Ensure output directory exists
        ensure_directory(output_dir)
        
        logger.info(f"Generating reports in {output_dir}")
        
        # Generate summary report
        summary = self._generate_summary(results)
        summary_path = os.path.join(output_dir, "summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Generate individual reports
        for result in results:
            self._generate_individual_report(result, output_dir)
        
        # Generate HTML report if requested
        if "html" in self.formats:
            html_path = self._generate_html_report(results, summary, output_dir)
            logger.info(f"Generated HTML report: {html_path}")
        
        # Generate PDF report if requested
        if "pdf" in self.formats:
            try:
                pdf_path = self._generate_pdf_report(results, summary, output_dir)
                logger.info(f"Generated PDF report: {pdf_path}")
            except Exception as e:
                logger.error(f"Failed to generate PDF report: {str(e)}")
        
        logger.info(f"Reports generated successfully in {output_dir}")
        return output_dir
    
    def _generate_summary(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """
        Generate a summary of analysis results.
        
        Args:
            results: List of analysis results
            
        Returns:
            Summary dictionary
        """
        # Count papers by verdict
        verdict_counts = {
            "legitimate": 0,
            "questionable": 0,
            "suspicious": 0,
            "error": 0
        }
        
        for result in results:
            if not result.success:
                verdict_counts["error"] += 1
            else:
                verdict = result.verdict or "legitimate"
                verdict_counts[verdict] += 1
        
        # Count issues by type
        issue_counts = {
            "ai_generated": 0,
            "hallucination": 0,
            "misunderstanding": 0,
            "other": 0
        }
        
        for result in results:
            if result.success:
                for issue in result.issues:
                    issue_type = issue.issue_type
                    if issue_type in issue_counts:
                        issue_counts[issue_type] += 1
                    else:
                        issue_counts["other"] += 1
        
        # Calculate average scores
        avg_scores = {
            "ai_generated": 0.0,
            "hallucination": 0.0,
            "misunderstanding": 0.0
        }
        
        valid_results = [r for r in results if r.success and r.overall_scores]
        if valid_results:
            for score_type in avg_scores:
                avg_scores[score_type] = sum(
                    r.overall_scores.get(score_type, 0.0) for r in valid_results
                ) / len(valid_results)
        
        # Create summary
        return {
            "timestamp": datetime.now().isoformat(),
            "total_papers": len(results),
            "successful_analyses": sum(1 for r in results if r.success),
            "failed_analyses": sum(1 for r in results if not r.success),
            "verdict_counts": verdict_counts,
            "issue_counts": issue_counts,
            "average_scores": avg_scores,
            "sources": list(set(r.source for r in results if r.source)),
            "papers_by_verdict": {
                "suspicious": [
                    {"id": r.paper_id, "title": r.title, "source": r.source}
                    for r in results if r.success and r.verdict == "suspicious"
                ],
                "questionable": [
                    {"id": r.paper_id, "title": r.title, "source": r.source}
                    for r in results if r.success and r.verdict == "questionable"
                ]
            }
        }
    
    def _generate_individual_report(
        self, 
        result: AnalysisResult, 
        output_dir: str
    ) -> str:
        """
        Generate an individual report for a single analysis result.
        
        Args:
            result: Analysis result
            output_dir: Output directory
            
        Returns:
            Path to the generated report file
        """
        # Create report data
        report_data = {
            "paper_id": result.paper_id,
            "source": result.source,
            "title": result.title,
            "success": result.success
        }
        
        if not result.success:
            report_data["error"] = result.error
        else:
            # Add metadata if requested
            if self.include_metadata:
                report_data["authors"] = result.authors
                report_data["publication_date"] = (
                    result.publication_date.isoformat() 
                    if result.publication_date else None
                )
            
            # Add analysis results
            report_data["verdict"] = result.verdict
            
            # Add confidence scores if requested
            if self.include_confidence_scores:
                report_data["overall_scores"] = result.overall_scores
                report_data["section_scores"] = result.section_scores
            
            # Add issues
            report_data["issues"] = [
                {
                    "type": issue.issue_type,
                    "section": issue.section,
                    "score": issue.score,
                    "details": issue.details,
                    "evidence": issue.evidence
                }
                for issue in result.issues
            ]
            
            # Add recommendations if requested
            if self.include_recommendations and result.recommendations:
                report_data["recommendations"] = result.recommendations
        
        # Write report to file
        filename = f"{result.source}_{result.paper_id}.json"
        report_path = os.path.join(output_dir, filename)
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return report_path
    
    def _generate_html_report(
        self, 
        results: List[AnalysisResult], 
        summary: Dict[str, Any], 
        output_dir: str
    ) -> str:
        """
        Generate an HTML report.
        
        Args:
            results: List of analysis results
            summary: Summary data
            output_dir: Output directory
            
        Returns:
            Path to the generated HTML report
        """
        try:
            # Load template
            template = self.jinja_env.get_template("report.html")
            
            # Render HTML
            html_content = template.render(
                summary=summary,
                results=results,
                include_metadata=self.include_metadata,
                include_analysis_details=self.include_analysis_details,
                include_confidence_scores=self.include_confidence_scores,
                include_recommendations=self.include_recommendations,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Write to file
            html_path = os.path.join(output_dir, "report.html")
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            return html_path
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            
            # Fallback to a simple HTML report
            html_path = os.path.join(output_dir, "report_simple.html")
            with open(html_path, 'w') as f:
                f.write("<html><head><title>Academic Verifier Report</title></head><body>")
                f.write("<h1>Academic Verifier Report</h1>")
                f.write(f"<p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
                f.write(f"<p>Total papers analyzed: {len(results)}</p>")
                f.write("<h2>Summary</h2>")
                f.write("<pre>" + json.dumps(summary, indent=2) + "</pre>")
                f.write("</body></html>")
            
            return html_path
    
    def _generate_pdf_report(
        self, 
        results: List[AnalysisResult], 
        summary: Dict[str, Any], 
        output_dir: str
    ) -> str:
        """
        Generate a PDF report.
        
        Args:
            results: List of analysis results
            summary: Summary data
            output_dir: Output directory
            
        Returns:
            Path to the generated PDF report
        """
        # This is a placeholder for PDF generation
        # In a real implementation, this would use a library like WeasyPrint or ReportLab
        
        pdf_path = os.path.join(output_dir, "report.pdf")
        
        # For now, just create a placeholder file
        with open(pdf_path, 'w') as f:
            f.write("PDF Report placeholder")
        
        return pdf_path