"""
arXiv API Client

This module provides a client for interacting with the arXiv API to search for
and retrieve academic papers.
"""

import logging
import time
import re
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests

from ..models.paper import Paper

logger = logging.getLogger(__name__)

# XML namespaces used in arXiv API responses
NAMESPACES = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}


class ArxivClient:
    """
    Client for interacting with the arXiv API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the arXiv API client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.api_config = config.get("api", {}).get("arxiv", {})
        
        # Get API configuration
        self.base_url = self.api_config.get("base_url", "http://export.arxiv.org/api/query")
        self.timeout = self.api_config.get("timeout", 20)
        self.max_results = self.api_config.get("max_results", 100)
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Academic Verifier/1.0 (https://example.com/academic-verifier)"
        })
    
    def search_papers(
        self, 
        max_results: int = 100,
        date_range: int = 30,
        **kwargs
    ) -> List[str]:
        """
        Search for papers on arXiv.
        
        Args:
            max_results: Maximum number of results to return
            date_range: Date range in days
            **kwargs: Additional search parameters
                - categories: List of arXiv categories
                
        Returns:
            List of paper IDs
        """
        # Limit max_results to API limit
        max_results = min(max_results, self.max_results)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        
        # Build search query
        query_parts = []
        
        # Add date range
        query_parts.append(f"submittedDate:[{start_date.strftime('%Y%m%d')} TO {end_date.strftime('%Y%m%d')}]")
        
        # Add categories if provided
        categories = kwargs.get("categories", [])
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            query_parts.append(f"({cat_query})")
        
        # Combine query parts
        query = " AND ".join(query_parts)
        
        # Prepare request parameters
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        try:
            # Make request
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            root = ET.fromstring(response.content)
            
            # Extract paper IDs
            paper_ids = []
            for entry in root.findall(".//atom:entry", NAMESPACES):
                # Get arXiv ID
                id_element = entry.find("atom:id", NAMESPACES)
                if id_element is not None and id_element.text:
                    # Extract ID from URL (e.g., http://arxiv.org/abs/1234.5678 -> 1234.5678)
                    id_match = re.search(r"arxiv\.org/abs/([^/]+)$", id_element.text)
                    if id_match:
                        paper_ids.append(id_match.group(1))
            
            logger.info(f"Found {len(paper_ids)} papers on arXiv")
            return paper_ids
        
        except requests.exceptions.RequestException as e:
            logger.error(f"arXiv API request failed: {str(e)}")
            return []
        except ET.ParseError as e:
            logger.error(f"Failed to parse arXiv API response: {str(e)}")
            return []
    
    def get_paper(self, paper_id: str) -> Paper:
        """
        Get details of a specific paper.
        
        Args:
            paper_id: arXiv paper ID
            
        Returns:
            Paper object
        """
        # Prepare request parameters
        params = {
            "id_list": paper_id,
            "max_results": 1
        }
        
        try:
            # Make request
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            root = ET.fromstring(response.content)
            
            # Find entry
            entry = root.find(".//atom:entry", NAMESPACES)
            if entry is None:
                raise ValueError(f"Paper not found: {paper_id}")
            
            # Extract paper details
            title_element = entry.find("atom:title", NAMESPACES)
            title = title_element.text.strip() if title_element is not None else ""
            
            # Extract authors
            authors = []
            for author_element in entry.findall(".//atom:author/atom:name", NAMESPACES):
                if author_element.text:
                    authors.append(author_element.text.strip())
            
            # Extract abstract
            summary_element = entry.find("atom:summary", NAMESPACES)
            abstract = summary_element.text.strip() if summary_element is not None else ""
            
            # Extract publication date
            published_element = entry.find("atom:published", NAMESPACES)
            publication_date = None
            if published_element is not None and published_element.text:
                try:
                    publication_date = datetime.fromisoformat(published_element.text.replace("Z", "+00:00"))
                except ValueError:
                    logger.warning(f"Failed to parse publication date: {published_element.text}")
            
            # Extract URL
            url = f"https://arxiv.org/abs/{paper_id}"
            
            # Extract categories
            categories = []
            for category_element in entry.findall(".//arxiv:primary_category", NAMESPACES):
                category = category_element.get("term")
                if category:
                    categories.append(category)
            
            # Create Paper object
            paper = Paper(
                id=paper_id,
                source="arxiv",
                title=title,
                authors=authors,
                abstract=abstract,
                content=abstract,  # Use abstract as content (full text would require PDF parsing)
                publication_date=publication_date,
                url=url,
                keywords=categories,
                metadata={
                    "categories": categories
                }
            )
            
            return paper
        
        except requests.exceptions.RequestException as e:
            logger.error(f"arXiv API request failed: {str(e)}")
            raise
        except ET.ParseError as e:
            logger.error(f"Failed to parse arXiv API response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting paper from arXiv: {str(e)}")
            raise