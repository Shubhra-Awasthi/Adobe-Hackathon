"""
Reranking module using cross-encoder for improved precision.
"""

import numpy as np
from typing import List, Tuple
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm

from .models import Chunk
from .config import CROSS_ENCODER_MODEL, BATCH_SIZE


class CrossEncoderReranker:
    """Handles cross-encoder reranking for improved precision."""
    
    def __init__(self):
        """Initialize the cross-encoder model."""
        print(f"Loading cross-encoder model: {CROSS_ENCODER_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(CROSS_ENCODER_MODEL)
        self.model = AutoModelForSequenceClassification.from_pretrained(CROSS_ENCODER_MODEL)
        self.model.eval()
        
    def rerank_candidates(self, query: str, candidates: List[Chunk]) -> List[Tuple[Chunk, float]]:
        """
        Rerank candidate chunks using cross-encoder scoring.
        
        Args:
            query: Query string
            candidates: List of candidate chunks
            
        Returns:
            List of (chunk, score) tuples sorted by descending score
        """
        if not candidates:
            return []
        
        # Prepare input pairs
        pairs = []
        for candidate in candidates:
            pairs.append([query, candidate.text])
        
        # Score in batches
        scores = []
        
        for i in tqdm(range(0, len(pairs), BATCH_SIZE), desc="Reranking with cross-encoder"):
            batch_pairs = pairs[i:i + BATCH_SIZE]
            batch_scores = self._score_batch(batch_pairs)
            scores.extend(batch_scores)
        
        # Combine chunks with scores and sort
        chunk_scores = list(zip(candidates, scores))
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        
        print(f"Reranked {len(chunk_scores)} candidates")
        return chunk_scores
    
    def _score_batch(self, pairs: List[List[str]]) -> List[float]:
        """
        Score a batch of query-chunk pairs.
        
        Args:
            pairs: List of [query, chunk] pairs
            
        Returns:
            List of relevance scores
        """
        # Tokenize pairs
        inputs = self.tokenizer(
            pairs,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            
            # Convert to probabilities or use raw logits
            if logits.shape[1] == 1:
                # Single score output
                scores = logits.squeeze().cpu().numpy()
            else:
                # Classification output, use positive class probability
                scores = torch.softmax(logits, dim=1)[:, 1].cpu().numpy()
        
        # Ensure scores is iterable
        if isinstance(scores, np.ndarray):
            if scores.ndim == 0:
                scores = [float(scores)]
            else:
                scores = scores.tolist()
        
        return scores


def rerank_candidates(query: str, candidates: List[Chunk]) -> List[Tuple[Chunk, float]]:
    """
    Convenience function to rerank candidate chunks.
    
    Args:
        query: Query string
        candidates: List of candidate chunks
        
    Returns:
        List of (chunk, score) tuples sorted by descending score
    """
    reranker = CrossEncoderReranker()
    return reranker.rerank_candidates(query, candidates)