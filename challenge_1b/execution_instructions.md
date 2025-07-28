# Execution Instructions

## Docker Setup and Execution

### 1. Build the Docker Image
```bash
docker build -t intelligent-document-analyst .
```

### 2. Run the Solution

#### Option A: Direct Execution
```bash
docker run -v $(pwd)/data:/app/data intelligent-document-analyst \
  python challenge_main.py \
  --input-file /app/data/challenge1b_input.json \
  --pdf-dir /app/data/challenge_pdfs \
  --output-file /app/data/challenge1b_output.json
```

#### Option B: Interactive Mode
```bash
docker run -it -v $(pwd)/data:/app/data intelligent-document-analyst bash
```

Then inside the container:
```bash
python challenge_main.py \
  --input-file /app/data/challenge1b_input.json \
  --pdf-dir /app/data/challenge_pdfs \
  --output-file /app/data/challenge1b_output.json
```

### 3. File Structure Requirements

Ensure your data directory contains:
```
data/
├── challenge1b_input.json
└── challenge_pdfs/
    ├── South of France - Cities.pdf
    ├── South of France - Cuisine.pdf
    ├── South of France - History.pdf
    ├── South of France - Restaurants and Hotels.pdf
    ├── South of France - Things to Do.pdf
    ├── South of France - Tips and Tricks.pdf
    └── South of France - Traditions and Culture.pdf
```

### 4. Expected Output

The solution will generate `challenge1b_output.json` with the following structure:
```json
{
  "metadata": {
    "input_documents": [...],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends.",
    "processing_timestamp": "..."
  },
  "extracted_sections": [...],
  "subsection_analysis": [...]
}
```

### 5. Performance Verification

The solution should complete within 60 seconds and use less than 1GB of memory. You can monitor performance with:

```bash
docker run --memory=1g -v $(pwd)/data:/app/data intelligent-document-analyst \
  time python challenge_main.py \
  --input-file /app/data/challenge1b_input.json \
  --pdf-dir /app/data/challenge_pdfs \
  --output-file /app/data/challenge1b_output.json
```

### 6. Testing Different Scenarios

To test with different input files, simply replace the input file:

```bash
docker run -v $(pwd)/data:/app/data intelligent-document-analyst \
  python challenge_main.py \
  --input-file /app/data/your_test_input.json \
  --pdf-dir /app/data/your_pdfs \
  --output-file /app/data/your_output.json
```

## Troubleshooting

### Common Issues:

1. **Memory Issues**: Ensure Docker has at least 2GB RAM allocated
2. **Model Download**: First run may take longer as models are downloaded
3. **PDF Access**: Ensure PDF files are readable and not corrupted
4. **Output Permissions**: Ensure output directory is writable

### Verification Commands:

```bash
# Check if models are downloaded
docker run intelligent-document-analyst ls -la /app/models

# Test with sample data
docker run -v $(pwd)/data:/app/data intelligent-document-analyst \
  python -c "from document_analyst.main import run_analysis; print('System ready')"
``` 