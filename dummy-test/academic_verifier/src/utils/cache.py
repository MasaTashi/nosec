"""
Cache Module

This module provides a simple caching mechanism for storing and retrieving data.
"""

import os
import json
import time
import logging
import hashlib
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)


class Cache:
    """
    Simple file-based cache for storing and retrieving data.
    """
    
    def __init__(self, cache_dir: str, ttl: int = 86400):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl: Time-to-live in seconds (default: 1 day)
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        cache_file = self._get_cache_file(key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            # Check if cache is expired
            mtime = os.path.getmtime(cache_file)
            if time.time() - mtime > self.ttl:
                logger.debug(f"Cache expired for key: {key}")
                return None
            
            # Read cache file
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            logger.debug(f"Cache hit for key: {key}")
            return cache_data.get("value")
        except Exception as e:
            logger.warning(f"Failed to read cache for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_file = self._get_cache_file(key)
        
        try:
            # Create cache data
            cache_data = {
                "key": key,
                "value": value,
                "timestamp": time.time()
            }
            
            # Write to cache file
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            logger.debug(f"Cached value for key: {key}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache value for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        cache_file = self._get_cache_file(key)
        
        if not os.path.exists(cache_file):
            return True
        
        try:
            os.remove(cache_file)
            logger.debug(f"Deleted cache for key: {key}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete cache for key {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all cached values.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            logger.debug("Cleared cache")
            return True
        except Exception as e:
            logger.warning(f"Failed to clear cache: {str(e)}")
            return False
    
    def clear_expired(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        cleared_count = 0
        
        try:
            current_time = time.time()
            
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                
                if os.path.isfile(file_path):
                    # Check if cache is expired
                    mtime = os.path.getmtime(file_path)
                    if current_time - mtime > self.ttl:
                        os.remove(file_path)
                        cleared_count += 1
            
            logger.debug(f"Cleared {cleared_count} expired cache entries")
            return cleared_count
        except Exception as e:
            logger.warning(f"Failed to clear expired cache entries: {str(e)}")
            return cleared_count
    
    def _get_cache_file(self, key: str) -> str:
        """
        Get the cache file path for a key.
        
        Args:
            key: Cache key
            
        Returns:
            Cache file path
        """
        # Hash the key to create a filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.json")


# Memory cache for in-memory caching
_memory_cache: Dict[str, Dict[str, Any]] = {}


def cache_in_memory(key: str, ttl: int = 300) -> Any:
    """
    Decorator for caching function results in memory.
    
    Args:
        key: Cache key prefix
        ttl: Time-to-live in seconds (default: 5 minutes)
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create a unique key based on function arguments
            arg_str = str(args) + str(sorted(kwargs.items()))
            cache_key = f"{key}_{hashlib.md5(arg_str.encode()).hexdigest()}"
            
            # Check if result is in cache and not expired
            if cache_key in _memory_cache:
                cache_entry = _memory_cache[cache_key]
                if time.time() - cache_entry["timestamp"] < ttl:
                    logger.debug(f"Memory cache hit for key: {cache_key}")
                    return cache_entry["value"]
            
            # Call the function
            result = func(*args, **kwargs)
            
            # Cache the result
            _memory_cache[cache_key] = {
                "value": result,
                "timestamp": time.time()
            }
            
            logger.debug(f"Cached result in memory for key: {cache_key}")
            return result
        
        return wrapper
    
    return decorator


def clear_memory_cache() -> None:
    """
    Clear the memory cache.
    """
    global _memory_cache
    _memory_cache = {}
    logger.debug("Cleared memory cache")


def clear_expired_memory_cache() -> int:
    """
    Clear expired entries from the memory cache.
    
    Returns:
        Number of entries cleared
    """
    global _memory_cache
    
    current_time = time.time()
    keys_to_delete = []
    
    for key, cache_entry in _memory_cache.items():
        ttl = cache_entry.get("ttl", 300)  # Default TTL: 5 minutes
        if current_time - cache_entry["timestamp"] > ttl:
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del _memory_cache[key]
    
    logger.debug(f"Cleared {len(keys_to_delete)} expired memory cache entries")
    return len(keys_to_delete)