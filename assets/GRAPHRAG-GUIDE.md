# GraphRAG (G-Retriever) Complete Setup Guide

## Table of Contents
1. [What is GraphRAG?](#what-is-graphrag)
2. [Prerequisites](#prerequisites)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Data Preparation](#data-preparation)
6. [Training the Model](#training-the-model)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## What is GraphRAG?

**GraphRAG** (Graph Retrieval-Augmented Generation) combines:
- **G-Retriever**: Graph Neural Network (GNN) for intelligent graph traversal
- **RAG**: Retrieval-Augmented Generation for context-aware answers
- **LLM**: Large Language Model for natural language synthesis

### Comparison with Other Query Types

| Feature | Pure RAG | Traditional Graph | GraphRAG |
|---------|----------|------------------|----------|
| **Technology** | Vector search + LLM | Graph database queries | GNN + Graph + LLM |
| **Intelligence** | Semantic similarity | Exact matches | AI-powered reasoning |
| **Setup** | Easy | Very easy | Complex (requires training) |
| **Speed** | Fast | Very fast | Medium |
| **Quality** | Good | Basic | Excellent (when trained) |
| **GPU Required** | No | No | **Yes (for training)** |

**When to use GraphRAG**:
- ✅ You have a large knowledge graph (1000+ nodes)
- ✅ You have question-answer training data
- ✅ You have GPU resources (16GB+ VRAM)
- ✅ You need the highest quality answers
- ❌ NOT for small graphs (<100 nodes)
- ❌ NOT for quick prototyping

---

## Prerequisites

### Required Knowledge
- Basic Python programming
- Understanding of machine learning concepts
- Familiarity with command line
- Docker basics (optional but helpful)

### Required Services
- ✅ ArangoDB running (knowledge graph database)
- ✅ NVIDIA API key (for LLMJudge evaluation)
- ✅ Knowledge graph data (minimum 100+ triples)
- ✅ Question-answer dataset (minimum 100 pairs)

---

## System Requirements

### Minimum (Training on GPU Cloud)
- **Local Machine**: Mac/Windows/Linux (any OS)
- **Cloud GPU**: NVIDIA GPU with 16GB+ VRAM
  - RunPod: $0.34/hour (RTX A6000)
  - Lambda Labs: $0.50/hour (RTX 4090)
  - Vast.ai: $0.20-0.40/hour
- **RAM**: 16GB+
- **Disk Space**: 50GB+

### Recommended (Local GPU Training)
- **GPU**: NVIDIA RTX 3060 Ti (16GB) or better
- **CPU**: 8+ cores
- **RAM**: 32GB+
- **Disk Space**: 100GB+
- **OS**: Linux (Ubuntu 20.04+) or Windows 11 with WSL2

### Not Recommended
- ❌ Mac CPU-only (training takes weeks)
- ❌ Systems with <8GB VRAM
- ❌ Integrated graphics (Intel/AMD)

---

## Installation

### Step 1: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv ~/graphrag_env
source ~/graphrag_env/bin/activate  # On Windows: ~/graphrag_env/Scripts/activate

# Install PyTorch (choose based on your system)

# For NVIDIA GPU (Linux/Windows):
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For Mac (CPU only - NOT recommended for training):
pip3 install torch torchvision torchaudio

# For CPU-only (any system - NOT recommended for training):
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install PyTorch Geometric
pip3 install torch-geometric

# Install other dependencies
pip3 install tqdm python-arango transformers numpy
```

**Verify installation**:
```bash
python3 -c "
import torch
import torch_geometric
print(f'✅ PyTorch {torch.__version__}')
print(f'✅ PyTorch Geometric {torch_geometric.__version__}')
print(f'✅ CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'✅ GPU: {torch.cuda.get_device_name(0)}')
"
```

Expected output (with GPU):
```
✅ PyTorch 2.6.0+cu121
✅ PyTorch Geometric 2.6.0
✅ CUDA available: True
✅ GPU: NVIDIA RTX 4090
```

### Step 2: Verify ArangoDB Connection

```bash
# Test connection to your txt2kg ArangoDB
python3 -c "
from arango import ArangoClient

client = ArangoClient(hosts='http://localhost:8529')
db = client.db('txt2kg', username='', password='')

# Count entities and relationships
entities = db.collection('entities').count()
relationships = db.collection('relationships').count()

print(f'✅ Connected to ArangoDB')
print(f'📊 Entities: {entities}')
print(f'📊 Relationships: {relationships}')

if relationships < 100:
    print('⚠️  WARNING: You have fewer than 100 triples.')
    print('   GraphRAG works best with 1000+ triples.')
"
```

---

## Data Preparation

### Step 1: Preprocess Knowledge Graph

Navigate to the GNN scripts directory:
```bash
cd /path/to/Graph-rag/assets/scripts/gnn
```

**Option A: Use Existing ArangoDB Data**
```bash
python3 preprocess_data.py \
  --use_arango \
  --arango_url "http://localhost:8529" \
  --arango_db "txt2kg" \
  --output_dir ./output
```

**Option B: Generate from Documents**
```bash
# First, ensure you have documents uploaded to txt2kg
# Then run preprocessing without --use_arango flag
python3 preprocess_data.py --output_dir ./output
```

**Expected output**:
```
Loading dataset from ArangoDB...
Found 92 entities and 66 relationships
Creating knowledge graph...
Generating embeddings...
Splitting into train/val/test sets...
✅ Dataset saved to ./output/tech_qa.pt
  Train: 40 samples
  Validation: 13 samples
  Test: 13 samples
```

### Step 2: Prepare Question-Answer Dataset

The preprocessing script expects a specific format. Create a file `qa_dataset.json`:

```json
{
  "questions": [
    "What is the CEO of Apple?",
    "Who founded Apple Inc?",
    "What products does Apple make?"
  ],
  "answers": [
    "Tim Cook is the CEO of Apple Inc.",
    "Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne.",
    "Apple makes iPhone, iPad, and MacBook."
  ]
}
```

**For BioRxiv/Scientific datasets**:
```json
{
  "questions": [
    "What is the relationship between BRCA1 and breast cancer?",
    "How does NQO1 affect oral submucous fibrosis?",
    "What proteins are associated with Alzheimer's disease?"
  ],
  "answers": [
    "BRCA1 is associated with breast cancer susceptibility.",
    "NQO1 c609t polymorphism is associated with oral submucous fibrosis.",
    "APOE is associated with Alzheimer's disease risk."
  ]
}
```

---

## Training the Model

### Quick Start (Default Settings)

```bash
cd /path/to/Graph-rag/assets/scripts/gnn

# Train with default settings
python3 train_test_gnn.py \
  --output_dir ./output \
  --NV_NIM_KEY "your-nvidia-api-key"
```

### Advanced Training Options

```bash
python3 train_test_gnn.py \
  --output_dir ./output \
  --NV_NIM_KEY "your-nvidia-api-key" \
  --gnn_hidden_channels 2048 \
  --num_gnn_layers 6 \
  --epochs 5 \
  --batch_size 2 \
  --lr 5e-6 \
  --llm_generator_mode "lora"
```

**Parameter Guide**:

| Parameter | Default | Description | Recommended Range |
|-----------|---------|-------------|-------------------|
| `gnn_hidden_channels` | 1024 | GNN hidden layer size | 512-2048 |
| `num_gnn_layers` | 4 | Number of GNN layers | 3-8 |
| `epochs` | 2 | Training epochs | 2-10 |
| `batch_size` | 1 | Training batch size | 1-4 |
| `eval_batch_size` | 2 | Evaluation batch size | 2-8 |
| `lr` | 1e-5 | Learning rate | 1e-6 to 1e-4 |
| `llm_generator_mode` | full | LLM mode | frozen/lora/full |

**LLM Generator Modes**:
- `frozen`: LLM weights frozen (fastest, less memory)
- `lora`: LoRA fine-tuning (balanced)
- `full`: Full fine-tuning (best quality, most memory)

### Training Time Estimates

**With RTX 4090 (24GB)**:
- Small dataset (100 triples, 2 epochs): ~30 minutes
- Medium dataset (1000 triples, 5 epochs): ~2-4 hours
- Large dataset (10000 triples, 10 epochs): ~8-24 hours

**With RTX 3060 Ti (16GB)**:
- Small dataset: ~1 hour
- Medium dataset: ~4-8 hours
- Large dataset: ~24-48 hours

**With CPU (Mac/No GPU)**:
- ⚠️ NOT RECOMMENDED - will take days/weeks

### Monitoring Training

The script outputs training progress:
```
Epoch: 1|5, Train Loss: 2.4567
Epoch: 1|5, Val Loss: 2.1234
Epoch: 2|5, Train Loss: 1.8901
Epoch: 2|5, Val Loss: 1.7654
...
✅ Model saved to ./output/tech-qa-model.pt
Testing...
Avg marlin accuracy = 0.85
Test results saved to ./output/test_results.txt
```

### Evaluation Only (Skip Training)

If you already have a trained model:
```bash
python3 train_test_gnn.py \
  --output_dir ./output \
  --NV_NIM_KEY "your-nvidia-api-key" \
  --eval_only
```

---

## Deployment

### Step 1: Verify Trained Model

```bash
ls -lh ./output/tech-qa-model.pt

# Should show file size (typically 2-8GB)
```

### Step 2: Deploy GNN Model Service

The txt2kg project includes a GNN model service. Deploy it:

```bash
cd /path/to/Graph-rag/assets/deploy/services/gnn_model

# Build Docker image
docker build -t txt2kg-gnn:latest .

# Run the service
docker run -d \
  -p 8090:8090 \
  -v /path/to/output:/models \
  --name txt2kg-gnn \
  txt2kg-gnn:latest
```

### Step 3: Test the Deployed Model

```bash
# Test health endpoint
curl http://localhost:8090/health

# Test inference
curl -X POST http://localhost:8090/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the CEO of Apple?",
    "graph_data": {...}
  }'
```

### Step 4: Integrate with Frontend

Update `frontend/app/api/enhanced-query/route.ts` to use the GNN service when `queryMode === 'graphrag'`.

---

## Troubleshooting

### Common Issues

#### 1. CUDA Out of Memory
```
RuntimeError: CUDA out of memory
```

**Solutions**:
- Reduce `batch_size` to 1
- Reduce `gnn_hidden_channels` to 512
- Use `llm_generator_mode: "frozen"`
- Use gradient checkpointing

#### 2. No Training Data
```
FileNotFoundError: Dataset file not found
```

**Solution**: Run preprocessing first:
```bash
python3 preprocess_data.py --use_arango --output_dir ./output
```

#### 3. ArangoDB Connection Failed
```
ConnectionError: Cannot connect to ArangoDB
```

**Solutions**:
- Verify ArangoDB is running: `docker ps | grep arango`
- Check connection parameters
- Ensure txt2kg database exists

#### 4. Slow Training on CPU
```
Training is extremely slow...
```

**Solution**: This is expected on CPU. Use GPU or cloud GPU service.

#### 5. Model Not Learning (Loss Not Decreasing)
```
Epoch: 5|5, Train Loss: 5.4321 (not improving)
```

**Solutions**:
- Check your question-answer dataset quality
- Increase epochs to 10+
- Adjust learning rate (try 5e-6 or 5e-5)
- Ensure sufficient training data (100+ pairs)

---

## FAQ

### Q1: How much training data do I need?
**A**: Minimum 100 question-answer pairs. Recommended: 1000+ pairs for good performance.

### Q2: Can I train on Mac M1/M2?
**A**: Technically yes, but it will be VERY slow (days/weeks). Use cloud GPU instead.

### Q3: How long does training take?
**A**: With RTX 4090: 30 min - 4 hours. With RTX 3060: 1-8 hours. Without GPU: Don't.

### Q4: Do I need all my data in ArangoDB first?
**A**: Yes for the graph structure. The preprocessing script extracts triples from ArangoDB.

### Q5: Can I use a different LLM?
**A**: Yes! Change `llm_generator_name` parameter to any HuggingFace model.

### Q6: What if I only have 66 triples like in the example?
**A**: GraphRAG may not provide significant benefit over Traditional Graph queries. Consider adding more documents first.

### Q7: Is GraphRAG better than Pure RAG?
**A**: For graph-structured data: Yes. For general documents: Pure RAG might be simpler and sufficient.

### Q8: Can I use this in production?
**A**: Yes, but it requires proper deployment, monitoring, and model versioning. This is an advanced feature.

### Q9: How do I update the model with new data?
**A**: Re-run preprocessing and training with updated ArangoDB data.

### Q10: What's the cost to train on cloud GPU?
**A**: $5-50 depending on dataset size and GPU choice (RunPod/Lambda Labs).

---

## Additional Resources

- **PyTorch Geometric Docs**: https://pytorch-geometric.readthedocs.io/
- **G-Retriever Paper**: https://arxiv.org/abs/2402.07630
- **txt2kg Issues**: https://github.com/anthropics/txt2kg/issues
- **NVIDIA NIM**: https://build.nvidia.com/

---

## Cost Estimates

### Cloud GPU Training Costs

| Service | GPU | VRAM | Cost/Hour | Small Dataset | Large Dataset |
|---------|-----|------|-----------|---------------|---------------|
| Vast.ai | RTX 3090 | 24GB | $0.20 | ~$0.50 | ~$4 |
| RunPod | RTX A6000 | 48GB | $0.34 | ~$1 | ~$7 |
| Lambda Labs | RTX 4090 | 24GB | $0.50 | ~$1.50 | ~$10 |
| Google Colab Pro+ | A100 | 40GB | $50/month | Unlimited | Unlimited |

### Local GPU Hardware Costs (One-time)

| GPU | VRAM | New Price | Used Price | Suitable For |
|-----|------|-----------|------------|--------------|
| RTX 3060 Ti | 16GB | $500 | $300 | Small-medium datasets |
| RTX 4070 Ti | 12GB | $800 | $600 | Medium datasets |
| RTX 4080 | 16GB | $1200 | $900 | Large datasets |
| RTX 4090 | 24GB | $2000 | $1500 | Any dataset |

---

## Summary

**GraphRAG is powerful but complex**. Before investing time:

1. ✅ **Do you have a large knowledge graph?** (1000+ nodes)
2. ✅ **Do you have training data?** (100+ QA pairs)
3. ✅ **Do you have GPU access?** (16GB+ VRAM)
4. ✅ **Is quality critical?** (worth the complexity)

**If not all YES**: Use Traditional Graph + NVIDIA API instead.

**If all YES**: Follow this guide and expect 1-2 days of setup + training time.

---

*Generated for txt2kg - NVIDIA Knowledge Graph Builder*
*Last Updated: November 2025*
