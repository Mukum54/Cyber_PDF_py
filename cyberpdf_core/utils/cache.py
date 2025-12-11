"""
Caching system for thumbnails and operation results
"""
from pathlib import Path
from typing import Optional, Any, Dict
import time
import pickle
import hashlib
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class LRUCache:
    """Least Recently Used cache implementation"""
    
    def __init__(self, maxsize: int = 500):
        """
        Initialize LRU cache
        
        Args:
            maxsize: Maximum number of items to cache
        """
        self.cache: OrderedDict = OrderedDict()
        self.maxsize = maxsize
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key not in self.cache:
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache"""
        if key in self.cache:
            # Update existing item
            self.cache.move_to_end(key)
        else:
            # Add new item
            if len(self.cache) >= self.maxsize:
                # Remove oldest item
                self.cache.popitem(last=False)
        
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear all cached items"""
        self.cache.clear()
    
    def __len__(self) -> int:
        return len(self.cache)


class CacheManager:
    """Intelligent caching system for thumbnails and operation results"""
    
    def __init__(self, cache_dir: str = "/tmp/cyberpdf"):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory for disk cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory caches
        self.thumbnail_cache = LRUCache(maxsize=500)
        self.result_cache: Dict[str, Any] = {}
        
        logger.info(f"Initialized CacheManager with cache_dir: {cache_dir}")
    
    def get_thumbnail(self, pdf_path: str, page_num: int, size: int = 200) -> Optional[str]:
        """
        Get cached thumbnail or return None
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number
            size: Thumbnail size
        
        Returns:
            Path to thumbnail or None if not cached
        """
        cache_key = self._generate_cache_key(pdf_path, page_num, size)
        
        # Check memory cache first
        cached_path = self.thumbnail_cache.get(cache_key)
        if cached_path and Path(cached_path).exists():
            return cached_path
        
        # Check disk cache
        thumbnail_path = self.cache_dir / f"{cache_key}.jpg"
        if thumbnail_path.exists():
            self.thumbnail_cache.put(cache_key, str(thumbnail_path))
            return str(thumbnail_path)
        
        return None
    
    def cache_thumbnail(self, pdf_path: str, page_num: int, thumbnail_path: str, size: int = 200) -> None:
        """
        Cache thumbnail path
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number
            thumbnail_path: Path to thumbnail image
            size: Thumbnail size
        """
        cache_key = self._generate_cache_key(pdf_path, page_num, size)
        self.thumbnail_cache.put(cache_key, thumbnail_path)
    
    def cache_operation_result(self, operation_id: str, result: Any) -> None:
        """
        Cache operation result
        
        Args:
            operation_id: Unique operation identifier
            result: Result to cache
        """
        cache_file = self.cache_dir / f"result_{operation_id}.pkl"
        
        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
        
        self.result_cache[operation_id] = result
        logger.debug(f"Cached operation result: {operation_id}")
    
    def get_operation_result(self, operation_id: str) -> Optional[Any]:
        """
        Get cached operation result
        
        Args:
            operation_id: Unique operation identifier
        
        Returns:
            Cached result or None
        """
        # Check memory cache
        if operation_id in self.result_cache:
            return self.result_cache[operation_id]
        
        # Check disk cache
        cache_file = self.cache_dir / f"result_{operation_id}.pkl"
        if cache_file.exists():
            with open(cache_file, "rb") as f:
                result = pickle.load(f)
            
            self.result_cache[operation_id] = result
            return result
        
        return None
    
    def cleanup_old_cache(self, max_age_hours: int = 24) -> int:
        """
        Remove old cache files
        
        Args:
            max_age_hours: Maximum age of cache files in hours
        
        Returns:
            Number of files removed
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        removed_count = 0
        
        for cache_file in self.cache_dir.glob("*"):
            if cache_file.is_file():
                file_age = current_time - cache_file.stat().st_mtime
                
                if file_age > max_age_seconds:
                    cache_file.unlink()
                    removed_count += 1
        
        logger.info(f"Cleaned up {removed_count} old cache files")
        return removed_count
    
    def clear_all(self) -> None:
        """Clear all caches (memory and disk)"""
        # Clear memory caches
        self.thumbnail_cache.clear()
        self.result_cache.clear()
        
        # Clear disk cache
        for cache_file in self.cache_dir.glob("*"):
            if cache_file.is_file():
                cache_file.unlink()
        
        logger.info("Cleared all caches")
    
    def get_cache_size(self) -> Dict[str, int]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache size information
        """
        disk_size = sum(f.stat().st_size for f in self.cache_dir.glob("*") if f.is_file())
        
        return {
            "memory_items": len(self.thumbnail_cache) + len(self.result_cache),
            "disk_files": len(list(self.cache_dir.glob("*"))),
            "disk_size_mb": disk_size / (1024 * 1024),
        }
    
    @staticmethod
    def _generate_cache_key(pdf_path: str, page_num: int, size: int) -> str:
        """Generate unique cache key"""
        key_string = f"{pdf_path}_{page_num}_{size}"
        return hashlib.md5(key_string.encode()).hexdigest()


# Global cache manager instance
cache_manager = CacheManager()
