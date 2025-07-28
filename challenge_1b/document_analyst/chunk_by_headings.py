"""
Text chunking module based on heading detection.
"""

import re
from typing import List, Dict, Any, Optional
from .models import Document, Chunk
from .config import MIN_CHUNK_LENGTH, HEADING_FONT_THRESHOLD


def chunk_by_headings(docs: List[Document]) -> List[Chunk]:
    """
    Chunk documents by detecting headings using font size heuristics.
    
    Args:
        docs: List of Document objects
        
    Returns:
        List of Chunk objects
    """
    chunks = []
    
    for doc in docs:
        doc_chunks = chunk_single_document(doc)
        chunks.extend(doc_chunks)
    
    return chunks


def chunk_single_document(doc: Document) -> List[Chunk]:
    """
    Chunk a single document by detecting headings.
    
    Args:
        doc: Document object to chunk
        
    Returns:
        List of Chunk objects from the document
    """
    chunks = []
    
    # Find the most common font size (likely body text)
    font_info = doc.metadata.get("font_info", {})
    if not font_info:
        # Fallback: simple paragraph-based chunking
        return simple_paragraph_chunking(doc)
    
    # Determine base font size
    base_font_size = get_base_font_size(font_info)
    
    # Process page by page
    page_texts = doc.metadata.get("page_texts", [])
    
    current_chunk = ""
    current_section_title = None
    chunk_start_page = 1
    
    for page_num, page_text in enumerate(page_texts, 1):
        lines = page_text.split("\\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a heading
            if is_heading(line, base_font_size):
                # Save current chunk if it exists
                if current_chunk.strip() and len(current_chunk.strip()) >= MIN_CHUNK_LENGTH:
                    chunks.append(Chunk(
                        text=current_chunk.strip(),
                        source_doc=doc.filename,
                        start_page=chunk_start_page,
                        end_page=page_num,
                        section_title=current_section_title
                    ))
                
                # Start new chunk
                current_chunk = line + "\\n"
                current_section_title = line
                chunk_start_page = page_num
            else:
                current_chunk += line + "\\n"
    
    # Add final chunk
    if current_chunk.strip() and len(current_chunk.strip()) >= MIN_CHUNK_LENGTH:
        chunks.append(Chunk(
            text=current_chunk.strip(),
            source_doc=doc.filename,
            start_page=chunk_start_page,
            end_page=len(page_texts),
            section_title=current_section_title
        ))
    
    return chunks


def simple_paragraph_chunking(doc: Document) -> List[Chunk]:
    """
    Simple fallback chunking by paragraphs when font info is not available.
    
    Args:
        doc: Document to chunk
        
    Returns:
        List of chunks
    """
    chunks = []
    paragraphs = doc.text.split("\\n\\n")
    
    current_chunk = ""
    words_in_chunk = 0
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        paragraph_words = len(paragraph.split())
        
        # If adding this paragraph would exceed token limit, save current chunk
        if words_in_chunk + paragraph_words > 400:  # Rough token estimate
            if current_chunk.strip():
                chunks.append(Chunk(
                    text=current_chunk.strip(),
                    source_doc=doc.filename,
                    start_page=1,
                    end_page=doc.pages,
                    section_title=None
                ))
            
            current_chunk = paragraph + "\\n\\n"
            words_in_chunk = paragraph_words
        else:
            current_chunk += paragraph + "\\n\\n"
            words_in_chunk += paragraph_words
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(Chunk(
            text=current_chunk.strip(),
            source_doc=doc.filename,
            start_page=1,
            end_page=doc.pages,
            section_title=None
        ))
    
    return chunks


def get_base_font_size(font_info: Dict[str, Any]) -> float:
    """
    Determine the base font size (most common, likely body text).
    
    Args:
        font_info: Font information dictionary
        
    Returns:
        Base font size
    """
    if not font_info:
        return 12.0  # Default
    
    # Find the most common font size
    max_count = 0
    base_size = 12.0
    
    for font_key, info in font_info.items():
        if info["count"] > max_count:
            max_count = info["count"]
            base_size = info["size"]
    
    return base_size


def is_heading(text: str, base_font_size: float) -> bool:
    """
    Determine if a text line is likely a heading.
    
    Args:
        text: Text line to check
        base_font_size: Base font size for comparison
        
    Returns:
        True if likely a heading
    """
    # Simple heuristics for heading detection
    text = text.strip()
    
    # Check length (headings are usually shorter)
    if len(text.split()) > 15:
        return False
    
    # Check for common heading patterns
    heading_patterns = [
        r"^\\d+\\.\\s",  # 1. Introduction
        r"^\\d+\\.\\d+\\s",  # 1.1 Overview
        r"^[A-Z][A-Z\\s]+$",  # ALL CAPS
        r"^[A-Z][a-z].*:$",  # Title:
    ]
    
    for pattern in heading_patterns:
        if re.match(pattern, text):
            return True
    
    return False