"""
Cache management for chat responses to reduce API token usage.
Uses similarity matching to find and reuse cached responses for similar queries.
"""

import logging
from typing import Optional, Tuple, Set
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import json
import re

logger = logging.getLogger(__name__)

class ResponseCache:
    """In-memory cache for chat responses with similarity matching."""
    
    def __init__(self, max_size: int = 100, ttl_hours: int = 24):
        """
        Initialize the response cache.
        
        Args:
            max_size: Maximum number of cached responses to store
            ttl_hours: Time-to-live for cached entries in hours
        """
        self.cache: list = []
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for better comparison."""
        return query.lower().strip()
    
    def _extract_key_terms(self, query: str) -> Set[str]:
        """
        Extract important keywords from query (e.g., 'bitcoin', 'binance', 'chart', etc).
        These are used to determine if queries are actually about the same topic.
        
        Args:
            query: The query string
            
        Returns:
            Set of important keywords
        """
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'for', 'is', 'are',
            'you', 'i', 'hello', 'want', 'create', 'make', 'do', 'please', 'can',
            'would', 'could', 'should', 'this', 'that', 'it', 'be', 'on', 'at'
        }
        
        # Keep only meaningful words
        key_terms = {word for word in words if word not in stop_words and len(word) > 2}
        return key_terms
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """
        Calculate similarity between two queries (0.0 to 1.0).
        
        Args:
            query1: First query
            query2: Second query
            
        Returns:
            Similarity score between 0 and 1
        """
        norm_query1 = self._normalize_query(query1)
        norm_query2 = self._normalize_query(query2)
        
        matcher = SequenceMatcher(None, norm_query1, norm_query2)
        return matcher.ratio()
    
    def _are_key_terms_different(self, query1: str, query2: str) -> bool:
        """
        Check if two queries have significantly different key terms.
        E.g., 'bitcoin' vs 'binance' should be considered different.
        
        Args:
            query1: First query
            query2: Second query
            
        Returns:
            True if key terms are significantly different, False otherwise
        """
        terms1 = self._extract_key_terms(query1)
        terms2 = self._extract_key_terms(query2)
        
        # If they have no terms in common, they're different
        common_terms = terms1 & terms2
        
        if not common_terms:
            return True
        
        # Calculate Jaccard similarity of terms
        union = terms1 | terms2
        if not union:
            return False
        
        jaccard = len(common_terms) / len(union)
        logger.debug(f"Key term comparison - Query1: {terms1}, Query2: {terms2}, Jaccard: {jaccard:.2%}")
        
        # If less than 40% of terms match, consider them different
        return jaccard < 0.4
    
    def find_similar(self, user_message: str, threshold: float = 0.75) -> Optional[dict]:
        """
        Find a cached response for a similar query.
        Uses intelligent matching to ensure consistent, standardized output formatting.
        
        Requirements for a match:
        1. String similarity >= threshold (75%)
        2. Key terms must be similar (not completely different topics)
        
        Args:
            user_message: Current user message
            threshold: Similarity threshold (0-1). Messages above this are considered similar.
                      Recommended: 0.75-0.85 for semantic similarity
            
        Returns:
            Cached response entry if similar one found, None otherwise.
            Guarantees consistent formatting if match is found.
        """
        logger.debug(f"   Searching cache for similar query. Threshold: {threshold}")
        logger.debug(f"   Query terms: {self._extract_key_terms(user_message)}")
        
        best_match = None
        best_similarity = 0
        
        for entry in self.cache:
            # Skip expired entries
            if self._is_expired(entry):
                continue
            
            similarity = self._calculate_similarity(user_message, entry['user_message'])
            
            # Check if key terms are different (e.g., bitcoin vs binance)
            if similarity >= threshold and self._are_key_terms_different(user_message, entry['user_message']):
                logger.debug(f"      Skipped due to different key terms")
                logger.debug(f"      Cached: {self._extract_key_terms(entry['user_message'])}")
                logger.debug(f"      Current: {self._extract_key_terms(user_message)}")
                continue
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = entry
        
        if best_match and best_similarity >= threshold:
            logger.info(f"   CACHE HIT - Returning consistent formatted output")
            logger.info(f"   Input Similarity: {best_similarity:.2%}")
            logger.info(f"   Original Query: '{best_match['user_message'][:80]}'")
            logger.info(f"   New Query: '{user_message[:80]}'")
            logger.info(f"   Format Type: {self._extract_format_type(best_match['html_content'])}")
            logger.info(f"   Reused: {best_match.get('access_count', 1)} times - Consistent output guaranteed!")
            return best_match
        
        logger.debug(f"❌ No similar cached query found (best similarity: {best_similarity:.2%})")
        return None
    
    def _extract_format_type(self, html_content: Optional[str]) -> str:
        """Extract the type of format being used (table, chart, form, etc)."""
        if not html_content:
            return "unknown"
        
        if "<table" in html_content:
            return "table"
        elif "<canvas" in html_content:
            return "chart"
        elif "<form" in html_content:
            return "form"
        elif "<div" in html_content:
            return "custom-layout"
        else:
            return "other"
    
    def _is_expired(self, entry: dict) -> bool:
        """Check if cache entry has expired."""
        timestamp = datetime.fromisoformat(entry['timestamp'])
        return datetime.now() > timestamp + self.ttl
    
    def add(self, user_message: str, bot_message: str, html_content: Optional[str]) -> None:
        """
        Add a new entry to the cache.
        
        Args:
            user_message: User's input message
            bot_message: Bot's response message
            html_content: Generated HTML content
        """
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size:
            self.cache.pop(0)
            logger.debug(f"Cache full. Removed oldest entry. Cache size: {len(self.cache)}")
        
        entry = {
            'user_message': user_message,
            'bot_message': bot_message,
            'html_content': html_content,
            'timestamp': datetime.now().isoformat(),
            'access_count': 1
        }
        
        self.cache.append(entry)
        logger.info(f"Added response to cache. Cache size: {len(self.cache)}")
    
    def update_access_count(self, entry: dict) -> None:
        """Update access count when a cached entry is reused."""
        if entry in self.cache:
            entry['access_count'] = entry.get('access_count', 1) + 1
            logger.info(f"CACHE HIT - Query: '{entry['user_message'][:80]}' - Access count: {entry['access_count']} - Tokens saved!")
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            'total_entries': len(self.cache),
            'max_size': self.max_size,
            'ttl_hours': self.ttl.total_seconds() / 3600,
            'entries': [
                {
                    'user_message': entry['user_message'][:100],
                    'access_count': entry.get('access_count', 1),
                    'timestamp': entry['timestamp']
                }
                for entry in self.cache
            ]
        }


# Global cache instance
response_cache = ResponseCache(max_size=100, ttl_hours=24)
