#!/usr/bin/env python3
"""
Upload bioRxiv dataset directly to Neo4j Aura
Uses neo4j-driver to connect directly without API
"""
import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Tuple
import time

try:
    from neo4j import GraphDatabase
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False
    print("neo4j-driver not installed. Install with: pip install neo4j")

# Neo4j Aura credentials
NEO4J_URI = "neo4j+s://50a0f5b5.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "7cFtku457GEwz2UbNcC9LRWkLRCQaqxqPuSfUmPE--Q"

# NVIDIA API for triple extraction
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Dataset path
DATASET_PATH = "/Users/dafesmith/Documents/repo/Graph-rag/assets/examples/biorxiv_genetics_genomics"

class Neo4jUploader:
    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection"""
        if not HAS_NEO4J:
            raise Exception("neo4j-driver not installed")

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"✓ Connected to Neo4j at {uri}")

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()

    def verify_connection(self):
        """Verify Neo4j connection works"""
        with self.driver.session() as session:
            result = session.run("RETURN 1 as test")
            value = result.single()["test"]
            assert value == 1
            print("✓ Neo4j connection verified")

    def create_indices(self):
        """Create indices for better performance"""
        with self.driver.session() as session:
            session.run("CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.name)")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS NOT NULL")
            print("✓ Created indices and constraints")

    def upload_triples(self, triples: List[Dict], document_name: str) -> int:
        """Upload triples to Neo4j"""
        if not triples:
            return 0

        with self.driver.session() as session:
            count = 0
            for triple in triples:
                try:
                    # Normalize values
                    subject = triple.get('subject', '').strip()
                    predicate = triple.get('predicate', '').strip()
                    obj = triple.get('object', '').strip()

                    if not subject or not predicate or not obj:
                        continue

                    # Create nodes and relationship
                    session.run("""
                        MERGE (s:Entity {name: $subject})
                        MERGE (o:Entity {name: $object})
                        MERGE (s)-[r:RELATIONSHIP {type: $predicate}]->(o)
                        ON CREATE SET r.source = $source
                        ON MATCH SET r.source = $source
                    """, subject=subject, object=obj, predicate=predicate, source=document_name)
                    count += 1
                except Exception as e:
                    print(f"    Error uploading triple: {e}")
                    continue

            return count

    def get_stats(self) -> Tuple[int, int]:
        """Get node and relationship counts"""
        with self.driver.session() as session:
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = node_result.single()["count"]

            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()["count"]

            return node_count, rel_count

def extract_triples_with_nvidia(text: str, document_name: str) -> List[Dict]:
    """Extract triples using NVIDIA API"""
    if not NVIDIA_API_KEY:
        print("    Warning: NVIDIA_API_KEY not set, cannot extract triples")
        return []

    prompt = f"""Extract knowledge graph triples from the following scientific text.
Return ONLY a JSON array of triples in the format: {{"subject": "...", "predicate": "...", "object": "..."}}

Text: {text[:2000]}

Output (JSON array only):"""

    try:
        response = requests.post(
            NVIDIA_API_URL,
            headers={
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta/llama-3.1-70b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 1024
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']

            # Try to parse JSON from response
            # Clean up response (remove markdown code blocks if present)
            content = content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            triples = json.loads(content)
            if isinstance(triples, list):
                return triples
            return []
        else:
            print(f"    NVIDIA API error: {response.status_code}")
            return []
    except Exception as e:
        print(f"    Error calling NVIDIA API: {e}")
        return []

def simple_triple_extraction(text: str, document_name: str) -> List[Dict]:
    """Simple rule-based triple extraction as fallback"""
    # This is a very basic implementation - just for demonstration
    # In production, you'd want to use NLP or LLM-based extraction
    triples = []

    # Extract some basic patterns
    sentences = text.split('.')[:5]  # First 5 sentences

    for sentence in sentences:
        words = sentence.strip().split()
        if len(words) >= 3:
            # Very simple: subject-verb-object from each sentence
            subject = words[0]
            predicate = "MENTIONS"
            obj = words[-1]

            triples.append({
                "subject": subject,
                "predicate": predicate,
                "object": obj
            })

    return triples[:10]  # Limit to 10 triples per doc

def read_document(file_path: str) -> str:
    """Read a document from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def process_dataset(uploader: Neo4jUploader, max_files: int = None, use_nvidia: bool = True):
    """Process all files in the dataset"""
    dataset_dir = Path(DATASET_PATH)
    txt_files = sorted(dataset_dir.glob("*.txt"))

    if max_files:
        txt_files = txt_files[:max_files]

    total_files = len(txt_files)
    print(f"\nFound {total_files} files to process")
    print("="*60)

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
                print(f"  ✗ Skipping (text too short: {len(text)} chars)")
                continue

            print(f"  Document size: {len(text)} chars")

            # Extract triples
            print(f"  Extracting triples...")
            if use_nvidia and NVIDIA_API_KEY:
                triples = extract_triples_with_nvidia(text, file_path.name)
            else:
                triples = simple_triple_extraction(text, file_path.name)

            if not triples:
                print(f"  ✗ No triples extracted")
                failed_uploads += 1
                continue

            print(f"  Extracted {len(triples)} triples")

            # Upload to Neo4j
            print(f"  Uploading to Neo4j...")
            uploaded_count = uploader.upload_triples(triples, file_path.name)

            if uploaded_count > 0:
                print(f"  ✓ Successfully uploaded {uploaded_count} triples")
                successful_uploads += 1
                total_triples += uploaded_count
            else:
                print(f"  ✗ Failed to upload")
                failed_uploads += 1

            # Progress report every 10 files
            if i % 10 == 0:
                nodes, rels = uploader.get_stats()
                print(f"\n--- Progress Report ---")
                print(f"Files processed: {i}/{total_files}")
                print(f"Total nodes in DB: {nodes:,}")
                print(f"Total relationships in DB: {rels:,}")
                print(f"----------------------")
                time.sleep(0.5)

        except Exception as e:
            print(f"  ✗ Error processing file: {e}")
            failed_uploads += 1
            continue

    # Final stats
    nodes, rels = uploader.get_stats()

    print(f"\n{'='*60}")
    print(f"Upload Complete!")
    print(f"{'='*60}")
    print(f"Total files processed: {total_files}")
    print(f"Successful uploads: {successful_uploads}")
    print(f"Failed uploads: {failed_uploads}")
    print(f"Total triples uploaded: {total_triples}")
    print(f"")
    print(f"Final Neo4j Stats:")
    print(f"  Nodes: {nodes:,}")
    print(f"  Relationships: {rels:,}")
    print(f"{'='*60}")

if __name__ == "__main__":
    import sys

    # Parse arguments
    max_files = None
    use_nvidia = True

    if len(sys.argv) > 1:
        try:
            max_files = int(sys.argv[1])
            print(f"Processing only first {max_files} files (test mode)")
        except ValueError:
            pass

    if "--no-nvidia" in sys.argv:
        use_nvidia = False
        print("Using simple triple extraction (not NVIDIA API)")

    print("="*60)
    print("bioRxiv Dataset Upload to Neo4j Aura")
    print("="*60)
    print(f"Dataset path: {DATASET_PATH}")
    print(f"Neo4j URI: {NEO4J_URI}")
    print(f"Neo4j User: {NEO4J_USER}")

    if use_nvidia and NVIDIA_API_KEY:
        print(f"Triple extraction: NVIDIA API")
    else:
        print(f"Triple extraction: Simple rule-based")

    print("="*60)

    try:
        # Initialize Neo4j uploader
        uploader = Neo4jUploader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

        # Verify connection
        uploader.verify_connection()

        # Create indices
        uploader.create_indices()

        # Get initial stats
        nodes, rels = uploader.get_stats()
        print(f"\nInitial Neo4j Stats:")
        print(f"  Nodes: {nodes:,}")
        print(f"  Relationships: {rels:,}")

        # Process dataset
        process_dataset(uploader, max_files, use_nvidia)

        # Close connection
        uploader.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
