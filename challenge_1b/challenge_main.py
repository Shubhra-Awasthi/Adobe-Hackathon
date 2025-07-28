#!/usr/bin/env python3
"""
Challenge main script for Intelligent Document Analyst.
Handles the specific input/output format required for the challenge.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, List
from datetime import datetime

from document_analyst.load_pdfs import load_pdfs
from document_analyst.chunk_by_headings import chunk_by_headings
from document_analyst.embed_chunks import embed_chunks, EmbeddingGenerator
from document_analyst.build_index import build_faiss_index, search_index
from document_analyst.recall import recall_candidates, create_query_string
from document_analyst.rerank import rerank_candidates
from document_analyst.extract_sentences import extract_sentences_batch
from document_analyst.config import TOP_N_OUTPUT, TOP_K_CANDIDATES
from document_analyst.models import ScoredSentence


def run_challenge_analysis(input_file: str, pdf_dir: str, output_file: str) -> Dict[str, Any]:
    """
    Run the document analysis with challenge-specific input/output format.
    
    Args:
        input_file: Path to input JSON file
        pdf_dir: Directory containing PDF files
        output_file: Path to output JSON file
        
    Returns:
        Analysis results dictionary
    """
    print("Starting Challenge Document Analysis...")
    
    # Load input configuration
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # Extract persona and job from the input format
    persona = input_data.get("persona", {})
    job_to_be_done = input_data.get("job_to_be_done", {}).get("task", "")
    
    # Get list of documents to process
    document_list = input_data.get("documents", [])
    
    # Step 1: Load PDFs
    print("\\n1. Loading PDF files...")
    pdf_paths = []
    for doc in document_list:
        filename = doc.get("filename", "")
        if filename:
            pdf_path = os.path.join(pdf_dir, filename)
            if os.path.exists(pdf_path):
                pdf_paths.append(pdf_path)
            else:
                print(f"Warning: PDF file not found: {pdf_path}")
    
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found in {pdf_dir}")
    
    print(f"Found {len(pdf_paths)} PDF files")
    documents = load_pdfs(pdf_paths)
    
    # Step 2: Chunk documents
    print("\\n2. Chunking documents by headings...")
    chunks = chunk_by_headings(documents)
    print(f"Created {len(chunks)} chunks")
    
    # Step 3: Generate embeddings
    print("\\n3. Generating embeddings...")
    embeddings = embed_chunks(chunks)
    
    # Step 4: Build FAISS index
    print("\\n4. Building FAISS index...")
    index = build_faiss_index(embeddings)
    
    # Step 5: Create query and recall candidates
    print("\\n5. Recalling candidate chunks...")
    # Convert persona to expected format for query creation
    persona_dict = {"role": persona.get("role", "")}
    query = create_query_string(persona_dict, job_to_be_done)
    print(f"Query: {query}")
    
    candidates = recall_candidates(query, index, chunks)
    
    # Step 6: Rerank candidates
    print("\\n6. Reranking candidates...")
    ranked_chunks = rerank_candidates(query, candidates)
    
    # Step 7: Extract top sentences
    print("\\n7. Extracting top sentences...")
    # Use only the top N chunks for sentence extraction to optimize performance
    top_chunks = [chunk for chunk, _ in ranked_chunks[:TOP_N_OUTPUT]]
    sentences_batch = extract_sentences_batch(top_chunks, query)
    
    # Step 8: Assemble output in challenge format
    print("\\n8. Assembling results...")
    result = assemble_challenge_output(ranked_chunks, sentences_batch, input_data)
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"Results saved to {output_file}")
    print_challenge_summary(result)
    
    return result


def assemble_challenge_output(
    ranked_chunks: List[tuple], 
    sentences_batch: List[List], 
    input_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assemble output in the challenge-specific format.
    
    Args:
        ranked_chunks: List of (chunk, score) tuples
        sentences_batch: List of sentence lists for each chunk
        input_data: Original input data
        
    Returns:
        Formatted output dictionary
    """
    # Create metadata
    metadata = {
        "input_documents": [doc.get("filename", "") for doc in input_data.get("documents", [])],
        "persona": input_data.get("persona", {}).get("role", ""),
        "job_to_be_done": input_data.get("job_to_be_done", {}).get("task", ""),
        "processing_timestamp": datetime.now().isoformat()
    }
    
    # Create extracted sections
    extracted_sections = []
    subsection_analysis = []
    
    for i, (chunk, score) in enumerate(ranked_chunks[:TOP_N_OUTPUT]):
        # Find corresponding sentences
        sentences = sentences_batch[i] if i < len(sentences_batch) else []
        
        # Extract section title from chunk text or use a default
        section_title = extract_section_title(chunk.text)
        
        # Create extracted section entry
        extracted_section = {
            "document": chunk.source_doc,
            "section_title": section_title,
            "importance_rank": i + 1,
            "page_number": chunk.start_page if chunk.start_page == chunk.end_page else f"{chunk.start_page}-{chunk.end_page}"
        }
        extracted_sections.append(extracted_section)
        
        # Create subsection analysis entry
        if sentences:
            # Use all sentences to create refined text
            refined_text = " ".join([sentence.text for sentence in sentences])
            
            subsection_entry = {
                "document": chunk.source_doc,
                "refined_text": refined_text,
                "page_number": chunk.start_page if chunk.start_page == chunk.end_page else f"{chunk.start_page}-{chunk.end_page}"
            }
            subsection_analysis.append(subsection_entry)
    
    return {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }


def extract_section_title(text: str) -> str:
    """
    Extract a section title from chunk text.
    
    Args:
        text: Chunk text
        
    Returns:
        Section title
    """
    # Split into lines and find the first meaningful line
    lines = text.split('\\n')
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 5 and len(line) < 100:
            # Remove numbers and dots from the beginning
            title = line.lstrip('0123456789. ')
            if title:
                return title
    
    # If no good title found, use first 50 characters
    clean_text = text.replace('\\n', ' ').strip()
    if len(clean_text) > 50:
        return clean_text[:50] + "..."
    return clean_text if clean_text else "Untitled Section"


def print_challenge_summary(result: Dict[str, Any]) -> None:
    """
    Print a summary of the challenge results.
    
    Args:
        result: Analysis result dictionary
    """
    print("\\n" + "="*60)
    print("CHALLENGE DOCUMENT ANALYST - RESULTS SUMMARY")
    print("="*60)
    
    metadata = result["metadata"]
    print(f"Processing Time: {metadata['processing_timestamp']}")
    print(f"Documents Analyzed: {len(metadata['input_documents'])}")
    print(f"Persona: {metadata['persona']}")
    print(f"Job to be Done: {metadata['job_to_be_done']}")
    print(f"Extracted Sections: {len(result['extracted_sections'])}")
    print(f"Subsection Analyses: {len(result['subsection_analysis'])}")
    
    print("\\n" + "-"*60)
    print("TOP EXTRACTED SECTIONS:")
    print("-"*60)
    
    for section in result["extracted_sections"][:5]:  # Show top 5
        print(f"\\n{section['importance_rank']}. {section['section_title']}")
        print(f"   Document: {section['document']}")
        print(f"   Page: {section['page_number']}")
    
    print("\\n" + "="*60)


def main():
    """Main CLI entry point for challenge format."""
    parser = argparse.ArgumentParser(
        description="Challenge Document Analyst - processes challenge format input/output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python challenge_main.py --input-file challenge1b_input.json --pdf-dir ./challenge_pdfs --output-file challenge1b_output.json
        """
    )
    
    parser.add_argument(
        '--input-file',
        type=str,
        required=True,
        help='Path to input JSON file with challenge format'
    )
    
    parser.add_argument(
        '--pdf-dir',
        type=str,
        required=True,
        help='Directory containing PDF files'
    )
    
    parser.add_argument(
        '--output-file',
        type=str,
        required=True,
        help='Path to output JSON file'
    )
    
    args = parser.parse_args()
    
    try:
        # Run challenge analysis
        results = run_challenge_analysis(
            input_file=args.input_file,
            pdf_dir=args.pdf_dir,
            output_file=args.output_file
        )
        
        print("\\nChallenge analysis completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()