"""
Sentence extraction module for finding the most relevant sentences within chunks.
"""

import re
import nltk
import numpy as np
from typing import List, Tuple
from nltk.tokenize import sent_tokenize

from .models import Chunk, ScoredSentence
from .embed_chunks import EmbeddingGenerator
from .config import TOP_M_SENTENCES


# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def extract_top_sentences(chunk: Chunk, query: str) -> List[ScoredSentence]:
    """
    Extract the top-scoring sentences from a chunk based on query relevance.
    
    Args:
        chunk: Chunk object to extract sentences from
        query: Query string for relevance scoring
        
    Returns:
        List of ScoredSentence objects, sorted by descending score
    """
    # Tokenize chunk into sentences
    sentences = sent_tokenize(chunk.text)
    
    # Clean and filter sentences
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20:  # Filter out very short sentences
            cleaned_sentences.append(sentence)
    
    if not cleaned_sentences:
        return []
    
    # Generate embeddings for sentences and query
    embedding_generator = EmbeddingGenerator()
    
    sentence_embeddings = embedding_generator.embed_sentences(cleaned_sentences)
    query_embedding = embedding_generator.embed_query(query)
    
    # Calculate cosine similarity scores
    scores = []
    for sentence_embedding in sentence_embeddings:
        similarity = np.dot(query_embedding, sentence_embedding)
        scores.append(float(similarity))
    
    # Create scored sentences
    scored_sentences = [
        ScoredSentence(text=sentence, score=score)
        for sentence, score in zip(cleaned_sentences, scores)
    ]
    
    # Sort by score and return top M
    scored_sentences.sort(key=lambda x: x.score, reverse=True)
    
    return scored_sentences[:TOP_M_SENTENCES]


def clean_sentence(sentence: str) -> str:
    """
    Clean a sentence by removing extra whitespace and fixing formatting.
    
    Args:
        sentence: Raw sentence string
        
    Returns:
        Cleaned sentence string
    """
    # Remove extra whitespace
    sentence = re.sub(r'\\s+', ' ', sentence)
    
    # Remove leading/trailing whitespace
    sentence = sentence.strip()
    
    # Fix common formatting issues
    sentence = re.sub(r'\\s+([.!?])', r'\\1', sentence)  # Fix spacing before punctuation
    sentence = re.sub(r'([.!?])\\s*([A-Z])', r'\\1 \\2', sentence)  # Fix spacing after punctuation
    
    return sentence


def extract_sentences_batch(chunks: List[Chunk], query: str) -> List[List[ScoredSentence]]:
    """
    Extract top sentences from multiple chunks efficiently.
    
    Args:
        chunks: List of Chunk objects
        query: Query string for relevance scoring
        
    Returns:
        List of lists containing ScoredSentence objects for each chunk
    """
    results = []
    
    # Initialize embedding generator once
    embedding_generator = EmbeddingGenerator()
    query_embedding = embedding_generator.embed_query(query)
    
    for chunk in chunks:
        # Tokenize chunk into sentences
        sentences = sent_tokenize(chunk.text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Filter out very short sentences
                cleaned_sentences.append(sentence)
        
        if not cleaned_sentences:
            results.append([])
            continue
        
        # Generate embeddings for sentences
        sentence_embeddings = embedding_generator.embed_sentences(cleaned_sentences)
        
        # Calculate cosine similarity scores
        scores = []
        for sentence_embedding in sentence_embeddings:
            similarity = np.dot(query_embedding, sentence_embedding)
            scores.append(float(similarity))
        
        # Create scored sentences
        scored_sentences = [
            ScoredSentence(text=sentence, score=score)
            for sentence, score in zip(cleaned_sentences, scores)
        ]
        
        # Sort by score and return top M
        scored_sentences.sort(key=lambda x: x.score, reverse=True)
        results.append(scored_sentences[:TOP_M_SENTENCES])
    
    return results