"""
File Utilities Module

This module provides utilities for file operations.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.paper import Paper

logger = logging.getLogger(__name__)


def ensure_directory(directory: str) -> bool:
    """
    Ensure that a directory exists.
    
    Args:
        directory: Directory path
        
    Returns:
        True if the directory exists or was created, False otherwise
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {str(e)}")
        return False


def save_paper(paper: Paper, directory: str) -> str:
    """
    Save a paper to a JSON file.
    
    Args:
        paper: Paper to save
        directory: Directory to save the paper in
        
    Returns:
        Path to the saved file
    """
    # Ensure directory exists
    ensure_directory(directory)
    
    # Create filename
    filename = f"{paper.source}_{paper.id}.json"
    file_path = os.path.join(directory, filename)
    
    try:
        # Convert paper to dictionary
        paper_dict = paper.to_dict()
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(paper_dict, f, indent=2)
        
        logger.debug(f"Saved paper to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to save paper to {file_path}: {str(e)}")
        raise


def load_paper(file_path: str) -> Paper:
    """
    Load a paper from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Paper object
    """
    try:
        with open(file_path, 'r') as f:
            paper_dict = json.load(f)
        
        # Create Paper object
        paper = Paper.from_dict(paper_dict)
        
        logger.debug(f"Loaded paper from {file_path}")
        return paper
    except Exception as e:
        logger.error(f"Failed to load paper from {file_path}: {str(e)}")
        raise


def load_paper_metadata(file_path: str) -> Paper:
    """
    Load paper metadata from a JSON file without loading the full content.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Paper object with metadata
    """
    try:
        with open(file_path, 'r') as f:
            paper_dict = json.load(f)
        
        # Remove content to save memory
        paper_dict.pop("content", None)
        
        # Create Paper object
        paper = Paper.from_dict(paper_dict)
        
        logger.debug(f"Loaded paper metadata from {file_path}")
        return paper
    except Exception as e:
        logger.error(f"Failed to load paper metadata from {file_path}: {str(e)}")
        raise


def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory(directory)
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.debug(f"Saved JSON data to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON data to {file_path}: {str(e)}")
        return False


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded data or None if loading failed
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        logger.debug(f"Loaded JSON data from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON data from {file_path}: {str(e)}")
        return None


def get_file_age(file_path: str) -> Optional[float]:
    """
    Get the age of a file in seconds.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Age in seconds or None if the file doesn't exist
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        # Get file modification time
        mtime = os.path.getmtime(file_path)
        
        # Calculate age
        age = datetime.now().timestamp() - mtime
        
        return age
    except Exception as e:
        logger.error(f"Failed to get age of file {file_path}: {str(e)}")
        return None


def list_files(directory: str, extension: Optional[str] = None) -> list:
    """
    List files in a directory.
    
    Args:
        directory: Directory path
        extension: File extension filter (optional)
        
    Returns:
        List of file paths
    """
    try:
        if not os.path.exists(directory):
            logger.warning(f"Directory does not exist: {directory}")
            return []
        
        files = []
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Apply extension filter
            if extension and not filename.endswith(extension):
                continue
            
            files.append(file_path)
        
        return files
    except Exception as e:
        logger.error(f"Failed to list files in {directory}: {str(e)}")
        return []