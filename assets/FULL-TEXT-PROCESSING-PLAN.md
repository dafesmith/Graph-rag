# Full-Text BioRxiv Processing Plan

## Dataset Overview

**Downloading:** `marianna13/biorxiv` Creative Commons papers
- **Total papers:** 1,000 full-text scientific papers
- **Content:** Complete research papers with full text
- **License:** Creative Commons (commercial use allowed)
- **Average size:** ~10-20 KB per paper (much larger than abstracts)

## Processing Strategy

### Challenge: Large File Sizes

Full-text papers are 10-20x larger than abstracts:
- **Abstracts:** ~1-2 KB each (what we processed earlier)
- **Full papers:** ~10-20 KB each (what we're downloading now)

### Recommended Approach

#### Option 1: Direct Processing (Best for GPU-less users)

Since individual papers are ~10-20 KB each, they can be processed directly without splitting:

```bash
# Process all 1,000 papers
python3 batch-process-chunks.py biorxiv_creative_commons/

# Estimated time: 1,000 × 30 seconds = ~8-9 hours
# Expected triples: 30,000-50,000 (assuming 30-50 per paper)
```

#### Option 2: Sample First (Recommended)

Test with a small sample first:

```bash
# Create 50-paper sample
mkdir -p biorxiv_cc_sample_50
for i in {1..50}; do
    file=$(ls biorxiv_creative_commons/ | sed -n "${i}p")
    cp "biorxiv_creative_commons/$file" biorxiv_cc_sample_50/
done

# Process sample (takes ~25 minutes)
python3 batch-process-chunks.py biorxiv_cc_sample_50/

# Expected: ~1,500-2,500 triples from 50 papers
```

#### Option 3: Split Large Papers (If needed)

If any papers are > 50 KB, split them:

```bash
# Find large papers
find biorxiv_creative_commons/ -size +50k

# Split them
for file in biorxiv_creative_commons/*.txt; do
    size=$(wc -c < "$file")
    if [ $size -gt 51200 ]; then  # 50 KB
        ./split-large-document.sh "$file" 50
    fi
done
```

## Processing Estimates

### Small Sample (10 papers)
- **Time:** ~5 minutes
- **Triples:** 300-500
- **Cost:** Minimal NVIDIA API usage

### Medium Sample (100 papers)
- **Time:** ~50 minutes
- **Triples:** 3,000-5,000
- **Cost:** Moderate NVIDIA API usage

### Full Dataset (1,000 papers)
- **Time:** ~8-9 hours
- **Triples:** 30,000-50,000
- **Cost:** Significant NVIDIA API usage (check your limits)

## Expected Knowledge Graph Content

Full-text papers will extract much richer relationships:

**Examples from genetics/medical papers:**
```
Gene X → encodes → Protein Y
Protein Y → phosphorylates → Protein Z
Drug A → inhibits → Enzyme B
Disease C → associated with → Mutation D
Treatment E → improves → Outcome F
Cell type G → expresses → Marker H
Pathway I → regulates → Process J
```

## Best Practices

1. **Start Small:** Process 10-50 papers first to verify quality
2. **Monitor Progress:** Check ArangoDB for accumulated triples
3. **API Limits:** Be aware of NVIDIA API rate limits
4. **Batch Processing:** Use the batch processor for automation
5. **Generate Embeddings:** After processing, enable semantic search

## Alternative: Use Local LLM

For processing 1,000 papers, consider local Ollama:

```bash
# Setup Ollama (requires GPU)
docker-compose up -d ollama

# Comment out NVIDIA_API_KEY in .env
# This makes the system use Ollama instead

# Rebuild
docker-compose restart app

# Process with local model (faster, no API costs)
python3 batch-process-chunks.py biorxiv_creative_commons/
```

**Benefits:**
- No API rate limits
- Potentially faster (if you have GPU)
- No API costs

## Timeline Recommendation

**Day 1:** Process 50 papers, explore knowledge graph
**Day 2:** Process 200 more papers
**Day 3:** Process remaining 750 papers (overnight)

**Total:** 1,000 papers = comprehensive biomedical knowledge graph!

## Next Steps After Download Completes

1. Check download results
2. Analyze paper sizes
3. Choose processing strategy (sample vs. full)
4. Start batch processing
5. Monitor progress
6. Generate embeddings
7. Query the knowledge graph!
