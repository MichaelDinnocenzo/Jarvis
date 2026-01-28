import logging
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from api_client import get_api_client
from cache import get_cache_manager
from utils import retry, measure_time
from metrics import get_metrics
from exceptions import APIError

logger = logging.getLogger(__name__)
cache = get_cache_manager()
metrics = get_metrics()

class EmbeddingManager:
    """Manage semantic embeddings."""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        self.api_client = get_api_client()
        self.model = model
        self.embeddings_cache = {}
        self.vectors: List[Tuple[str, List[float]]] = []
        self.embedding_count = 0
        
    @retry(max_attempts=2, delay=1.0)
    @measure_time
    def embed(self, text: str) -> List[float]:
        """Create embedding for text."""
        cache_key = f"embed_{text[:50]}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            embedding = self.api_client.create_embedding(text, self.model)
            cache.set(cache_key, embedding)
            self.embedding_count += 1
            metrics.increment_counter("embeddings")
            logger.info(f"Embedded: {text[:40]}...")
            return embedding
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise APIError(f"Embedding failed: {e}")
    
    def semantic_search(self, query: str, candidates: List[str], top_k: int = 3) -> List[Tuple[str, float]]:
        """Find semantically similar texts."""
        try:
            query_embedding = self.embed(query)
            
            results = []
            for candidate in candidates:
                candidate_embedding = self.embed(candidate)
                similarity = self._cosine_similarity(query_embedding, candidate_embedding)
                results.append((candidate, similarity))
            
            results.sort(key=lambda x: x[1], reverse=True)
            logger.info(f"Found {len(results)} semantic matches")
            return results[:top_k]
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def add_vector(self, text: str, metadata: Optional[Dict] = None):
        """Add vector with metadata."""
        try:
            embedding = self.embed(text)
            self.vectors.append((text, embedding))
            logger.info(f"Added vector (total: {len(self.vectors)})")
        except Exception as e:
            logger.error(f"Failed to add vector: {e}")
    
    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity."""
        if not a or not b:
            return 0.0
        try:
            a_arr = np.array(a)
            b_arr = np.array(b)
            return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def get_stats(self) -> Dict:
        """Get embedding statistics."""
        return {
            "embeddings_created": self.embedding_count,
            "vectors_stored": len(self.vectors),
            "cache_size": len(self.embeddings_cache)
        }
