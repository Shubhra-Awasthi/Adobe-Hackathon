"""
Output assembly module for formatting final results.
"""

import json
from typing import List, Tuple, Dict, Any
from datetime import datetime

from .models import Chunk, ScoredSentence, AnalysisResult
from .config import TOP_N_OUTPUT, OUTPUT_PRECISION


def assemble_output(
    ranked_chunks: List[Tuple[Chunk, float]], 
    sentences_map: Dict[Chunk, List[ScoredSentence]],
    input_metadata: Dict[str, Any]
) -> AnalysisResult:
    """
    Assemble the final output with all required metadata and results.
    
    Args:
        ranked_chunks: List of (chunk, score) tuples sorted by relevance
        sentences_map: Dictionary mapping chunks to their top sentences
        input_metadata: Metadata about the input (persona, job_to_be_done, etc.)
        
    Returns:
        AnalysisResult object with structured output
    """
    # Create metadata section
    metadata = {
        "input_documents": input_metadata.get("input_documents", []),
        "persona": input_metadata.get("persona", {}),
        "job_to_be_done": input_metadata.get("job_to_be_done", ""),
        "processing_timestamp": datetime.now().isoformat(),
        "total_chunks_processed": len(ranked_chunks),
        "top_results_returned": min(TOP_N_OUTPUT, len(ranked_chunks))
    }
    
    # Create results section
    results = []
    
    for i, (chunk, score) in enumerate(ranked_chunks[:TOP_N_OUTPUT]):
        # Get top sentences for this chunk
        top_sentences = sentences_map.get(chunk, [])
        
        # Format sentences
        formatted_sentences = []
        for sentence in top_sentences:
            formatted_sentences.append({
                "text": sentence.text,
                "score": round(sentence.score, OUTPUT_PRECISION)
            })
        
        # Create result entry
        result_entry = {
            "extracted_section": {
                "document": chunk.source_doc,
                "page_number": f"{chunk.start_page}-{chunk.end_page}" if chunk.start_page != chunk.end_page else str(chunk.start_page),
                "section_title": chunk.section_title or "Untitled Section",
                "importance_rank": i + 1,
                "relevance_score": round(score, OUTPUT_PRECISION),
                "chunk_text": chunk.text
            },
            "sub_section_analysis": {
                "document": chunk.source_doc,
                "page_number": f"{chunk.start_page}-{chunk.end_page}" if chunk.start_page != chunk.end_page else str(chunk.start_page),
                "top_sentences": formatted_sentences,
                "refined_text": " ".join([s["text"] for s in formatted_sentences[:2]])  # Top 2 sentences as refined text
            }
        }
        
        results.append(result_entry)
    
    return AnalysisResult(metadata=metadata, results=results)


def save_results_to_json(result: AnalysisResult, output_file: str) -> None:
    """
    Save analysis results to a JSON file.
    
    Args:
        result: AnalysisResult object to save
        output_file: Output file path
    """
    output_dict = result.to_dict()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_dict, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to {output_file}")


def print_summary(result: AnalysisResult) -> None:
    """
    Print a summary of the analysis results.
    
    Args:
        result: AnalysisResult object to summarize
    """
    print("\\n" + "="*60)
    print("INTELLIGENT DOCUMENT ANALYST - RESULTS SUMMARY")
    print("="*60)
    
    metadata = result.metadata
    print(f"Processing Time: {metadata['processing_timestamp']}")
    print(f"Documents Analyzed: {len(metadata['input_documents'])}")
    print(f"Persona: {metadata['persona']}")
    print(f"Job to be Done: {metadata['job_to_be_done']}")
    print(f"Total Chunks Processed: {metadata['total_chunks_processed']}")
    print(f"Top Results Returned: {metadata['top_results_returned']}")
    
    print("\\n" + "-"*60)
    print("TOP RESULTS:")
    print("-"*60)
    
    for i, result_entry in enumerate(result.results[:5]):  # Show top 5
        extracted = result_entry["extracted_section"]
        sub_analysis = result_entry["sub_section_analysis"]
        
        print(f"\\n{i+1}. {extracted['section_title']} (Score: {extracted['relevance_score']})")
        print(f"   Document: {extracted['document']}, Page: {extracted['page_number']}")
        print(f"   Top Sentence: {sub_analysis['top_sentences'][0]['text'][:100]}..." if sub_analysis['top_sentences'] else "   No sentences extracted")
    
    print("\\n" + "="*60)