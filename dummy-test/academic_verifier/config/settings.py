"""
Configuration settings module for Academic Verifier.

This module handles loading and validating configuration from YAML files.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    "api": {
        "trshr": {
            "key": "trr_Y7vrG9F6xY9Dsj6hNumNfa1AauLxyfRSxyGDmd5cQtiq8Apfd9LJvHmewt",
            "base_url": "https://api.trshr.io/v1",
            "timeout": 30,
            "max_retries": 3
        }
    },
    "sources": [
        "arxiv",
        "pubmed",
        "sciencedirect",
        "springer"
    ],
    "analysis": {
        "models": {
            "primary": "trshr-academic-v2",
            "fallback": "trshr-standard-v1"
        },
        "thresholds": {
            "ai_generated": 0.85,
            "hallucination": 0.75,
            "misunderstanding": 0.65
        },
        "batch_size": 10,
        "max_concurrent": 5
    },
    "storage": {
        "papers_dir": "data/papers",
        "cache_dir": "data/cache",
        "reports_dir": "data/reports"
    },
    "logging": {
        "level": "INFO",
        "file": "logs/academic_verifier.log",
        "max_size": 10485760,  # 10 MB
        "backup_count": 5
    }
}


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing the merged configuration
    """
    config = DEFAULT_CONFIG.copy()
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                
            if user_config:
                # Merge user configuration with defaults
                _deep_merge(config, user_config)
                logger.info(f"Loaded configuration from {config_path}")
            else:
                logger.warning(f"Empty configuration file: {config_path}")
        else:
            logger.warning(f"Configuration file not found: {config_path}")
            logger.info("Using default configuration")
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        logger.info("Using default configuration")
    
    # Ensure required directories exist
    _ensure_directories(config)
    
    return config


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    """
    Deep merge two dictionaries, modifying the base dictionary in-place.
    
    Args:
        base: Base dictionary to merge into
        override: Dictionary with values to override
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def _ensure_directories(config: Dict[str, Any]) -> None:
    """
    Ensure that directories specified in the configuration exist.
    
    Args:
        config: Configuration dictionary
    """
    dirs_to_create = []
    
    # Add storage directories
    storage = config.get("storage", {})
    for dir_key in ["papers_dir", "cache_dir", "reports_dir"]:
        if dir_key in storage:
            dirs_to_create.append(storage[dir_key])
    
    # Add log directory
    log_config = config.get("logging", {})
    if "file" in log_config:
        log_dir = os.path.dirname(log_config["file"])
        if log_dir:
            dirs_to_create.append(log_dir)
    
    # Create directories
    for directory in dirs_to_create:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to create directory {directory}: {str(e)}")


def get_api_key(service: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    Get API key for a specific service.
    
    Args:
        service: Service name (e.g., 'trshr')
        config: Configuration dictionary (optional)
        
    Returns:
        API key as string
    """
    if config is None:
        config = load_config("config/config.yaml")
    
    # Try to get from config
    api_config = config.get("api", {}).get(service, {})
    api_key = api_config.get("key")
    
    # Try to get from environment
    if not api_key:
        env_var = f"{service.upper()}_API_KEY"
        api_key = os.environ.get(env_var)
    
    if not api_key:
        logger.warning(f"No API key found for service: {service}")
    
    return api_key