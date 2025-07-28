"""
PDF loading and text extraction module.
"""

import fitz  # PyMuPDF
import os
from typing import List, Dict, Any
from tqdm import tqdm

from .models import Document


def load_pdfs(pdf_paths: List[str]) -> List[Document]:
    """
    Load PDF files and extract text content with metadata.
    
    Args:
        pdf_paths: List of paths to PDF files
        
    Returns:
        List of Document objects containing extracted text and metadata
    """
    documents = []
    
    for pdf_path in tqdm(pdf_paths, desc="Loading PDFs"):
        try:
            doc = load_single_pdf(pdf_path)
            documents.append(doc)
        except Exception as e:
            print(f"Error loading {pdf_path}: {e}")
            continue
    
    return documents


def load_single_pdf(pdf_path: str) -> Document:
    """
    Load a single PDF file and extract text with metadata.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Document object with extracted content
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    full_text = ""
    page_texts = []
    font_info = {}
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text blocks with font information
        blocks = page.get_text("dict")
        page_text = ""
        
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        text = span["text"]
                        font_size = span["size"]
                        font_flags = span["flags"]
                        
                        # Store font information for heading detection
                        if text.strip():
                            font_key = f"{font_size}_{font_flags}"
                            if font_key not in font_info:
                                font_info[font_key] = {
                                    "size": font_size,
                                    "flags": font_flags,
                                    "count": 0
                                }
                            font_info[font_key]["count"] += 1
                        
                        line_text += text
                    
                    if line_text.strip():
                        page_text += line_text + "\\n"
        
        page_texts.append(page_text)
        full_text += page_text + "\\n"
    
    doc.close()
    
    # Create metadata
    metadata = {
        "filename": os.path.basename(pdf_path),
        "full_path": pdf_path,
        "page_texts": page_texts,
        "font_info": font_info
    }
    
    return Document(
        filename=os.path.basename(pdf_path),
        text=full_text,
        pages=len(page_texts),
        metadata=metadata
    )


def find_pdf_files(directory: str) -> List[str]:
    """
    Find all PDF files in a directory.
    
    Args:
        directory: Directory path to search for PDFs
        
    Returns:
        List of PDF file paths
    """
    pdf_files = []
    
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, filename))
    
    return sorted(pdf_files)