#!/usr/bin/env python3
"""
Test script for all three RAG query modes:
1. Traditional Graph Query (keyword-based matching in Neo4j)
2. Pure RAG (Pinecone vector search + LLM generation)
3. GraphRAG (hybrid vector + multi-hop graph traversal)
"""

import os
import requests
import json
import sys

# Configuration
BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
API_ENDPOINT = f'{BASE_URL}/api/query'

# Test queries
TEST_QUERIES = [
    "What genes are associated with cancer?",
    "Tell me about genetic variants and their effects",
    "What research has been done on protein interactions?",
]

def test_query_mode(query: str, mode: str):
    """Test a single query mode"""
    print(f"\n{'='*80}")
    print(f"Testing {mode.upper()} mode")
    print(f"Query: {query}")
    print(f"{'='*80}\n")

    try:
        response = requests.post(
            API_ENDPOINT,
            json={
                'query': query,
                'queryMode': mode
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success!")
            print(f"Answer: {result.get('answer', 'No answer')}\n")

            # Print metrics if available
            metrics = result.get('metrics', {})
            if metrics:
                print(f"Metrics:")
                print(f"  - Execution time: {metrics.get('executionTimeMs', 0):.2f}ms")
                print(f"  - Result count: {metrics.get('resultCount', 0)}")
                if 'relevanceScore' in metrics:
                    print(f"  - Relevance score: {metrics.get('relevanceScore', 0):.2f}")

            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False

def main():
    """Run all RAG mode tests"""
    print("\n" + "="*80)
    print("RAG MODES TEST SUITE")
    print("="*80)

    # Test each mode with first query
    query = TEST_QUERIES[0]
    modes = ['traditional', 'pure-rag', 'vector-search']

    results = {}
    for mode in modes:
        results[mode] = test_query_mode(query, mode)

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for mode, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{mode.upper()}: {status}")

    # Exit with appropriate code
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
