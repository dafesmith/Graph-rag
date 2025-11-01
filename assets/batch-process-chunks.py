#!/usr/bin/env python3
"""
Batch processor for txt2kg chunks
Processes multiple document chunks and stores them in the knowledge graph
"""

import os
import sys
import json
import time
import glob
import requests
from pathlib import Path

API_BASE_URL = "http://localhost:3001"
EXTRACT_ENDPOINT = f"{API_BASE_URL}/api/extract-triples"
STORE_ENDPOINT = f"{API_BASE_URL}/api/graph-db/triples"

def process_chunk(chunk_file, use_langchain=True):
    """Process a single chunk file"""
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(chunk_file)}")
    print(f"{'='*60}")

    # Read the file
    with open(chunk_file, 'r', encoding='utf-8') as f:
        text = f.read()

    file_size_kb = len(text) / 1024
    print(f"File size: {file_size_kb:.2f} KB")

    # Extract triples
    print("Extracting triples using NVIDIA Nemotron...")
    start_time = time.time()

    try:
        response = requests.post(
            EXTRACT_ENDPOINT,
            json={
                "text": text,
                "useLangChain": use_langchain,
                "useGraphTransformer": False
            },
            timeout=120  # 2 minute timeout per chunk
        )
        response.raise_for_status()
        result = response.json()

        extraction_time = time.time() - start_time
        triple_count = result.get('count', 0)

        print(f"✅ Extracted {triple_count} triples in {extraction_time:.1f}s")

        if triple_count == 0:
            print("⚠️  No triples extracted from this chunk")
            return {'success': True, 'triples': 0, 'stored': 0}

        # Store triples in graph database
        print("Storing triples in ArangoDB...")
        store_response = requests.post(
            STORE_ENDPOINT,
            json={
                "triples": result['triples'],
                "documentName": os.path.basename(chunk_file)
            },
            timeout=30
        )
        store_response.raise_for_status()
        store_result = store_response.json()

        stored_count = store_result.get('count', 0)
        print(f"✅ Stored {stored_count} triples in graph database")

        return {
            'success': True,
            'triples': triple_count,
            'stored': stored_count,
            'time': extraction_time
        }

    except requests.Timeout:
        print("❌ Request timed out - chunk may be too large")
        return {'success': False, 'error': 'timeout'}
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 batch-process-chunks.py <chunks_directory>")
        print("Example: python3 batch-process-chunks.py document_chunks/")
        sys.exit(1)

    chunks_dir = sys.argv[1]

    if not os.path.isdir(chunks_dir):
        print(f"Error: Directory '{chunks_dir}' not found")
        sys.exit(1)

    # Find all .txt files in the directory
    chunk_files = sorted(glob.glob(os.path.join(chunks_dir, "*.txt")))

    if not chunk_files:
        print(f"Error: No .txt files found in '{chunks_dir}'")
        sys.exit(1)

    print("\n" + "="*60)
    print("txt2kg Batch Processor")
    print("="*60)
    print(f"Chunks directory: {chunks_dir}")
    print(f"Total chunks: {len(chunk_files)}")
    print(f"API endpoint: {API_BASE_URL}")
    print("="*60)

    # Process each chunk
    results = []
    total_triples = 0
    total_stored = 0
    total_time = 0

    for i, chunk_file in enumerate(chunk_files, 1):
        print(f"\n[{i}/{len(chunk_files)}]", end=" ")
        result = process_chunk(chunk_file)
        results.append(result)

        if result['success']:
            total_triples += result['triples']
            total_stored += result['stored']
            total_time += result.get('time', 0)

        # Small delay between chunks to avoid overwhelming the API
        if i < len(chunk_files):
            time.sleep(1)

    # Summary
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    print(f"Total chunks processed: {len(chunk_files)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    print(f"Total triples extracted: {total_triples}")
    print(f"Total triples stored: {total_stored}")
    print(f"Total processing time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    if total_triples > 0:
        print(f"Average time per triple: {total_time/total_triples:.2f}s")
    print("="*60)
    print("\n✅ Batch processing complete!")
    print("\nNext steps:")
    print("1. View your knowledge graph at http://localhost:3001")
    print("2. Generate embeddings for semantic search")
    print("3. Test RAG queries at http://localhost:3001/rag")

if __name__ == "__main__":
    main()
