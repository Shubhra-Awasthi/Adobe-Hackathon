# Adobe "Connecting the Dots" Challenge Submission

> **Rethink Reading. Rediscover Knowledge**

This repository contains our complete solution for the Adobe "Connecting the Dots" Challenge, implementing intelligent PDF processing and document analysis systems for both Round 1A and Round 1B.

## 🎯 Challenge Overview

The challenge focuses on reimagining PDFs as intelligent, interactive experiences that understand structure, surface insights, and respond like trusted research companions.

- **Round 1A**: Extract structured outlines from raw PDFs with speed and accuracy
- **Round 1B**: Build persona-driven document intelligence for specific user needs

## 📁 Project Structure

```
Adobe/
├── challenge_1a/                    # Round 1A: PDF Outline Extraction
│   ├── app/
│   │   ├── input/                   # Sample PDF files
│   │   └── output/                  # Generated JSON outlines
│   ├── process_pdfs.py             # Main processing script
│   ├── Dockerfile                   # AMD64 compatible container
│   ├── requirements.txt             # Dependencies
│   └── README.md                   # Round 1A documentation
│
├── challenge_1b/                    # Round 1B: Intelligent Document Analyst
│   ├── document_analyst/           # Core AI pipeline modules
│   ├── challenge_pdfs/             # Sample PDF documents
│   ├── challenge_main.py           # Main entry point
│   ├── approach_explanation.md     # Methodology explanation
│   ├── execution_instructions.md   # Detailed execution guide
│   ├── challenge1b_input.json      # Sample input
│   ├── challenge1b_output.json     # Sample output
│   ├── test_submission.py          # Comprehensive test suite
│   ├── SUBMISSION_CHECKLIST.md     # Verification checklist
│   ├── Dockerfile                  # Container configuration
│   ├── requirements.txt            # Dependencies
│   └── README.md                   # Round 1B documentation
│
└── README.md                       # This file
```

## 🚀 Quick Start

### Round 1A: PDF Outline Extraction

```bash
# Build the Docker image
cd challenge_1a
docker build --platform linux/amd64 -t pdf-outline-extractor .

# Run the solution
docker run --rm -v $(pwd)/app/input:/app/input -v $(pwd)/app/output:/app/output \
  --network none pdf-outline-extractor
```

### Round 1B: Intelligent Document Analyst

```bash
# Build the Docker image
cd challenge_1b
docker build -t intelligent-document-analyst .

# Run the solution
docker run -v $(pwd)/data:/app/data intelligent-document-analyst \
  python challenge_main.py \
  --input-file /app/data/challenge1b_input.json \
  --pdf-dir /app/data/challenge_pdfs \
  --output-file /app/data/challenge1b_output.json
```

## 🎯 Round 1A: Understand Your Document

### Features
- **Smart Heading Detection**: Multi-method approach using embedded outlines, font analysis, and numbering patterns
- **Multilingual Support**: Handles Chinese, Arabic, and other numbering systems
- **Robust Processing**: Works with various PDF formats and structures
- **Fast Execution**: ≤ 10 seconds for 50-page PDFs
- **Offline Processing**: No internet dependencies

### Technical Implementation
- **PDF Processing**: PyMuPDF for efficient text and font extraction
- **Heading Detection**: Font-size heuristics, numbering patterns, embedded outlines
- **Output Format**: Valid JSON with title and hierarchical outline structure

### Performance Constraints Met
- ✅ **Execution Time**: ≤ 10 seconds for 50-page PDFs
- ✅ **Model Size**: ≤ 200MB (PyMuPDF + numpy)
- ✅ **CPU Only**: AMD64 architecture
- ✅ **No Network**: Offline processing only

## 🧠 Round 1B: Persona-Driven Document Intelligence

### Features
- **Multi-PDF Processing**: Analyzes 3-10 PDF files simultaneously
- **AI-Powered Relevance**: Dual-model approach with bi-encoder and cross-encoder
- **Persona-Aware Analysis**: Incorporates user context into relevance calculations
- **Smart Chunking**: Automatic document section detection using font-size heuristics
- **Granular Extraction**: Sentence-level relevance scoring within sections

### Technical Architecture
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

### Performance Constraints Met
- ✅ **Execution Time**: ≤ 60 seconds (completes in ~55s for 7 documents)
- ✅ **Model Size**: ≤ 1GB (uses ~180MB total)
- ✅ **CPU Only**: Optimized for CPU inference
- ✅ **No Internet**: Pre-downloaded models

## 📊 Output Formats

### Round 1A Output
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "What is AI?",
      "page": 2
    }
  ]
}
```

### Round 1B Output
```json
{
  "metadata": {
    "input_documents": [...],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip of 4 days...",
    "processing_timestamp": "..."
  },
  "extracted_sections": [
    {
      "document": "document.pdf",
      "section_title": "Section Title",
      "importance_rank": 1,
      "page_number": "1-5"
    }
  ],
  "subsection_analysis": [
    {
      "document": "document.pdf",
      "refined_text": "Extracted relevant text...",
      "page_number": "1-5"
    }
  ]
}
```

## 🏆 Scoring Criteria Alignment

### Round 1A
- ✅ **Heading Detection Accuracy**: Multi-method approach ensures high precision and recall
- ✅ **Performance**: Fast processing with minimal dependencies
- ✅ **Multilingual Handling**: Supports diverse languages and numbering systems

### Round 1B
- ✅ **Section Relevance (60 points)**: Smart chunking, context-aware querying, hybrid scoring
- ✅ **Sub-Section Relevance (40 points)**: Granular sentence extraction and ranking

## 🔧 Technical Highlights

### Innovation Features
1. **Font-Based Heading Detection**: Automatically identifies document sections without manual annotation
2. **Hybrid Relevance Scoring**: Combines fast retrieval with precise reranking
3. **Persona-Aware Processing**: Incorporates user context into relevance calculations
4. **Scalable Architecture**: Handles diverse document collections with consistent performance

### Code Quality
- **Modular Architecture**: Clean separation of concerns
- **Error Handling**: Robust error management
- **Configurable Parameters**: Adjustable settings for different use cases
- **Comprehensive Testing**: Test suite for validation

## 📋 Submission Checklist

### Round 1A ✅
- [x] Working Dockerfile (AMD64 compatible)
- [x] All dependencies installed within container
- [x] README with approach explanation and build/run instructions
- [x] Processes PDFs from `/app/input` to `/app/output`
- [x] Generates valid JSON output format
- [x] Meets all performance constraints

### Round 1B ✅
- [x] `approach_explanation.md` (300-500 words)
- [x] Dockerfile and execution instructions
- [x] Sample input/output for testing
- [x] Meets all performance constraints
- [x] Comprehensive test suite

## 🚀 Getting Started

### Prerequisites
- Docker (for containerized execution)
- Python 3.9+ (for direct execution)

### Installation
1. Clone this repository
2. Navigate to the specific challenge directory (`challenge_1a` or `challenge_1b`)
3. Follow the respective README files for detailed instructions

### Testing
- **Round 1A**: Place PDF files in `challenge_1a/app/input/` and run the Docker container
- **Round 1B**: Use the provided sample files or create your own input JSON

## 📈 Performance Metrics

### Round 1A
- **Processing Speed**: ≤ 10 seconds for 50-page PDFs
- **Model Size**: ~50MB total dependencies
- **Accuracy**: Multi-method heading detection for high precision/recall

### Round 1B
- **Processing Speed**: ≤ 60 seconds for 7 documents
- **Model Size**: ~180MB total AI models
- **Relevance**: Hybrid scoring for optimal section and sentence extraction

## 🤝 Contributing

This is a competition submission for the Adobe "Connecting the Dots" Challenge. The code is designed to be self-contained and ready for evaluation.

## 📄 License

This project is submitted for the Adobe "Connecting the Dots" Challenge. All rights reserved.

---

**Theme**: "Connect What Matters — For the User Who Matters"

*Building the future of how we read, learn, and connect.* 