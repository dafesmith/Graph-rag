#!/usr/bin/env python3
"""
Test Neo4j Aura connection
"""
from neo4j import GraphDatabase

# Neo4j Aura credentials
NEO4J_URI = "neo4j+s://50a0f5b5.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "7cFtku457GEwz2UbNcC9LRWkLRCQaqxqPuSfUmPE--Q"

def test_connection():
    """Test Neo4j connection"""
    print("="*60)
    print("Testing Neo4j Aura Connection")
    print("="*60)
    print(f"URI: {NEO4J_URI}")
    print(f"User: {NEO4J_USER}")
    print("="*60)

    try:
        # Create driver
        print("\n1. Creating driver...")
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        print("   ✓ Driver created")

        # Verify connection
        print("\n2. Verifying connection...")
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            value = result.single()["test"]
            assert value == 1
            print("   ✓ Connection verified")

        # Get current stats
        print("\n3. Getting database stats...")
        with driver.session() as session:
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = node_result.single()["count"]

            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()["count"]

            print(f"   Current nodes: {node_count:,}")
            print(f"   Current relationships: {rel_count:,}")

        # Close driver
        driver.close()
        print("\n✓ Connection test successful!")
        print("="*60)
        return True

    except Exception as e:
        print(f"\n✗ Connection test failed!")
        print(f"Error: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_connection()
