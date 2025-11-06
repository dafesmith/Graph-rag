# txt2kg Documentation Index

Complete guide index for the txt2kg Knowledge Graph Builder.

## Getting Started

1. **[README.md](README.md)** - Project overview and quick start
2. **[QUICK-START.md](QUICK-START.md)** - 5-minute quick start guide
3. **[setup-guide.md](setup-guide.md)** - Detailed local setup instructions

## Processing & Usage

4. **[FULL-TEXT-PROCESSING-PLAN.md](FULL-TEXT-PROCESSING-PLAN.md)** - BioRxiv dataset processing guide
5. **[LARGE-FILES-GUIDE.md](LARGE-FILES-GUIDE.md)** - Handling large documents

## Advanced Features

6. **[KNOWLEDGE-GRAPHS-DEEP-DIVE.md](KNOWLEDGE-GRAPHS-DEEP-DIVE.md)** 🔥 **NEW** - Comprehensive Knowledge Graph Research & Use Cases
   - Industry adoption (Google, Microsoft, Amazon, Meta)
   - Medical/healthcare knowledge graphs (35KB research report)
   - GraphRAG explained with performance benchmarks
   - Pharmaceutical companies (Pfizer, AstraZeneca) implementations
   - Real-world performance: 3.4x accuracy improvement
   - Integration patterns for medical RAG systems
   - Specific guidance for NeMo-Agent + txt2kg integration

7. **[GRAPHRAG-GUIDE.md](GRAPHRAG-GUIDE.md)** ⭐ - Complete GraphRAG (G-Retriever) setup and training guide
   - Prerequisites and system requirements
   - Installation and dependencies
   - Data preparation
   - Model training
   - Deployment
   - Troubleshooting
   - FAQ and cost estimates

## Integration & Implementation

8. **[INTEGRATION-TASK.md](INTEGRATION-TASK.md)** 🚀 **NEW** - NeMo-Agent Integration Feasibility Assessment
   - Codebase complexity analysis
   - Integration architecture design
   - 3-phase implementation plan
   - Effort estimates (3 weeks total)
   - Working code examples
   - Risk assessment and mitigation
   - **Verdict: EASY TO MODERATE complexity**

## Deployment

9. **[RAILWAY-DEPLOYMENT.md](RAILWAY-DEPLOYMENT.md)** ⭐ - Deploy to Railway using DockerHub
   - Prerequisites and account setup
   - Docker image preparation
   - Railway configuration
   - Environment variables
   - Monitoring and scaling
   - Cost optimization
   - CI/CD pipeline

## API & Development

10. **Frontend API Routes** - See `frontend/app/api/`
11. **Backend Services** - See `deploy/services/`
12. **Scripts** - See `scripts/` directory

## Quick Reference

### Query Types

| Type | File | Description |
|------|------|-------------|
| **Traditional Graph** | Built-in | Simple graph database queries |
| **Pure RAG** | Built-in | Vector search + LLM |
| **GraphRAG** | [GRAPHRAG-GUIDE.md](GRAPHRAG-GUIDE.md) | GNN-powered intelligent retrieval |

### Deployment Options

| Platform | Guide | Difficulty | Cost |
|----------|-------|------------|------|
| **Local** | [setup-guide.md](setup-guide.md) | Easy | Free |
| **Railway** | [RAILWAY-DEPLOYMENT.md](RAILWAY-DEPLOYMENT.md) | Medium | $30-80/month |
| **Docker** | [docker-compose.yml](deploy/compose/docker-compose.yml) | Easy | Free |

## Documentation by Use Case

### "I want to get started quickly"
→ [QUICK-START.md](QUICK-START.md)

### "I want to understand knowledge graphs and industry use cases"
→ [KNOWLEDGE-GRAPHS-DEEP-DIVE.md](KNOWLEDGE-GRAPHS-DEEP-DIVE.md) 🔥

### "I want to integrate txt2kg with my medical RAG system"
→ [INTEGRATION-TASK.md](INTEGRATION-TASK.md) 🚀 **START HERE**
→ [KNOWLEDGE-GRAPHS-DEEP-DIVE.md](KNOWLEDGE-GRAPHS-DEEP-DIVE.md) (Background research)

### "I want to process scientific papers"
→ [FULL-TEXT-PROCESSING-PLAN.md](FULL-TEXT-PROCESSING-PLAN.md)

### "I want the best query quality (GraphRAG)"
→ [GRAPHRAG-GUIDE.md](GRAPHRAG-GUIDE.md)

### "I want to deploy to production"
→ [RAILWAY-DEPLOYMENT.md](RAILWAY-DEPLOYMENT.md)

### "I have very large documents"
→ [LARGE-FILES-GUIDE.md](LARGE-FILES-GUIDE.md)

## External Resources

- **NVIDIA Build**: https://build.nvidia.com/
- **PyTorch Geometric**: https://pytorch-geometric.readthedocs.io/
- **Railway Docs**: https://docs.railway.app/
- **ArangoDB Docs**: https://www.arangodb.com/docs/

---

*Last Updated: November 2025*
