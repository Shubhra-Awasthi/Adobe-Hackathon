"""
Recall stage module for retrieving candidate chunks.
"""

import faiss
import numpy as np
from typing import List

from .models import Chunk
from .embed_chunks import EmbeddingGenerator
from .build_index import search_index
from .config import TOP_K_CANDIDATES


def recall_candidates(query: str, index: faiss.Index, chunks: List[Chunk]) -> List[Chunk]:
    """
    Recall top-k candidate chunks using FAISS similarity search.
    
    Args:
        query: Combined persona + job_to_be_done query string
        index: FAISS index for similarity search
        chunks: List of all available chunks
        
    Returns:
        List of top-k candidate chunks
    """
    if not chunks:
        return []
    
    # Generate query embedding
    embedding_generator = EmbeddingGenerator()
    query_embedding = embedding_generator.embed_query(query)
    
    # Search for top candidates
    k = min(TOP_K_CANDIDATES, len(chunks))
    scores, indices = search_index(index, query_embedding, k)
    
    # Return candidate chunks
    candidates = []
    for i, idx in enumerate(indices):
        if idx < len(chunks):  # Safety check
            candidates.append(chunks[idx])
    
    print(f"Recalled {len(candidates)} candidate chunks")
    return candidates


def create_query_string(persona: dict, job_to_be_done: str) -> str:
    """
    Create a combined query string from persona and job description.
    
    Args:
        persona: Persona dictionary containing user context
        job_to_be_done: Job description string
        
    Returns:
        Combined query string
    """
    # Extract key information from persona
    persona_parts = []
    
    if isinstance(persona, dict):
        for key, value in persona.items():
            if value and str(value).strip():
                persona_parts.append(f"{key}: {value}")
    
    # Combine persona and job
    query_parts = []
    
    if persona_parts:
        query_parts.append("User context: " + "; ".join(persona_parts))
    
    if job_to_be_done and job_to_be_done.strip():
        query_parts.append(f"Task: {job_to_be_done}")
    
    return " ".join(query_parts)