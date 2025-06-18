"""
TRSHR API Client

This module provides a client for interacting with the TRSHR API, which is used
for analyzing academic papers for AI-generated content, hallucinations, and
misunderstandings.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
import requests

from ..config.settings import get_api_key

logger = logging.getLogger(__name__)


class TRSHRClient:
    """
    Client for interacting with the TRSHR API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the TRSHR API client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.api_config = config.get("api", {}).get("trshr", {})
        
        # Get API key
        self.api_key = get_api_key("trshr", config)
        if not self.api_key:
            raise ValueError("TRSHR API key is required")
        
        # Get API configuration
        self.base_url = self.api_config.get("base_url", "https://api.trshr.io/v1")
        self.timeout = self.api_config.get("timeout", 30)
        self.max_retries = self.api_config.get("max_retries", 3)
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def analyze_text(
        self, 
        text: str, 
        model: str = "trshr-academic-v2",
        features: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Analyze text for AI-generated content, hallucinations, and misunderstandings.
        
        Args:
            text: Text to analyze
            model: Model to use for analysis
            features: Features to enable/disable
            
        Returns:
            Analysis results
        """
        if not text:
            logger.warning("Empty text provided for analysis")
            return {
                "ai_generated_score": 0.0,
                "hallucination_score": 0.0,
                "misunderstanding_score": 0.0,
                "identified_issues": []
            }
        
        # Set default features if not provided
        if features is None:
            features = {
                "citation_check": True,
                "methodology_analysis": True,
                "statistical_validation": True,
                "reference_verification": True,
                "cross_paper_comparison": False
            }
        
        # Prepare request data
        data = {
            "text": text,
            "model": model,
            "features": features
        }
        
        # Send request with retries
        for attempt in range(self.max_retries):
            try:
                response = self._make_request("POST", "/analyze", data)
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to analyze text after {self.max_retries} attempts")
                    raise
        
        # This should not be reached, but just in case
        raise RuntimeError("Failed to analyze text")
    
    def batch_analyze(
        self, 
        texts: List[str], 
        model: str = "trshr-academic-v2",
        features: Optional[Dict[str, bool]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple texts in a batch.
        
        Args:
            texts: List of texts to analyze
            model: Model to use for analysis
            features: Features to enable/disable
            
        Returns:
            List of analysis results
        """
        if not texts:
            logger.warning("Empty list of texts provided for batch analysis")
            return []
        
        # Set default features if not provided
        if features is None:
            features = {
                "citation_check": True,
                "methodology_analysis": True,
                "statistical_validation": True,
                "reference_verification": True,
                "cross_paper_comparison": True
            }
        
        # Prepare request data
        data = {
            "texts": texts,
            "model": model,
            "features": features
        }
        
        # Send request with retries
        for attempt in range(self.max_retries):
            try:
                response = self._make_request("POST", "/batch-analyze", data)
                return response.get("results", [])
            except requests.exceptions.RequestException as e:
                logger.warning(f"Batch request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to batch analyze texts after {self.max_retries} attempts")
                    raise
        
        # This should not be reached, but just in case
        raise RuntimeError("Failed to batch analyze texts")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models.
        
        Returns:
            List of available models
        """
        try:
            response = self._make_request("GET", "/models")
            return response.get("models", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get models: {str(e)}")
            return []
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the TRSHR API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=self.timeout)
            elif method == "POST":
                response = self.session.post(
                    url, 
                    data=json.dumps(data) if data else None,
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise