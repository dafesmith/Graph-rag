#!/bin/bash
# Script to split large documents into smaller chunks for txt2kg processing
# Usage: ./split-large-document.sh <input_file> [chunk_size_kb]

set -e

INPUT_FILE="$1"
CHUNK_SIZE_KB="${2:-50}"  # Default 50KB chunks (processes in ~20-30 seconds)

if [ -z "$INPUT_FILE" ]; then
    echo "Usage: $0 <input_file> [chunk_size_kb]"
    echo "Example: $0 large-document.txt 50"
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File '$INPUT_FILE' not found"
    exit 1
fi

# Get file info
FILE_SIZE=$(wc -c < "$INPUT_FILE")
FILE_SIZE_KB=$((FILE_SIZE / 1024))
BASENAME=$(basename "$INPUT_FILE" .txt)
OUTPUT_DIR="${BASENAME}_chunks"

echo "================================================"
echo "txt2kg Large Document Splitter"
echo "================================================"
echo "Input file: $INPUT_FILE"
echo "File size: ${FILE_SIZE_KB} KB"
echo "Chunk size: ${CHUNK_SIZE_KB} KB"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Calculate number of chunks
NUM_CHUNKS=$(( (FILE_SIZE_KB + CHUNK_SIZE_KB - 1) / CHUNK_SIZE_KB ))
echo "Will create approximately $NUM_CHUNKS chunks"
echo ""

# Split the file by lines to avoid breaking sentences
CHUNK_SIZE_BYTES=$((CHUNK_SIZE_KB * 1024))
LINES_PER_CHUNK=$((CHUNK_SIZE_BYTES / 80))  # Assume ~80 chars per line

split -l "$LINES_PER_CHUNK" "$INPUT_FILE" "$OUTPUT_DIR/${BASENAME}_chunk_"

# Rename chunks with .txt extension and sequential numbers
CHUNK_NUM=1
for chunk in "$OUTPUT_DIR"/${BASENAME}_chunk_*; do
    if [ -f "$chunk" ]; then
        NEW_NAME="${OUTPUT_DIR}/${BASENAME}_part_$(printf "%03d" $CHUNK_NUM).txt"
        mv "$chunk" "$NEW_NAME"
        CHUNK_SIZE=$(wc -c < "$NEW_NAME")
        CHUNK_SIZE_KB=$((CHUNK_SIZE / 1024))
        echo "Created: $(basename $NEW_NAME) (${CHUNK_SIZE_KB} KB)"
        CHUNK_NUM=$((CHUNK_NUM + 1))
    fi
done

echo ""
echo "================================================"
echo "✅ Successfully split into $((CHUNK_NUM - 1)) chunks"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Upload each chunk to txt2kg UI at http://localhost:3001"
echo "2. Process each chunk separately (takes ~20-30 sec per 50KB)"
echo "3. All triples will be stored in the same graph database"
echo "4. Generate embeddings after all chunks are processed"
echo ""
echo "Or process all chunks via API:"
echo "  for file in $OUTPUT_DIR/*.txt; do"
echo "    echo \"Processing \$file...\""
echo "    curl -X POST http://localhost:3001/api/extract-triples \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d \"{\\\"text\\\":\\\$(cat \\\$file | jq -Rs .),\\\"useLangChain\\\":true}\""
echo "  done"
