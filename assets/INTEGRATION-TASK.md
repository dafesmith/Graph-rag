# Knowledge Graph Integration Task Assessment

**Purpose**: Assess feasibility and complexity of integrating txt2kg knowledge graph capabilities into NeMo-Agent medical RAG system.

**Date**: January 2025
**Status**: Feasibility Assessment Complete

---

## Executive Summary

**Verdict**: ✅ **EASY TO MODERATE COMPLEXITY** - This integration is straightforward and feasible.

**Estimated Timeline**:
- **Phase 1** (Basic Graph Query Tool): 1-2 days
- **Phase 2** (Drug Knowledge Graph): 1 week
- **Phase 3** (Full Medical KG): 2-3 weeks

**Confidence Level**: HIGH - Both systems are designed for modularity and integration.

---

## Architecture Assessment

### txt2kg Current State ✅

**What Works**:
```
✅ ArangoDB running (92 entities, 66 relationships)
✅ Triple extraction pipeline (batch-process-chunks.py)
✅ HTTP API endpoints ready for consumption
✅ Query modes: Traditional Graph, Pure RAG, GraphRAG
✅ Sentence transformers for embeddings (running on port 8002)
✅ Docker deployment configured
```

**Key Integration Points**:
1. **REST API**: `/api/graph-db/triples` - GET all triples
2. **Enhanced Query**: `/api/enhanced-query` - POST query with parameters
3. **RemoteBackendService**: TypeScript service with 3 query methods:
   - `query()` - Vector KNN + graph traversal
   - `queryTraditional()` - Direct text matching
   - `enhancedQuery()` - KNN with metadata scoring

**API Request Format**:
```typescript
POST http://localhost:3000/api/enhanced-query
{
  "query": "What drugs interact with Metformin?",
  "queryMode": "traditional",  // or "pure_rag" or "graphrag"
  "topK": 5
}
```

**API Response Format**:
```typescript
{
  "relevantTriples": [
    { "subject": "Metformin", "predicate": "interacts_with", "object": "Warfarin" }
  ],
  "count": 5,
  "success": true
}
```

---

### NeMo-Agent Current State 📋

**What Exists** (Planning Stage):
```
📋 YAML-based agent configuration pattern
📋 Custom tool registration via Python functions
📋 PostgreSQL schema designed (Synthea EHR data)
📋 Milvus RAG retriever pattern established
📋 ReAct agent workflow documented
```

**Tool Registration Pattern**:
```yaml
functions:
  search_drug_info_tool:
    _type: nat_retriever
    retriever: drug_info_retriever
    topic: "FDA drug information"

  find_patient_tool:
    _type: custom_function
    module: medical_tools.patient_query
    function: find_patient
    description: "Search for patient by name or ID"
```

**What Needs to Be Created**:
1. Directory: `medical_tools/` (Python module)
2. File: `medical_tools/graph_query.py` (new tool)
3. Updated config: Add graph query tool to agent YAML

---

## Integration Complexity Analysis

### Easy ✅ (1-2 days)

**Task**: Create basic graph query tool for NeMo Agent

**Why Easy**:
1. txt2kg API is already HTTP-accessible (no backend modification needed)
2. Python `requests` library handles HTTP calls (standard library)
3. NeMo Agent tool pattern is simple (just Python functions)
4. No database schema changes required
5. No authentication/security complexity (both local services)

**Implementation**:
```python
# File: medical_tools/graph_query.py
import requests
from typing import List, Dict

def query_drug_knowledge_graph(query: str, top_k: int = 5) -> str:
    """
    Query the txt2kg drug knowledge graph for interactions,
    contraindications, and mechanisms.

    Args:
        query: Natural language query about drugs
        top_k: Number of relevant triples to return

    Returns:
        String summary of relevant knowledge graph facts
    """
    # Call txt2kg API
    response = requests.post(
        "http://localhost:3000/api/enhanced-query",
        json={
            "query": query,
            "queryMode": "traditional",
            "topK": top_k
        }
    )

    if response.status_code != 200:
        return f"Error querying knowledge graph: {response.status_code}"

    data = response.json()
    triples = data.get("relevantTriples", [])

    # Format triples into readable text
    if not triples:
        return "No relevant information found in knowledge graph."

    facts = []
    for triple in triples:
        fact = f"{triple['subject']} {triple['predicate']} {triple['object']}"
        facts.append(fact)

    return f"Knowledge Graph Facts:\n" + "\n".join(f"- {fact}" for fact in facts)
```

**YAML Config Update**:
```yaml
functions:
  query_drug_kg_tool:
    _type: custom_function
    module: medical_tools.graph_query
    function: query_drug_knowledge_graph
    description: "Query drug knowledge graph for interactions, contraindications, and mechanisms"
```

**Test Query**:
```python
User: "Is Metformin safe for patients taking Warfarin?"

Agent Flow:
[Thought] Need to check drug interactions
[Action] query_drug_kg_tool(query="Metformin Warfarin interaction")
[Observation] Knowledge Graph Facts:
- Metformin interacts_with Warfarin
- Warfarin increases_risk_of bleeding
- Metformin may_require dose_adjustment
[Final Answer] According to the drug knowledge graph, Metformin does interact
with Warfarin. Warfarin increases bleeding risk, and Metformin may require
dose adjustment. Clinical review recommended.
```

---

### Moderate 🔶 (1-2 weeks)

**Task**: Build comprehensive drug knowledge graph with FDA data

**Why Moderate**:
1. Need to download FDA drug labels (~10,000 drugs)
2. Extract structured data (interactions, contraindications, dosing)
3. Process through txt2kg triple extraction pipeline
4. Map medical ontologies (RxNorm codes → drug names)
5. Generate embeddings for all drug entities
6. Test query quality and tune parameters

**Data Sources**:
- **FDA OpenFDA API**: https://open.fda.gov/apis/drug/label/
- **RxNorm**: https://www.nlm.nih.gov/research/umls/rxnorm/
- **DrugBank** (optional): https://go.drugbank.com/

**Processing Pipeline**:
```bash
# Step 1: Download FDA drug labels
curl "https://api.fda.gov/drug/label.json?limit=1000" > fda_labels.json

# Step 2: Convert to text format for txt2kg
python scripts/fda_to_text.py fda_labels.json > fda_drugs.txt

# Step 3: Extract triples using txt2kg
python batch-process-chunks.py fda_drugs.txt --output drug_triples.json

# Step 4: Import to ArangoDB via API
curl -X POST http://localhost:3000/api/graph-db/triples \
  -H "Content-Type: application/json" \
  -d @drug_triples.json
```

**Expected Graph Size**:
- **Drugs**: ~10,000 entities
- **Interactions**: ~50,000 relationships
- **Contraindications**: ~20,000 relationships
- **Mechanisms**: ~15,000 relationships
- **Total Triples**: ~85,000

**Challenges**:
1. 🔶 FDA API rate limits (1000 requests/hour)
2. 🔶 Unstructured text in drug labels (requires NLP extraction)
3. 🔶 Deduplication (same drug, different names)
4. 🔶 Quality control (validate extracted triples)

**Mitigation**:
- Use batch processing with delays for rate limits
- Leverage txt2kg's LangChain-based triple extraction (already handles unstructured text)
- Implement fuzzy matching for drug name normalization
- Sample validation: manually review 100 random triples

---

### Advanced 🔷 (2-4 weeks)

**Task**: Full medical knowledge graph (diseases, symptoms, procedures)

**Why Advanced**:
1. Multiple data sources need integration:
   - Synthea EHR data (patient conditions, medications)
   - UMLS/SNOMED-CT (medical terminology)
   - PubMed literature (clinical evidence)
   - Disease ontologies (ICD-10, disease hierarchies)
2. Complex ontology mapping
3. Large-scale data processing (millions of triples)
4. Need GraphRAG training for optimal performance

**Data Sources**:
| Source | Triples | Complexity |
|--------|---------|------------|
| FDA Drug Labels | ~85K | Moderate |
| Synthea Patient Data | ~50K | Easy |
| Disease-Symptom DB | ~100K | Moderate |
| UMLS Subset | ~500K | Advanced |
| PubMed Abstracts | ~1M | Advanced |

**GraphRAG Training** (Optional but Recommended):
- Requires GPU (16GB+ VRAM)
- Training time: 2-4 hours (RTX 4090) or use cloud GPU
- Improves query quality by 3.4x (based on benchmarks)
- See [GRAPHRAG-GUIDE.md](GRAPHRAG-GUIDE.md) for details

**Current Limitation**: User is on Mac (no NVIDIA GPU)
- **Solution**: Use cloud GPU (RunPod, Lambda Labs) for training
- **Cost**: $5-20 for training run
- **Alternative**: Skip GraphRAG, use Traditional Graph mode (still effective)

---

## Recommended Implementation Plan

### Phase 1: Proof of Concept (2 days) ✅ EASY

**Goal**: Get basic graph query working in NeMo Agent

**Tasks**:
1. ✅ Create `medical_tools/graph_query.py`
2. ✅ Implement `query_drug_knowledge_graph()` function
3. ✅ Update NeMo Agent YAML config
4. ✅ Test with existing txt2kg data (92 entities, 66 relationships)
5. ✅ Verify agent can call tool and get results

**Success Criteria**:
- Agent successfully queries txt2kg API
- Returns relevant triples for drug interaction queries
- Integrates with existing patient query tools

**Deliverable**: Working demo showing NeMo Agent using knowledge graph for drug queries

---

### Phase 2: Drug Knowledge Graph (1 week) 🔶 MODERATE

**Goal**: Build comprehensive drug interaction knowledge graph

**Tasks**:
1. Download FDA drug labels (10,000 drugs)
2. Extract drug information:
   - Generic/brand names
   - Interactions
   - Contraindications
   - Dosing guidelines
   - Mechanisms of action
3. Process through txt2kg extraction pipeline
4. Import to ArangoDB
5. Generate embeddings for all drug entities
6. Test query quality with medical scenarios

**Success Criteria**:
- 10,000+ drug entities in graph
- 50,000+ interaction relationships
- Agent can answer complex drug interaction questions
- <3 second query response time

**Deliverable**: Production-ready drug knowledge graph integrated with NeMo Agent

---

### Phase 3: Patient-Drug Context Integration (1 week) 🔶 MODERATE

**Goal**: Connect patient EHR data with drug knowledge graph

**Tasks**:
1. Create tool: `check_patient_drug_interactions(patient_id: str)`
   - Query patient medications from PostgreSQL
   - Query drug interactions from txt2kg
   - Combine results and highlight conflicts
2. Create tool: `recommend_alternatives(drug_name: str, patient_id: str)`
   - Query patient conditions and allergies
   - Find contraindications in knowledge graph
   - Suggest alternative medications
3. Add memory to track drug interaction checks
4. Create clinical decision support workflow

**Example Use Case**:
```
User: "Check if John Doe's current medications are safe"

Agent Flow:
1. get_patient_medications(patient_id=P12345)
   → [Metformin 500mg, Lisinopril 10mg, Aspirin 81mg]

2. query_drug_kg_tool("interactions between Metformin Lisinopril Aspirin")
   → Knowledge Graph: No major interactions found

3. Final Answer: John Doe's medications (Metformin, Lisinopril, Aspirin)
   show no major drug-drug interactions according to the knowledge graph.
```

**Success Criteria**:
- Agent combines EHR data with knowledge graph seamlessly
- Detects drug interactions before prescription
- Provides alternative drug suggestions
- Includes clinical evidence from knowledge graph

**Deliverable**: Clinical decision support agent with integrated knowledge graph

---

## Technical Architecture

### System Integration Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     User (Clinician)                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  NeMo Agent (ReAct)                             │
│                  Port: 8000                                     │
│                                                                 │
│  Tools:                                                         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ 1. find_patient_tool → PostgreSQL                      │   │
│  │ 2. get_medications_tool → PostgreSQL                   │   │
│  │ 3. search_drug_info_tool → Milvus (RAG)               │   │
│  │ 4. query_drug_kg_tool → txt2kg API (NEW!)             │   │
│  │ 5. check_patient_interactions → Hybrid (NEW!)         │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
┌──────────────────┐ ┌─────────────┐ ┌──────────────────────┐
│  PostgreSQL      │ │  Milvus DB  │ │  txt2kg API          │
│  (Synthea EHR)   │ │  (Drug Info │ │  http://localhost:3000│
│                  │ │   + Medical │ │                      │
│  - patients      │ │   Literature│ │  Endpoints:          │
│  - medications   │ │   RAG)      │ │  - /api/enhanced-query│
│  - conditions    │ │             │ │  - /api/graph-db/... │
│  - encounters    │ │  Port: 19530│ │                      │
│                  │ │             │ │  Backend: ArangoDB   │
│  Port: 5432      │ │             │ │  - Entities: 10K+    │
└──────────────────┘ └─────────────┘ │  - Relationships: 85K│
                                     │                      │
                                     │  Port: 8529          │
                                     └──────────────────────┘
```

### Data Flow

**Query**: "Is Metformin safe for John Doe who has kidney disease?"

```
1. NeMo Agent receives query
   ↓
2. Agent selects tools:
   - find_patient_tool("John Doe")
   - get_diagnoses_tool(patient_id)
   - query_drug_kg_tool("Metformin kidney disease contraindication")
   ↓
3. Tool execution:
   PostgreSQL: Returns patient P12345, diagnosis: Chronic Kidney Disease (Stage 3)
   txt2kg API: Returns triples:
     - Metformin contraindicated_in renal_impairment
     - Metformin requires dose_adjustment_for CKD_stage_3
     - Metformin risk_of lactic_acidosis
   ↓
4. Agent synthesizes response:
   "⚠️ WARNING: Metformin is contraindicated in renal impairment.
   John Doe has Chronic Kidney Disease Stage 3. Metformin requires
   dose adjustment and carries risk of lactic acidosis in CKD patients.

   Clinical review recommended. Consider alternative: Sitagliptin."
```

---

## Risk Assessment

### Low Risk ✅

1. **API Integration**: txt2kg has stable HTTP API, Python requests library is battle-tested
2. **Tool Pattern**: NeMo Agent custom tools are simple Python functions
3. **Data Availability**: FDA data is free, well-structured, and legally unrestricted
4. **Backward Compatibility**: New tools don't break existing patient query tools

### Medium Risk 🔶

1. **FDA Data Quality**: Some drug labels may have incomplete interaction data
   - **Mitigation**: Supplement with DrugBank, RxNorm, or manual curation
2. **Query Performance**: Large knowledge graph (85K+ triples) may slow queries
   - **Mitigation**: Add caching, index optimization, limit search scope
3. **False Positives**: Knowledge graph may flag benign interactions
   - **Mitigation**: Confidence scoring, clinical validation with experts

### High Risk 🔴

1. **None Identified** - This is a straightforward integration with well-understood components

---

## Resource Requirements

### Development Resources

| Phase | Developer Time | GPU Needed | Cost |
|-------|---------------|------------|------|
| Phase 1: POC | 2 days | No | $0 |
| Phase 2: Drug KG | 1 week | Optional | $0-20 |
| Phase 3: Integration | 1 week | Optional | $0-20 |
| **Total** | **3 weeks** | **Optional** | **$0-40** |

### Infrastructure

**Current State** (Already Running):
- ✅ txt2kg frontend (Next.js) - Port 3000
- ✅ ArangoDB - Port 8529
- ✅ Sentence Transformers - Port 8002

**Needed for NeMo Agent**:
- PostgreSQL (Synthea data) - Port 5432 - **Not yet deployed**
- Milvus (Medical RAG) - Port 19530 - **Not yet deployed**
- Redis (Session state) - Port 6379 - **Not yet deployed**

**Deployment Options**:
1. **Local Docker**: All services on localhost (development)
2. **Railway**: Cloud deployment for production (see [RAILWAY-DEPLOYMENT.md](RAILWAY-DEPLOYMENT.md))
3. **Hybrid**: NeMo Agent local, txt2kg on Railway

---

## Success Metrics

### Phase 1: POC Success

- [ ] NeMo Agent successfully calls txt2kg API
- [ ] Returns relevant drug interaction triples
- [ ] Response time <2 seconds
- [ ] No errors in tool execution

### Phase 2: Drug KG Success

- [ ] 10,000+ drugs in knowledge graph
- [ ] 50,000+ interaction relationships
- [ ] Agent answers 90%+ of drug interaction test queries correctly
- [ ] Queries complete in <3 seconds
- [ ] <5% false positive rate on interaction warnings

### Phase 3: Integration Success

- [ ] Agent combines patient EHR + drug KG seamlessly
- [ ] Detects contraindications based on patient conditions
- [ ] Provides alternative medication suggestions
- [ ] Clinician validation: 80%+ accuracy on test cases
- [ ] Zero data access errors

---

## Conclusion

### Final Assessment: ✅ **EASY TO MODERATE**

**Why This Integration Is Feasible**:

1. ✅ **Both systems are modular**: txt2kg has APIs, NeMo Agent has plugin architecture
2. ✅ **No database migrations needed**: Each system keeps its own storage
3. ✅ **HTTP integration is simple**: Python `requests` library handles all communication
4. ✅ **Data is available**: FDA drug labels are free and unrestricted
5. ✅ **Clear implementation path**: 3-phase plan with concrete deliverables
6. ✅ **Low risk**: No major technical blockers identified

**Recommended Next Steps**:

1. **Start with Phase 1** (2 days) - Prove the concept works
2. **Evaluate results** - Does basic graph query provide value?
3. **If successful, proceed to Phase 2** (1 week) - Build drug knowledge graph
4. **Production deployment** - Follow [RAILWAY-DEPLOYMENT.md](RAILWAY-DEPLOYMENT.md) guide

**Timeline**: 3 weeks total for full integration

**Confidence**: HIGH - This is a well-scoped, achievable project.

---

## Next Actions

### Immediate (This Week)

1. **Review this assessment** with stakeholders
2. **Approve Phase 1** POC implementation
3. **Set up development environment**:
   ```bash
   # Terminal 1: Start txt2kg (already running)
   cd /Users/dafesmith/Documents/repo/Graph-rag/assets
   docker compose up

   # Terminal 2: Clone NeMo Agent (if not done)
   cd /Users/dafesmith/Documents/repo
   git clone https://github.com/NVIDIA/NeMo-Agent-Toolkit.git
   cd NeMo-Agent-Toolkit

   # Terminal 3: Create medical tools directory
   mkdir -p examples/medical/ehr_agent/src/medical_tools
   touch examples/medical/ehr_agent/src/medical_tools/__init__.py
   touch examples/medical/ehr_agent/src/medical_tools/graph_query.py
   ```

4. **Implement first tool** (2 hours):
   - Copy the `query_drug_knowledge_graph()` function from this document
   - Add to `graph_query.py`
   - Test with curl to verify txt2kg API works

5. **Create agent config** (1 hour):
   - Copy YAML template from this document
   - Update with graph query tool
   - Test agent locally

6. **Demo to stakeholders** (1 hour):
   - Show agent querying knowledge graph
   - Demonstrate drug interaction detection
   - Collect feedback for Phase 2

### Short Term (Next 2 Weeks)

- Complete Phase 1 POC
- Download FDA drug labels
- Begin Phase 2 implementation if Phase 1 is successful

### Long Term (Next Month)

- Deploy production drug knowledge graph
- Integrate with patient EHR queries
- Train GraphRAG model (optional, requires GPU)
- Deploy to Railway for production access

---

**Document Version**: 1.0
**Last Updated**: January 2025
**Author**: txt2kg Integration Assessment
**Status**: ✅ Ready for Implementation
