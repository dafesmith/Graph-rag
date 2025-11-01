# Large File Processing Guide - txt2kg

## Overview

This guide explains how to efficiently process large documents in txt2kg, which uses NVIDIA Cloud API for knowledge graph extraction.

## Performance Benchmarks

| File Size | Chunks | Processing Time | Triples Extracted | Status |
|-----------|--------|----------------|-------------------|--------|
| 800 bytes | 1 | ~16 seconds | 8 | ✅ Fast |
| 50 KB | 1 | ~20-30 seconds | ~50-100 | ✅ Optimal |
| 2.6 MB | 40+ | ~15-20 minutes | 632 | ⚠️ Slow/Timeouts |

## Recommended Approach: Split Large Files

### Method 1: Automatic Splitting (Recommended)

**Step 1: Split your large document**
```bash
cd /Users/dafesmith/Documents/repo/txt2kg/assets

# Split into 50KB chunks (optimal size)
./split-large-document.sh your-large-file.txt 50

# Or split into 100KB chunks (if you want fewer files)
./split-large-document.sh your-large-file.txt 100
```

**Step 2: Batch process all chunks**
```bash
# Automatically process all chunks and store in graph database
python3 batch-process-chunks.py your-large-file_chunks/
```

**Example Output:**
```
txt2kg Batch Processor
================================================
Chunks directory: document_chunks/
Total chunks: 52
API endpoint: http://localhost:3001
================================================

[1/52] Processing: document_part_001.txt
File size: 48.23 KB
Extracting triples using NVIDIA Nemotron...
✅ Extracted 87 triples in 23.4s
✅ Stored 87 triples in graph database

[2/52] Processing: document_part_002.txt
...

PROCESSING SUMMARY
================================================
Total chunks processed: 52
Successful: 52
Failed: 0
Total triples extracted: 4,520
Total triples stored: 4,520
Total processing time: 1,248s (20.8 minutes)
Average time per triple: 0.28s
================================================
```

### Method 2: Manual Processing via UI

1. **Split the document:**
   ```bash
   ./split-large-document.sh your-large-file.txt 50
   ```

2. **Upload each chunk to the UI:**
   - Go to http://localhost:3001
   - Upload chunks one by one using "Process Documents" tab
   - Each chunk will be processed in 20-30 seconds
   - All triples are stored in the same graph database

3. **Generate embeddings** (optional, after all chunks):
   - Click "Generate Embeddings" button in UI
   - This enables semantic similarity search

## Alternative Solutions

### Option 2: Increase Timeout Settings

If you don't want to split files, you can increase timeout limits:

**Update [frontend/lib/text-processor.ts](frontend/lib/text-processor.ts)**
```typescript
// Line ~94 - Increase NVIDIA API timeout
const response = await this.llm!.invoke(prompt, {
  timeout: 300000  // Increase from default to 5 minutes
});
```

**Update [.env](.env)**
```bash
# Increase Node.js timeouts
HTTP_TIMEOUT=3600000  # 1 hour
REQUEST_TIMEOUT=3600000  # 1 hour
```

Then rebuild:
```bash
docker-compose down
docker-compose build app
docker-compose up -d
```

⚠️ **Note:** This doesn't solve the slow sequential processing issue.

### Option 3: Use Local LLM (Faster for Large Volumes)

If you have a GPU, local models can be faster for large-scale processing:

**Setup Ollama (requires NVIDIA GPU):**
```bash
# Uncomment Ollama service in docker-compose.yml
# Update .env to prioritize Ollama:
OLLAMA_BASE_URL=http://ollama:11434/v1
OLLAMA_MODEL=llama3.1:8b
# Comment out NVIDIA_API_KEY to use Ollama
```

**Rebuild and restart:**
```bash
docker-compose down
docker-compose up -d ollama
docker-compose restart app
```

**Performance comparison:**
- NVIDIA Cloud API: ~25-30s per chunk (network latency)
- Local Ollama (with GPU): ~10-15s per chunk
- Local vLLM (with GPU): ~5-10s per chunk

### Option 4: Adjust Chunk Size in Code

You can modify the chunk size in the code:

**Edit [frontend/lib/text-processor.ts](frontend/lib/text-processor.ts)** (Line ~188):
```typescript
// Change chunk size from 64000 to smaller value
const chunkSize = 32000; // Smaller chunks = faster processing
```

**Rebuild:**
```bash
cd /Users/dafesmith/Documents/repo/txt2kg/assets
docker build -f deploy/app/Dockerfile -t compose-app:latest .
docker-compose restart app
```

## Best Practices

### For Production Use:

1. **File Size Guidelines:**
   - Small files (< 50 KB): Upload directly ✅
   - Medium files (50-500 KB): Split into 50-100 KB chunks
   - Large files (> 500 KB): Split into 50 KB chunks for optimal processing

2. **Batch Processing:**
   - Process during off-peak hours
   - Use the batch processor script for automation
   - Monitor progress in Docker logs: `docker logs txt2kg-app -f`

3. **Cost Optimization (NVIDIA Cloud API):**
   - NVIDIA API has rate limits and potential costs
   - Split files to stay within limits
   - Consider local LLM for large-scale operations

4. **Quality vs Speed:**
   - Smaller chunks: Faster, but may miss cross-chunk relationships
   - Larger chunks: Slower, but better context for extraction
   - Optimal: 50-100 KB chunks balances both

## Troubleshooting

### Timeouts Still Occurring?

```bash
# Check NVIDIA API status
curl -X POST http://localhost:3001/api/extract-triples \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test", "useLangChain": true}'

# If errors, check logs
docker logs txt2kg-app --tail 50
```

### Slow Processing?

1. Check network latency to NVIDIA API
2. Consider switching to local Ollama if you have GPU
3. Use smaller chunk sizes (25-30 KB)

### Out of Memory?

```bash
# Increase Node.js memory limit in docker-compose.yml:
environment:
  - NODE_OPTIONS=--max-old-space-size=4096
```

## Example Workflow

**Process a 5 MB document:**

```bash
# 1. Split into chunks
./split-large-document.sh large-doc.txt 50
# Output: 100 chunks in large-doc_chunks/

# 2. Batch process
python3 batch-process-chunks.py large-doc_chunks/
# Time: ~50 minutes (30s per chunk × 100)
# Result: ~10,000 triples stored

# 3. Generate embeddings (in UI)
# Go to http://localhost:3001
# Click "Generate Embeddings"

# 4. Query your knowledge graph
# Go to http://localhost:3001/rag
# Ask questions about the document
```

## Summary

✅ **Best for most users:** Split files into 50KB chunks + batch processor
✅ **Best for GPU users:** Local Ollama + larger chunks
✅ **Best for small files:** Upload directly to UI (< 50 KB)

## Files Created

- [split-large-document.sh](split-large-document.sh) - Automatic file splitter
- [batch-process-chunks.py](batch-process-chunks.py) - Automated batch processor
- This guide: [LARGE-FILES-GUIDE.md](LARGE-FILES-GUIDE.md)
