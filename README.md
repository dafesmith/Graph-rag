# Dafe Graphs - Enterprise Knowledge Graph Builder

> Transform unstructured documents into interactive knowledge graphs using NVIDIA AI, advanced RAG, and production-ready graph databases

[![GitHub](https://img.shields.io/badge/GitHub-dafesmith%2FGraph--rag-blue)](https://github.com/dafesmith/Graph-rag)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-Cloud%20API-76B900)](https://build.nvidia.com)
[![Live Demo](https://img.shields.io/badge/demo-Railway-blueviolet)](https://dafe-graphs-frontend-production.up.railway.app)

---

## 🎯 Overview

**Dafe Graphs** is an enterprise-ready knowledge graph construction and querying system that leverages NVIDIA NIM APIs to extract entities, relationships, and insights from unstructured documents. Built with Next.js 15, Neo4j, and Docker, it provides a complete pipeline from document processing to interactive 2D/3D graph visualization and advanced RAG querying.

### ✅ Current Status: Production-Ready

**Live Demo**: https://dafe-graphs-frontend-production.up.railway.app

This system has been tested and verified with:
- **1,200+ nodes** with clean entity extraction from Game of Thrones dataset
- **NVIDIA Cloud API** integrated (`meta/llama-3.1-8b-instruct` for extraction and querying)
- **Three RAG modes** fully operational (Traditional, Pure RAG, GraphRAG)
- **Neo4j Aura** cloud database with persistent storage
- **2D and 3D visualization** with interactive exploration
- **Railway deployment** with Docker containerization

---

## 🚀 Key Features

### 🧠 Advanced Knowledge Graph Construction

- **AI-Powered Triple Extraction**: Extract subject-predicate-object relationships using NVIDIA LLMs
- **Multiple LLM Support**:
  - NVIDIA Cloud API (production, no GPU required)
  - Local LLMs via Ollama/vLLM (enterprise self-hosted)
  - Custom model integration
- **LangChain Integration**: Advanced extraction with LLMGraphTransformer
- **Smart Chunking**: Automatically handle large documents
- **Batch Processing**: Process thousands of documents with Python scripts

### 📊 Three Powerful Query Modes

1. **Traditional Graph Query** - Cypher-based keyword matching (fastest)
2. **Pure RAG** - Vector similarity search + LLM generation
3. **GraphRAG** - Hybrid approach: vector search + multi-hop graph traversal + LLM synthesis

### 🗄️ Enterprise Data Management

- **Graph Databases**:
  - Neo4j (primary) - Cloud (Neo4j Aura) or self-hosted
  - ArangoDB (optional alternative)
- **Vector Database**:
  - Pinecone local instance for embeddings
  - NVIDIA embeddings (4096 dimensions)
- **Supported Formats**: TXT, PDF, CSV, JSON, Markdown

### 🎨 Interactive Visualization

- **2D Graph Viewer**:
  - Force-directed, hierarchical, and radial layouts
  - Real-time search and filtering
  - Node highlighting and exploration
- **3D Graph Viewer**:
  - Immersive 3D exploration with react-force-graph-3d
  - Camera controls and zoom
  - Physics-based layout
- **Export Options**: JSON, CSV, PNG

### 🔒 Enterprise-Ready Features

- **localStorage Caching**: Smart version control and automatic cleanup
- **Database Connection Testing**: Real-time health checks
- **Railway Deployment**: Production-ready cloud hosting
- **Docker Containerization**: Complete environment isolation
- **Environment Configuration**: Flexible settings management

---

## 📊 What You Get

A complete end-to-end knowledge graph system:

| Feature | Description | Status |
|---------|-------------|--------|
| **Document Upload** | Web UI for uploading documents | ✅ Working |
| **Triple Extraction** | NVIDIA LLM-powered extraction | ✅ Tested |
| **Graph Storage** | Neo4j Aura cloud database | ✅ Production |
| **Vector Embeddings** | NVIDIA 4096-dim embeddings | ✅ Available |
| **Traditional Query** | Fast Cypher-based search | ✅ Working |
| **Pure RAG** | Semantic vector search + LLM | ✅ Working |
| **GraphRAG** | Hybrid vector + graph traversal | ✅ Working |
| **2D Visualization** | Interactive graph explorer | ✅ Working |
| **3D Visualization** | Immersive 3D graph view | ✅ Working |
| **Batch Processing** | Automated bulk document upload | ✅ Available |
| **Export** | JSON, CSV, PNG export | ✅ Working |

---

## 🛠️ Quick Start

### Prerequisites

- **Docker** & **Docker Compose** installed
- **NVIDIA API Key** (get free at https://build.nvidia.com)
- **8 GB RAM minimum** (16 GB recommended)
- **Neo4j Aura account** (free tier available) OR local Neo4j instance

### Installation

```bash
# Clone the repository
git clone https://github.com/dafesmith/Graph-rag.git
cd Graph-rag/assets

# Configure environment
cp .env.example .env

# Edit .env and add:
# - NVIDIA_API_KEY
# - NEO4J_URI (optional, uses demo DB by default)
# - NEO4J_USER
# - NEO4J_PASSWORD

# Start all services
docker-compose up -d

# Wait for services to be ready (~30 seconds)
docker logs -f dafe-graphs-frontend
```

### Access the Application

**Web Interface**: http://localhost:3001
- Upload documents via drag-and-drop
- Extract triples with AI
- Visualize knowledge graphs in 2D/3D
- Query with three RAG modes

**Neo4j Browser** (if running locally): http://localhost:7474

### First Test

Try the built-in extraction:

```bash
# Test triple extraction API
curl -X POST http://localhost:3001/api/extract-triples \
  -H "Content-Type": "application/json" \
  -d '{
    "text": "Apple Inc. was founded by Steve Jobs in 1976. The company is headquartered in Cupertino, California.",
    "useLangChain": true
  }'
```

Expected: 5-8 triples extracted in ~10-20 seconds

---

## 📚 Documentation

### Core Guides

- **[ENTERPRISE-ARCHITECTURE.md](ENTERPRISE-ARCHITECTURE.md)**: Enterprise deployment for healthcare & finance
  - Local LLM architecture
  - HIPAA/PCI-DSS compliance
  - GPU optimization strategies
  - On-premise deployment options

- **[RAILWAY-DEPLOYMENT.md](assets/RAILWAY-DEPLOYMENT.md)**: Cloud deployment guide
  - Railway setup instructions
  - Environment configuration
  - Database connection
  - Monitoring and logs

- **[GRAPHRAG-GUIDE.md](assets/GRAPHRAG-GUIDE.md)**: RAG implementation deep-dive
  - Traditional vs Pure RAG vs GraphRAG
  - Query strategies
  - Performance optimization

### Additional Documentation

- **[KNOWLEDGE-GRAPHS-DEEP-DIVE.md](assets/KNOWLEDGE-GRAPHS-DEEP-DIVE.md)**: Knowledge graph concepts
- **[NEO4J_INVESTIGATION_REPORT.md](assets/NEO4J_INVESTIGATION_REPORT.md)**: Neo4j integration details
- **[DOCUMENTATION-INDEX.md](assets/DOCUMENTATION-INDEX.md)**: Complete documentation index

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     Web Interface (Next.js 15)                      │
│                   https://dafe-graphs.railway.app                   │
└──────────────┬────────────────────────────────────┬────────────────┘
               │                                    │
               ▼                                    ▼
┌───────────────────────────┐      ┌───────────────────────────────┐
│    NVIDIA Cloud API       │      │   Neo4j Aura (Graph DB)       │
│                           │      │   - Nodes (entities)          │
│  - LLM Inference          │      │   - Relationships (edges)     │
│  - Triple Extraction      │      │   - Cypher queries            │
│  - Text Generation        │      │   - 1,200+ nodes              │
│  - Embeddings (4096-dim)  │      └───────────────────────────────┘
└───────────────────────────┘                     │
               │                                    │
               ▼                                    ▼
┌───────────────────────────┐      ┌───────────────────────────────┐
│   Pinecone (Vector DB)    │      │    RAG Service                │
│   - Local instance        │      │    - Traditional Query        │
│   - Semantic search       │      │    - Pure RAG                 │
│   - Fast similarity       │      │    - GraphRAG                 │
└───────────────────────────┘      └───────────────────────────────┘
```

### Technology Stack

**Frontend**
- Next.js 15.2.4 with App Router
- React 19 with TypeScript
- TailwindCSS for styling
- shadcn/ui components
- D3.js for 2D graphs
- react-force-graph-3d for 3D visualization

**Backend Services**
- NVIDIA NIM API for LLM inference
- Neo4j for graph storage
- Pinecone for vector search
- LangChain for RAG orchestration

**Deployment**
- Docker & Docker Compose
- Railway cloud platform
- Neo4j Aura cloud database

---

## 📊 Testing & Validation

### Verified Production Data

**Current Deployment** (as of latest update):
- **Database**: Neo4j Aura (neo4j+s://50a0f5b5.databases.neo4j.io)
- **Nodes**: 1,200+ clean entities (Game of Thrones dataset)
- **Relationships**: 1,326 relationships
- **Processing Quality**: High-quality extraction with NVIDIA API

**Sample Knowledge Graph Triples**:
```
Eddard Stark → is_lord_of → Winterfell
Jon Snow → is_member_of → Night's Watch
Daenerys Targaryen → has_dragon → Drogon
Tyrion Lannister → is_hand_of → Daenerys Targaryen
```

### RAG Query Testing

All three query modes tested and operational:
- ✅ **Traditional**: Fast keyword-based graph queries
- ✅ **Pure RAG**: Vector similarity + LLM generation
- ✅ **GraphRAG**: Hybrid vector + multi-hop reasoning

---

## 🔧 Batch Processing

### Direct Neo4j Upload

Process documents and upload directly to Neo4j:

```bash
cd assets

# Upload 10 papers (test)
python3 upload_biorxiv_direct.py 10

# Upload 100 papers with NVIDIA extraction (recommended)
python3 upload_biorxiv_direct.py 100

# Upload without NVIDIA (faster, lower quality)
python3 upload_biorxiv_direct.py 100 --no-nvidia

# Options:
# - Automatic triple extraction
# - Direct Neo4j storage
# - Progress tracking
# - Error handling
```

### Expected Performance

| Papers | Extraction Method | Time | Triples/Paper | Quality |
|--------|------------------|------|---------------|---------|
| 10 | NVIDIA API | ~5 min | 8-12 | High |
| 100 | NVIDIA API | ~50 min | 8-12 | High |
| 100 | No NVIDIA | ~10 min | 4-6 | Medium |
| 1000 | NVIDIA API | ~8 hours | 8-12 | High |

---

## ⚙️ Configuration

### Environment Variables

Key configurations in `.env`:

```bash
# NVIDIA Cloud API
NVIDIA_API_KEY=your_nvidia_api_key_here

# Neo4j Database
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# Embeddings Provider
EMBEDDINGS_PROVIDER=nvidia

# Optional: Local LLM (for enterprise self-hosted)
OLLAMA_BASE_URL=http://ollama:11434/v1
OLLAMA_MODEL=llama3.1:8b

# Vector Database
PINECONE_API_KEY=your_pinecone_key (optional)
```

### Model Selection

**NVIDIA Cloud Models** (recommended):
- `meta/llama-3.1-8b-instruct` (fast, good quality)
- `meta/llama-3.1-70b-instruct` (best quality)
- `nvidia/llama-3.1-nemotron-70b-instruct` (optimized)

**NVIDIA Embeddings**:
- `nvidia/llama-3.2-nv-embedqa-1b-v2` (4096 dimensions)

---

## 🚀 Enterprise Deployment

### For Healthcare & Finance

See [ENTERPRISE-ARCHITECTURE.md](ENTERPRISE-ARCHITECTURE.md) for:

- **Local LLM deployment** (no cloud data transfer)
- **HIPAA/PCI-DSS compliance** features
- **GPU optimization** (vLLM, TGI, Ollama)
- **High availability** setup
- **Security & encryption**
- **Cost analysis** (on-premise vs cloud)

### Deployment Options

1. **Cloud (Railway)** - Production-ready, auto-scaling
2. **Docker Compose** - Single server, quick setup
3. **Kubernetes** - Multi-server, high availability
4. **Air-Gapped** - Maximum security, offline

---

## 🎨 Features Deep-Dive

### localStorage Smart Caching

- Automatic version control
- Stale data cleanup
- Long filename filtering
- Cross-session persistence

### Database Connection Testing

- Real-time health checks
- Connection status display
- Automatic reconnection
- Error handling

### 3D Visualization

- Physics-based layout
- Camera controls
- Interactive exploration
- Export to various formats

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| **LangChain SSL error** | Uncheck "Use LangChain" checkbox when processing |
| **Old data in visualization** | Hard refresh browser (Ctrl+Shift+R) to clear cache |
| **Neo4j connection failed** | Check credentials in .env and Neo4j Aura status |
| **NVIDIA API errors** | Verify API key and model name |
| **Slow processing** | Use smaller documents or enable batch processing |

### Common Fixes

```bash
# Restart all services
cd assets
docker-compose down && docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker logs dafe-graphs-frontend -f

# Rebuild after code changes
docker-compose build
docker-compose up -d
```

---

## 📈 Performance

### Processing Speed

Based on NVIDIA API testing:

| Operation | Time | Notes |
|-----------|------|-------|
| Triple extraction (1 KB doc) | ~10s | 5-8 triples |
| Triple extraction (10 KB doc) | ~20s | 10-20 triples |
| Graph query (Traditional) | <100ms | Cypher-based |
| Graph query (Pure RAG) | 500ms-2s | Vector + LLM |
| Graph query (GraphRAG) | 1-5s | Multi-hop reasoning |
| Embedding generation | ~1s per doc | 4096 dimensions |

### Optimization Tips

1. **Use NVIDIA API** - Better quality than local simple extraction
2. **Batch processing** - Use Python scripts for bulk uploads
3. **Cache embeddings** - Avoid regenerating for same documents
4. **Query optimization** - Use Traditional for simple lookups, GraphRAG for complex questions

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **NVIDIA** for NIM Cloud APIs and AI infrastructure
- **Neo4j** for graph database technology
- **LangChain** for RAG orchestration framework
- **Railway** for cloud deployment platform
- **Vercel** for Next.js framework

---

## 📧 Support

- **Issues**: https://github.com/dafesmith/Graph-rag/issues
- **Discussions**: https://github.com/dafesmith/Graph-rag/discussions
- **Live Demo**: https://dafe-graphs-frontend-production.up.railway.app

---

## 🗺️ Roadmap

### Phase 1: Core Features (✅ Complete)
- [x] NVIDIA API integration
- [x] Neo4j graph storage
- [x] Three RAG query modes
- [x] 2D/3D visualization
- [x] Railway deployment
- [x] localStorage caching

### Phase 2: Enterprise Features (🚧 In Progress)
- [x] Enterprise architecture documentation
- [ ] Local LLM integration (Ollama/vLLM)
- [ ] Self-hosted vector database (Qdrant/Weaviate)
- [ ] JWT authentication
- [ ] Role-based access control (RBAC)
- [ ] Audit logging

### Phase 3: Advanced Features (📋 Planned)
- [ ] Multi-tenancy support
- [ ] Custom extraction prompts per domain
- [ ] Streaming API for real-time processing
- [ ] Graph analytics dashboard
- [ ] Export to GraphML, RDF, Turtle
- [ ] SSO integration (SAML/LDAP)

---

**Built with** ❤️ **by Dafe Smith using NVIDIA Cloud AI**
