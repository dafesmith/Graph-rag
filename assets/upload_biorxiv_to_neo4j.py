#!/usr/bin/env python3
"""
Upload bioRxiv dataset to Neo4j Aura
Processes .txt files and extracts knowledge graph triples using the API
"""
import os
import json
import requests
from pathlib import Path
from typing import List, Dict
import time

# Neo4j Aura credentials
NEO4J_URI = "neo4j+s://50a0f5b5.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "7cFtku457GEwz2UbNcC9LRWkLRCQaqxqPuSfUmPE--Q"

# API endpoint (assuming local development)
API_BASE_URL = "http://localhost:3000"

# Dataset path
DATASET_PATH = "/Users/dafesmith/Documents/repo/Graph-rag/assets/examples/biorxiv_genetics_genomics"

def read_document(file_path: str) -> str:
    """Read a document from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_triples_via_api(text: str, document_name: str) -> List[Dict]:
    """Extract triples from text using the API endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/extract-triples",
            json={"text": text, "documentName": document_name},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('triples', [])
        else:
            print(f"Error extracting triples: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Exception extracting triples: {e}")
        return []

def upload_triples_to_neo4j(triples: List[Dict]) -> bool:
    """Upload triples to Neo4j via API endpoint"""
    try:
        # Use the graph-db endpoint with Neo4j credentials
        response = requests.post(
            f"{API_BASE_URL}/api/graph-db?type=neo4j&url={NEO4J_URI}&username={NEO4J_USER}&password={NEO4J_PASSWORD}",
            json={"triples": triples},
            timeout=120
        )

        if response.status_code == 200:
            return True
        else:
            print(f"Error uploading triples: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception uploading triples: {e}")
        return False

def process_dataset(max_files: int = None):
    """Process all files in the dataset"""
    dataset_dir = Path(DATASET_PATH)
    txt_files = sorted(dataset_dir.glob("*.txt"))

    if max_files:
        txt_files = txt_files[:max_files]

    total_files = len(txt_files)
    print(f"Found {total_files} files to process")

    successful_uploads = 0
    failed_uploads = 0
    total_triples = 0

    for i, file_path in enumerate(txt_files, 1):
        print(f"\n[{i}/{total_files}] Processing: {file_path.name}")

        try:
            # Read document
            text = read_document(str(file_path))

            # Skip if text is too short
            if len(text) < 50:
                print(f"  Skipping (text too short: {len(text)} chars)")
                continue

            print(f"  Document size: {len(text)} chars")

            # Extract triples
            print(f"  Extracting triples...")
            triples = extract_triples_via_api(text, file_path.name)

            if not triples:
                print(f"  No triples extracted")
                failed_uploads += 1
                continue

            print(f"  Extracted {len(triples)} triples")
            total_triples += len(triples)

            # Upload to Neo4j
            print(f"  Uploading to Neo4j...")
            if upload_triples_to_neo4j(triples):
                print(f"  ✓ Successfully uploaded")
                successful_uploads += 1
            else:
                print(f"  ✗ Failed to upload")
                failed_uploads += 1

            # Rate limiting
            if i % 10 == 0:
                print(f"\n--- Progress: {i}/{total_files} files processed ---")
                time.sleep(1)

        except Exception as e:
            print(f"  Error processing file: {e}")
            failed_uploads += 1
            continue

    print(f"\n{'='*60}")
    print(f"Upload Complete!")
    print(f"{'='*60}")
    print(f"Total files processed: {total_files}")
    print(f"Successful uploads: {successful_uploads}")
    print(f"Failed uploads: {failed_uploads}")
    print(f"Total triples uploaded: {total_triples}")
    print(f"{'='*60}")

if __name__ == "__main__":
    import sys

    # Allow limiting number of files for testing
    max_files = None
    if len(sys.argv) > 1:
        try:
            max_files = int(sys.argv[1])
            print(f"Processing only first {max_files} files (test mode)")
        except ValueError:
            pass

    print("="*60)
    print("bioRxiv Dataset Upload to Neo4j Aura")
    print("="*60)
    print(f"Dataset path: {DATASET_PATH}")
    print(f"Neo4j URI: {NEO4J_URI}")
    print(f"API endpoint: {API_BASE_URL}")
    print("="*60)

    process_dataset(max_files)
