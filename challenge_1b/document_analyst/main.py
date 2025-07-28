"""
Main pipeline module for the Intelligent Document Analyst.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any

from .load_pdfs import load_pdfs, find_pdf_files
from .chunk_by_headings import chunk_by_headings
from .embed_chunks import embed_chunks
from .build_index import build_faiss_index
from .recall import recall_candidates, create_query_string
from .rerank import rerank_candidates
from .extract_sentences import extract_sentences_batch
from .assemble_output import assemble_output, save_results_to_json, print_summary


def run_analysis(
    pdf_dir: str,
    persona: Dict[str, Any],
    job_to_be_done: str,
    output_file: str = None
) -> Dict[str, Any]:
    """
    Run the complete document analysis pipeline.
    
    Args:
        pdf_dir: Directory containing PDF files
        persona: Persona dictionary
        job_to_be_done: Job description string
        output_file: Optional output file path
        
    Returns:
        Analysis results dictionary
    """
    print("Starting Intelligent Document Analyst...")
    
    # Step 1: Load PDFs
    print("\\n1. Loading PDF files...")
    pdf_files = find_pdf_files(pdf_dir)
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {pdf_dir}")
    
    print(f"Found {len(pdf_files)} PDF files")
    documents = load_pdfs(pdf_files)
    
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
    query = create_query_string(persona, job_to_be_done)
    print(f"Query: {query}")
    
    candidates = recall_candidates(query, index, chunks)
    
    # Step 6: Rerank candidates
    print("\\n6. Reranking candidates...")
    ranked_chunks = rerank_candidates(query, candidates)
    
    # Step 7: Extract top sentences
    print("\\n7. Extracting top sentences...")
    candidate_chunks = [chunk for chunk, _ in ranked_chunks]
    sentences_batch = extract_sentences_batch(candidate_chunks, query)
    
    # Create sentences map
    sentences_map = {}
    for chunk, sentences in zip(candidate_chunks, sentences_batch):
        sentences_map[chunk] = sentences
    
    # Step 8: Assemble final output
    print("\\n8. Assembling results...")
    input_metadata = {
        "input_documents": [doc.filename for doc in documents],
        "persona": persona,
        "job_to_be_done": job_to_be_done
    }
    
    result = assemble_output(ranked_chunks, sentences_map, input_metadata)
    
    # Save results if output file specified
    if output_file:
        save_results_to_json(result, output_file)
    
    # Print summary
    print_summary(result)
    
    return result.to_dict()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Intelligent Document Analyst - AI-powered document analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m document_analyst.main --pdf-dir ./pdfs --persona-json ./persona.json --job "Find information about data security" --output-file results.json
  
  python -m document_analyst.main --pdf-dir ./documents --persona-json ./user_context.json --job "Analyze financial performance metrics"
        """
    )
    
    parser.add_argument(
        '--pdf-dir',
        type=str,
        required=True,
        help='Directory containing PDF files to analyze'
    )
    
    parser.add_argument(
        '--persona-json',
        type=str,
        required=True,
        help='Path to JSON file containing persona information'
    )
    
    parser.add_argument(
        '--job',
        type=str,
        required=True,
        help='Job to be done description string'
    )
    
    parser.add_argument(
        '--output-file',
        type=str,
        help='Output file path for results (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load persona from JSON file
        with open(args.persona_json, 'r', encoding='utf-8') as f:
            persona = json.load(f)
        
        # Run analysis
        results = run_analysis(
            pdf_dir=args.pdf_dir,
            persona=persona,
            job_to_be_done=args.job,
            output_file=args.output_file
        )
        
        print("\\nAnalysis completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()