#!/usr/bin/env python3
"""
Academic Verifier - Main Application

This application automates the process of gathering academic papers and analyzing them
for potentially AI-generated content, hallucinations, or misunderstandings.
"""

import argparse
import logging
import os
import sys
from datetime import datetime

from config.settings import load_config
from core.paper_collector import PaperCollector
from core.content_analyzer import ContentAnalyzer
from core.report_generator import ReportGenerator
from utils.logger import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Academic Verifier - Detect AI-generated content in academic papers"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/config.yaml", 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output directory for reports"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--sources", 
        type=str, 
        nargs="+", 
        help="Specific sources to collect papers from"
    )
    return parser.parse_args()


def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(log_level)
    
    logger.info("Starting Academic Verifier")
    
    try:
        # Initialize components
        paper_collector = PaperCollector(config)
        content_analyzer = ContentAnalyzer(config)
        report_generator = ReportGenerator(config)
        
        # Set output directory
        output_dir = args.output or os.path.join(
            "data", 
            "reports", 
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        )
        os.makedirs(output_dir, exist_ok=True)
        
        # Collect papers
        sources = args.sources or config.get("sources", [])
        papers = paper_collector.collect(sources=sources)
        logger.info(f"Collected {len(papers)} papers for analysis")
        
        # Analyze papers
        analysis_results = content_analyzer.analyze_batch(papers)
        logger.info(f"Completed analysis of {len(analysis_results)} papers")
        
        # Generate reports
        report_path = report_generator.generate(
            analysis_results, 
            output_dir=output_dir
        )
        logger.info(f"Generated report at {report_path}")
        
        return 0
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())