"""
Paper Collector Module

This module is responsible for collecting academic papers from various sources
such as arXiv, PubMed, ScienceDirect, and Springer.
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..api.arxiv_client import ArxivClient
from ..api.pubmed_client import PubmedClient
from ..api.sciencedirect_client import ScienceDirectClient
from ..api.springer_client import SpringerClient
from ..models.paper import Paper
from ..utils.file_utils import save_paper, load_paper_metadata
from ..utils.cache import Cache

logger = logging.getLogger(__name__)


class PaperCollector:
    """
    Collects academic papers from various sources.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the paper collector.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.source_settings = config.get("source_settings", {})
        self.storage_config = config.get("storage", {})
        self.papers_dir = self.storage_config.get("papers_dir", "data/papers")
        
        # Initialize API clients
        self.clients = {
            "arxiv": ArxivClient(config),
            "pubmed": PubmedClient(config),
            "sciencedirect": ScienceDirectClient(config),
            "springer": SpringerClient(config)
        }
        
        # Initialize cache
        cache_dir = self.storage_config.get("cache_dir", "data/cache")
        cache_ttl = self.storage_config.get("cache_ttl", 604800)  # 7 days default
        self.cache = Cache(cache_dir, ttl=cache_ttl)
        
        # Ensure papers directory exists
        os.makedirs(self.papers_dir, exist_ok=True)
    
    def collect(self, sources: Optional[List[str]] = None) -> List[Paper]:
        """
        Collect papers from specified sources.
        
        Args:
            sources: List of sources to collect from. If None, uses all configured sources.
            
        Returns:
            List of collected papers
        """
        if not sources:
            sources = self.config.get("sources", [])
        
        logger.info(f"Collecting papers from sources: {sources}")
        
        all_papers = []
        
        # Use ThreadPoolExecutor for concurrent collection
        max_workers = min(len(sources), 4)  # Limit to 4 concurrent source collections
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {
                executor.submit(self._collect_from_source, source): source
                for source in sources if source in self.clients
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    papers = future.result()
                    logger.info(f"Collected {len(papers)} papers from {source}")
                    all_papers.extend(papers)
                except Exception as e:
                    logger.error(f"Error collecting papers from {source}: {str(e)}")
        
        logger.info(f"Total papers collected: {len(all_papers)}")
        return all_papers
    
    def _collect_from_source(self, source: str) -> List[Paper]:
        """
        Collect papers from a specific source.
        
        Args:
            source: Source name
            
        Returns:
            List of papers from the source
        """
        if source not in self.clients:
            logger.warning(f"Unknown source: {source}")
            return []
        
        # Get source-specific settings
        settings = self.source_settings.get(source, {})
        max_papers = settings.get("max_papers", 100)
        date_range = settings.get("date_range", 30)  # days
        
        # Check cache first
        cache_key = f"papers_{source}_{date_range}_{max_papers}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info(f"Using cached data for {source}")
            paper_ids = cached_data
        else:
            # Fetch paper IDs from source
            client = self.clients[source]
            paper_ids = client.search_papers(
                max_results=max_papers,
                date_range=date_range,
                **settings
            )
            
            # Cache the results
            self.cache.set(cache_key, paper_ids)
        
        # Fetch full papers
        papers = []
        for paper_id in paper_ids:
            try:
                # Check if we already have this paper
                paper_path = os.path.join(self.papers_dir, f"{source}_{paper_id}.json")
                if os.path.exists(paper_path):
                    paper = load_paper_metadata(paper_path)
                    papers.append(paper)
                    continue
                
                # Fetch paper details
                paper = self.clients[source].get_paper(paper_id)
                
                # Save paper to disk
                save_paper(paper, self.papers_dir)
                
                papers.append(paper)
                
                # Small delay to avoid overwhelming APIs
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error fetching paper {paper_id} from {source}: {str(e)}")
        
        return papers