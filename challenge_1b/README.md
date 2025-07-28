# Intelligent Document Analyst - Adobe Challenge Submission

## Theme: "Connect What Matters — For the User Who Matters"

This solution implements an intelligent document analysis system that extracts and prioritizes the most relevant sections from document collections based on specific personas and their job-to-be-done requirements.

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Build the Docker image:**
   ```bash
   docker build -t intelligent-document-analyst .
   ```

2. **Run the solution:**
   ```bash
   docker run -v $(pwd)/data:/app/data intelligent-document-analyst \
     python challenge_main.py \
     --input-file /app/data/challenge1b_input.json \
     --pdf-dir /app/data/challenge_pdfs \
     --output-file /app/data/challenge1b_output.json
   ```

### Using Python Directly

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the solution:**
   ```bash
   python challenge_main.py \
     --input-file challenge1b_input.json \
     --pdf-dir challenge_pdfs \
     --output-file challenge1b_output.json
   ```

## 📁 Project Structure

```
challenge_1b/
├── document_analyst/          # Core AI pipeline modules
├── challenge_main.py          # Main entry point for challenge format
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── approach_explanation.md    # Methodology explanation
├── execution_instructions.md  # Detailed execution guide
├── challenge1b_input.json     # Sample input file
├── challenge1b_output.json    # Sample output file
├── challenge_pdfs/            # Sample PDF documents
└── README.md                  # This file
```

## 🎯 Features

### Core Capabilities
- **Multi-PDF Processing**: Analyzes 3-10 PDF files simultaneously
- **Smart Chunking**: Automatic document section detection using font-size heuristics
- **AI-Powered Relevance**: Dual-model approach with bi-encoder and cross-encoder
- **Persona-Aware Analysis**: Incorporates user context into relevance calculations
- **Granular Extraction**: Sentence-level relevance scoring within sections

### Performance Constraints Met
- ✅ **CPU Only**: No GPU dependencies
- ✅ **Model Size ≤ 1GB**: Total model size ~180MB
- ✅ **Processing Time ≤ 60s**: Completes in ~55 seconds for 7 documents
- ✅ **No Internet Access**: All models pre-downloaded and cached

## 🔧 Technical Architecture

### AI Pipeline Stages
1. **PDF Loading**: Extracts text and font metadata using PyMuPDF
2. **Smart Chunking**: Segments documents by heading detection
3. **Embedding Generation**: Creates vector representations using bi-encoder
4. **FAISS Indexing**: Builds efficient similarity search index
5. **Recall Stage**: Retrieves candidate chunks using similarity search
6. **Reranking**: Refines relevance with cross-encoder model
7. **Sentence Extraction**: Identifies top sentences within chunks
8. **Output Assembly**: Formats final results

### AI Models Used
- **Bi-Encoder**: `all-MiniLM-L6-v2` (~80MB) for fast similarity search
- **Cross-Encoder**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (~100MB) for precise reranking

## 📊 Input/Output Format

### Input Format
```json
{
    "challenge_info": {
        "challenge_id": "round_1b_002",
        "test_case_name": "travel_planner",
        "description": "France Travel"
    },
    "documents": [
        {"filename": "document1.pdf", "title": "Document Title"}
    ],
    "persona": {
        "role": "Travel Planner"
    },
    "job_to_be_done": {
        "task": "Plan a trip of 4 days for a group of 10 college friends."
    }
}
```

### Output Format
```json
{
    "metadata": {
        "input_documents": [...],
        "persona": "Travel Planner",
        "job_to_be_done": "Plan a trip...",
        "processing_timestamp": "..."
    },
    "extracted_sections": [
        {
            "document": "document.pdf",
            "section_title": "Section Title",
            "importance_rank": 1,
            "page_number": "1-3"
        }
    ],
    "subsection_analysis": [
        {
            "document": "document.pdf",
            "refined_text": "Extracted relevant text...",
            "page_number": "1-3"
        }
    ]
}
```

## 🧪 Testing

### Run Sample Test
```bash
python challenge_main.py \
  --input-file challenge1b_input.json \
  --pdf-dir challenge_pdfs \
  --output-file test_output.json
```

### Verify Performance
```bash
time python challenge_main.py \
  --input-file challenge1b_input.json \
  --pdf-dir challenge_pdfs \
  --output-file test_output.json
```

## 📈 Scoring Criteria Alignment

### Section Relevance (60 points)
- **Smart Chunking**: Font-based heading detection preserves document structure
- **Context-Aware Querying**: Combines persona and job requirements
- **Hybrid Relevance**: Bi-encoder for recall, cross-encoder for precision
- **Proper Ranking**: Configurable importance ranking with relevance scores

### Sub-Section Relevance (40 points)
- **Sentence-Level Extraction**: Cross-encoder identifies top sentences
- **Granular Analysis**: Each chunk analyzed for most relevant content
- **Refined Text Generation**: Combines top sentences into coherent summaries
- **Quality Ranking**: Sentences ranked by relevance to persona and job

## 🔍 Use Cases Supported

The system is designed to handle diverse scenarios:

- **Academic Research**: Literature reviews, research paper analysis
- **Business Analysis**: Financial reports, market research
- **Educational Content**: Textbook analysis, exam preparation
- **Travel Planning**: Destination guides, itinerary creation
- **Technical Documentation**: Manual analysis, procedure extraction

## 🛠️ Configuration

Key parameters can be adjusted in `document_analyst/config.py`:
- `TOP_K_CANDIDATES`: Number of candidates for recall (default: 20)
- `TOP_N_OUTPUT`: Number of final sections (default: 10)
- `TOP_M_SENTENCES`: Number of top sentences per chunk (default: 3)
- `MAX_CHUNK_TOKENS`: Maximum tokens per chunk (default: 512)

## 📝 License

This project is provided as-is for the Adobe Challenge submission. 