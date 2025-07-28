"""
Embedding generation module using sentence transformers.
"""

import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from .models import Chunk
from .config import BI_ENCODER_MODEL, BATCH_SIZE


class EmbeddingGenerator:
    """Handles embedding generation for text chunks."""
    
    def __init__(self):
        """Initialize the embedding model."""
        print(f"Loading bi-encoder model: {BI_ENCODER_MODEL}")
        self.model = SentenceTransformer(BI_ENCODER_MODEL)
        
    def embed_chunks(self, chunks: List[Chunk]) -> np.ndarray:
        """
        Generate embeddings for a list of chunks.
        
        Args:
            chunks: List of Chunk objects to embed
            
        Returns:
            Normalized embedding matrix (n_chunks x embedding_dim)
        """
        if not chunks:
            return np.array([])
        
        # Extract text from chunks
        texts = [chunk.text for chunk in chunks]
        
        # Generate embeddings in batches
        embeddings = []
        
        for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Generating embeddings"):
            batch_texts = texts[i:i + BATCH_SIZE]
            batch_embeddings = self.model.encode(
                batch_texts,
                batch_size=BATCH_SIZE,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            embeddings.append(batch_embeddings)
        
        # Concatenate all embeddings
        all_embeddings = np.vstack(embeddings)
        
        # Normalize embeddings for cosine similarity
        embeddings_normalized = all_embeddings / np.linalg.norm(all_embeddings, axis=1, keepdims=True)
        
        return embeddings_normalized
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query string.
        
        Args:
            query: Query string to embed
            
        Returns:
            Normalized query embedding
        """
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        query_normalized = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        return query_normalized[0]
    
    def embed_sentences(self, sentences: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of sentences.
        
        Args:
            sentences: List of sentence strings
            
        Returns:
            Normalized sentence embeddings
        """
        if not sentences:
            return np.array([])
        
        sentence_embeddings = self.model.encode(
            sentences,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Normalize embeddings
        embeddings_normalized = sentence_embeddings / np.linalg.norm(sentence_embeddings, axis=1, keepdims=True)
        
        return embeddings_normalized


def embed_chunks(chunks: List[Chunk]) -> np.ndarray:
    """
    Convenience function to generate embeddings for chunks.
    
    Args:
        chunks: List of Chunk objects
        
    Returns:
        Normalized embedding matrix
    """
    generator = EmbeddingGenerator()
    return generator.embed_chunks(chunks)