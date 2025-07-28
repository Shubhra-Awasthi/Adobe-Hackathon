"""
Configuration constants for the Intelligent Document Analyst.
"""

# Model configurations
BI_ENCODER_MODEL = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Processing parameters
TOP_K_CANDIDATES = 20      # Number of candidates for recall stage (reduced for speed)
TOP_N_OUTPUT = 10          # Number of final sections to output
TOP_M_SENTENCES = 3        # Number of top sentences per chunk
MAX_CHUNK_TOKENS = 512     # Approximate max tokens per chunk
BATCH_SIZE = 16            # Batch size for model inference (reduced for speed)

# FAISS configuration
FAISS_INDEX_TYPE = "IndexFlatIP"  # Inner product for cosine similarity

# Chunking parameters
MIN_CHUNK_LENGTH = 100     # Minimum characters per chunk
HEADING_FONT_THRESHOLD = 2  # Font size difference to detect headings

# Output formatting
OUTPUT_PRECISION = 4       # Decimal places for scores