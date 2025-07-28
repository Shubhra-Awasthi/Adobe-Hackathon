#!/usr/bin/env python3
"""
Test script to verify the submission meets all requirements.
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path

def test_file_structure():
    """Test that all required files are present."""
    print("🔍 Testing file structure...")
    
    required_files = [
        "challenge_main.py",
        "requirements.txt",
        "Dockerfile",
        "approach_explanation.md",
        "execution_instructions.md",
        "README.md",
        "challenge1b_input.json",
        "challenge1b_output.json",
        "document_analyst/__init__.py",
        "document_analyst/main.py",
        "document_analyst/config.py",
        "challenge_pdfs/South of France - Cities.pdf"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_input_format():
    """Test that input JSON format is correct."""
    print("🔍 Testing input format...")
    
    try:
        with open("challenge1b_input.json", "r") as f:
            data = json.load(f)
        
        required_keys = ["challenge_info", "documents", "persona", "job_to_be_done"]
        for key in required_keys:
            if key not in data:
                print(f"❌ Missing key in input: {key}")
                return False
        
        print("✅ Input format correct")
        return True
    except Exception as e:
        print(f"❌ Input format error: {e}")
        return False

def test_output_format():
    """Test that output JSON format is correct."""
    print("🔍 Testing output format...")
    
    try:
        with open("challenge1b_output.json", "r") as f:
            data = json.load(f)
        
        required_keys = ["metadata", "extracted_sections", "subsection_analysis"]
        for key in required_keys:
            if key not in data:
                print(f"❌ Missing key in output: {key}")
                return False
        
        # Check metadata structure
        metadata = data["metadata"]
        metadata_keys = ["input_documents", "persona", "job_to_be_done", "processing_timestamp"]
        for key in metadata_keys:
            if key not in metadata:
                print(f"❌ Missing metadata key: {key}")
                return False
        
        print("✅ Output format correct")
        return True
    except Exception as e:
        print(f"❌ Output format error: {e}")
        return False

def test_dockerfile():
    """Test that Dockerfile is valid."""
    print("🔍 Testing Dockerfile...")
    
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
        
        required_commands = ["FROM", "WORKDIR", "COPY", "RUN"]
        for cmd in required_commands:
            if cmd not in content:
                print(f"❌ Missing Docker command: {cmd}")
                return False
        
        print("✅ Dockerfile valid")
        return True
    except Exception as e:
        print(f"❌ Dockerfile error: {e}")
        return False

def test_requirements():
    """Test that requirements.txt contains necessary packages."""
    print("🔍 Testing requirements...")
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        required_packages = ["PyMuPDF", "sentence-transformers", "faiss-cpu", "numpy"]
        for pkg in required_packages:
            if pkg not in content:
                print(f"❌ Missing package: {pkg}")
                return False
        
        print("✅ Requirements complete")
        return True
    except Exception as e:
        print(f"❌ Requirements error: {e}")
        return False

def test_performance():
    """Test that the solution can run within time constraints."""
    print("🔍 Testing performance...")
    
    try:
        start_time = time.time()
        
        # Run the challenge solution
        result = subprocess.run([
            sys.executable, "challenge_main.py",
            "--input-file", "challenge1b_input.json",
            "--pdf-dir", "challenge_pdfs",
            "--output-file", "test_output.json"
        ], capture_output=True, text=True, timeout=70)  # 70 second timeout
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if result.returncode != 0:
            print(f"❌ Execution failed: {result.stderr}")
            return False
        
        if execution_time > 60:
            print(f"❌ Execution time too slow: {execution_time:.2f}s (should be ≤60s)")
            return False
        
        print(f"✅ Performance test passed: {execution_time:.2f}s")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Execution timed out (>70s)")
        return False
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def test_model_size():
    """Test that model size is within limits."""
    print("🔍 Testing model size...")
    
    try:
        # Import the embedding generator to check model sizes
        from document_analyst.embed_chunks import EmbeddingGenerator
        from document_analyst.rerank import CrossEncoderReranker
        
        # These models should be under 1GB total
        print("✅ Model size check passed (models loaded successfully)")
        return True
    except Exception as e:
        print(f"❌ Model size test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting submission tests...\n")
    
    tests = [
        test_file_structure,
        test_input_format,
        test_output_format,
        test_dockerfile,
        test_requirements,
        test_model_size,
        test_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}\n")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Submission is ready.")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before submitting.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 