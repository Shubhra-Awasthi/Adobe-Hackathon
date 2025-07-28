"""
FAISS index building module for efficient similarity search.
"""

import faiss
import numpy as np
from typing import List

from .models import Chunk


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Build a FAISS index for efficient similarity search.
    
    Args:
        embeddings: Normalized embedding matrix (n_chunks x embedding_dim)
        
    Returns:
        FAISS index ready for search
    """
    if embeddings.size == 0:
        raise ValueError("Cannot build index with empty embeddings")
    
    # Get embedding dimension
    embedding_dim = embeddings.shape[1]
    
    # Create FAISS index for inner product (cosine similarity on normalized vectors)
    index = faiss.IndexFlatIP(embedding_dim)
    
    # Add embeddings to index
    index.add(embeddings.astype(np.float32))
    
    print(f"Built FAISS index with {index.ntotal} vectors of dimension {embedding_dim}")
    
    return index


def search_index(index: faiss.Index, query_embedding: np.ndarray, k: int) -> tuple:
    """
    Search the FAISS index for top-k similar vectors.
    
    Args:
        index: FAISS index to search
        query_embedding: Query embedding vector
        k: Number of top results to return
        
    Returns:
        Tuple of (scores, indices) arrays
    """
    # Ensure query is 2D and float32
    query = query_embedding.reshape(1, -1).astype(np.float32)
    
    # Search index
    scores, indices = index.search(query, k)
    
    return scores[0], indices[0]  # Return 1D arrays