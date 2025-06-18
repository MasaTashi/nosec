#!/usr/bin/env python3
"""
Basic test script for Academic Verifier.

This script demonstrates how to use the Academic Verifier to analyze academic papers
for AI-generated content, hallucinations, and misunderstandings.
"""

import os
import sys
import logging
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import load_config
from src.core.paper_collector import PaperCollector
from src.core.content_analyzer import ContentAnalyzer
from src.core.report_generator import ReportGenerator
from src.models.paper import Paper
from src.utils.logger import setup_logger


def main():
    """Run a basic test of the Academic Verifier."""
    # Setup logging
    logger = setup_logger(level=logging.INFO)
    logger.info("Starting Academic Verifier test")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    config = load_config(config_path)
    
    # Create test output directory
    output_dir = os.path.join(os.path.dirname(__file__), 'output', 
                             datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(output_dir, exist_ok=True)
    
    # Test with sample papers
    sample_papers = create_sample_papers()
    
    # Initialize components
    content_analyzer = ContentAnalyzer(config)
    report_generator = ReportGenerator(config)
    
    # Analyze papers
    logger.info(f"Analyzing {len(sample_papers)} sample papers")
    analysis_results = content_analyzer.analyze_batch(sample_papers)
    
    # Generate report
    logger.info("Generating report")
    report_path = report_generator.generate(analysis_results, output_dir=output_dir)
    
    logger.info(f"Test completed. Report generated at: {report_path}")
    logger.info(f"Summary: {len(analysis_results)} papers analyzed")
    
    # Print verdicts
    for result in analysis_results:
        logger.info(f"Paper: {result.title} - Verdict: {result.verdict}")
    
    return 0


def create_sample_papers():
    """Create sample papers for testing."""
    papers = []
    
    # Sample paper 1 - Legitimate paper
    papers.append(Paper(
        id="sample1",
        source="test",
        title="Advances in Natural Language Processing",
        authors=["John Smith", "Jane Doe"],
        abstract="This paper presents recent advances in natural language processing techniques.",
        content="""
        Abstract
        This paper presents recent advances in natural language processing techniques.
        
        Introduction
        Natural Language Processing (NLP) has seen significant advancements in recent years.
        These advancements have been driven by the development of new deep learning architectures
        and the availability of large datasets.
        
        Methodology
        We conducted experiments using transformer-based models on standard NLP benchmarks.
        Our approach involved fine-tuning pre-trained models on task-specific datasets.
        
        Results
        Our experiments show that transformer-based models outperform traditional methods
        on a variety of NLP tasks. We observed improvements of 5-10% on standard benchmarks.
        
        Discussion
        The results indicate that contextual representations are crucial for understanding
        natural language. However, these models require significant computational resources.
        
        Conclusion
        We have demonstrated the effectiveness of transformer-based models for NLP tasks.
        Future work should focus on improving efficiency and reducing computational requirements.
        
        References
        1. Vaswani et al. (2017). Attention is All You Need.
        2. Devlin et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
        """,
        publication_date=datetime(2023, 1, 15)
    ))
    
    # Sample paper 2 - Paper with AI-generated content
    papers.append(Paper(
        id="sample2",
        source="test",
        title="Quantum Computing Applications in Machine Learning",
        authors=["Alice Johnson", "Bob Williams"],
        abstract="This paper explores potential applications of quantum computing in machine learning.",
        content="""
        Abstract
        This paper explores potential applications of quantum computing in machine learning.
        
        Introduction
        Quantum computing offers the potential to solve certain computational problems more efficiently
        than classical computers. This has significant implications for machine learning algorithms,
        which often involve computationally intensive tasks.
        
        Quantum Machine Learning
        Quantum machine learning leverages quantum algorithms to enhance traditional machine learning approaches.
        Quantum computers can potentially provide exponential speedups for certain linear algebra operations,
        which are fundamental to many machine learning algorithms.
        
        The quantum support vector machine (QSVM) utilizes quantum computing to perform classification tasks
        with potentially exponential speedup compared to classical SVMs. Similarly, quantum neural networks
        (QNNs) use quantum circuits to implement neural network architectures.
        
        Experimental Results
        Our simulations show that QSVMs can achieve classification accuracy of 99.8% on the MNIST dataset,
        significantly outperforming classical SVMs which achieve only 97.2% accuracy. QNNs also demonstrate
        superior performance on image recognition tasks, with a 15% reduction in error rate.
        
        Discussion
        While our results are promising, it's important to note that current quantum hardware is still in
        its early stages. Noise and decoherence remain significant challenges for practical implementation.
        
        Conclusion
        Quantum machine learning shows great promise for revolutionizing the field of artificial intelligence.
        As quantum hardware continues to improve, we expect to see increasingly practical applications of
        these techniques.
        
        References
        1. Biamonte et al. (2017). Quantum Machine Learning.
        2. Schuld et al. (2019). Quantum Machine Learning in Feature Hilbert Spaces.
        """,
        publication_date=datetime(2023, 2, 20)
    ))
    
    # Sample paper 3 - Paper with hallucinations
    papers.append(Paper(
        id="sample3",
        source="test",
        title="Novel Approaches to Climate Change Mitigation",
        authors=["Carlos Rodriguez", "Maria Garcia"],
        abstract="This paper presents novel approaches to climate change mitigation.",
        content="""
        Abstract
        This paper presents novel approaches to climate change mitigation.
        
        Introduction
        Climate change represents one of the most significant challenges facing humanity.
        Effective mitigation strategies are essential to limit global warming and its impacts.
        
        Methodology
        We conducted a comprehensive review of climate mitigation technologies and policies.
        Additionally, we developed a new carbon capture system called HyperCapture-9000,
        which can remove CO2 from the atmosphere at rates 200 times faster than existing technologies.
        
        Results
        Our HyperCapture-9000 system demonstrated CO2 capture rates of 500 tons per day in
        laboratory conditions. Field tests in Arizona showed similar performance levels,
        with energy requirements of just 0.1 kWh per ton of CO2 captured.
        
        The system was successfully deployed in 15 countries between 2020-2022, resulting in
        a measurable 0.5°C reduction in global temperatures within just 18 months of operation.
        
        Discussion
        The unprecedented performance of the HyperCapture-9000 system challenges conventional
        understanding of carbon capture thermodynamics. We believe the efficiency stems from
        our proprietary catalyst, which has been verified by three independent laboratories.
        
        Conclusion
        The HyperCapture-9000 system represents a breakthrough in climate change mitigation.
        Wide deployment could reverse climate change within a decade, according to our models.
        
        References
        1. IPCC (2022). Sixth Assessment Report.
        2. Rodriguez et al. (2021). Theoretical Foundations of Advanced Carbon Capture.
        """,
        publication_date=datetime(2023, 3, 10)
    ))
    
    return papers


if __name__ == "__main__":
    sys.exit(main())