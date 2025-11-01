# 🚀 txt2kg Setup Guide

## Quick Start (3 Steps)

### 1️⃣ Choose Your Setup Mode

**Option A: Cloud-Based (NVIDIA API) - No GPU Required**
```bash
# Edit .env file and add your NVIDIA API key:
# NVIDIA_API_KEY=nvapi-your-key-here

# Start minimal stack (no local LLM needed)
docker compose -f deploy/compose/docker-compose.yml up -d app arangodb arangodb-init
```

**Option B: Local GPU (Ollama) - Requires NVIDIA GPU**
```bash
# Start minimal stack with Ollama
./start.sh
```

**Option C: Complete Stack (All Services)**
```bash
# Start everything (Ollama + vLLM + Embeddings + Vector DB)
./start.sh --complete
```

---

### 2️⃣ Pull a Language Model (if using Ollama)

```bash
# Wait for Ollama to start (about 30 seconds), then:
docker exec ollama-compose ollama pull llama3.1:8b

# Optional: Try other models
docker exec ollama-compose ollama pull llama3.2:3b        # Smaller, faster
docker exec ollama-compose ollama pull qwen2.5:7b         # Good for knowledge extraction
docker exec ollama-compose ollama pull mistral:7b         # Alternative model
```

---

### 3️⃣ Access the Application

Open in your browser:
- **Main App**: http://localhost:3001
- **ArangoDB UI**: http://localhost:8529
- **Ollama API** (if running): http://localhost:11434

---

## 📦 What Gets Installed?

### Minimal Setup (`./start.sh`):
- ✅ **Frontend** (Next.js) - Port 3001
- ✅ **ArangoDB** (Graph Database) - Port 8529
- ✅ **Ollama** (Local LLM) - Port 11434

### Complete Setup (`./start.sh --complete`):
- ✅ Everything from minimal +
- ✅ **vLLM** (Advanced LLM) - Port 8001
- ✅ **Sentence Transformers** (Embeddings) - Port 8000
- ✅ **Pinecone** (Vector DB) - Port 5081

---

## 🔧 Detailed Setup Instructions

### Prerequisites Check

```bash
# Check Docker is running
docker ps

# Check Docker Compose version
docker compose version

# Check GPU (optional, for local models)
nvidia-smi
```

---

### Setup for NVIDIA API (Cloud)

**Step 1: Get API Key**
1. Go to https://build.nvidia.com
2. Sign in and create an API key
3. Copy the key (starts with `nvapi-`)

**Step 2: Configure Environment**
```bash
# Edit .env file
nano .env

# Add your key:
NVIDIA_API_KEY=nvapi-your-actual-key-here
```

**Step 3: Start Services**
```bash
# Start just the frontend and database (no Ollama needed)
docker compose -f deploy/compose/docker-compose.yml up -d app arangodb arangodb-init

# Check logs
docker compose -f deploy/compose/docker-compose.yml logs -f
```

**Step 4: Configure in UI**
1. Open http://localhost:3001
2. Go to "Process" tab
3. Select "NVIDIA API" as your model provider
4. Choose a model (e.g., `meta/llama-3.1-70b-instruct`)

---

### Setup for Local GPU (Ollama)

**Step 1: Verify GPU**
```bash
# Check NVIDIA GPU is available
nvidia-smi

# You should see your GPU listed
```

**Step 2: Start Services**
```bash
# Navigate to project directory
cd /Users/dafesmith/Documents/repo/txt2kg/assets

# Make start script executable
chmod +x start.sh

# Start minimal setup
./start.sh
```

**Step 3: Pull Model**
```bash
# Wait ~30 seconds for Ollama to start, then:
docker exec ollama-compose ollama pull llama3.1:8b

# This downloads the model (~4.7GB)
# Takes 5-10 minutes depending on internet speed
```

**Step 4: Verify**
```bash
# Check all services are running
docker ps

# You should see:
# - app (frontend)
# - arangodb
# - ollama-compose
```

---

### Setup for Complete Stack

```bash
# Start everything
./start.sh --complete

# Pull Ollama model
docker exec ollama-compose ollama pull llama3.1:8b

# Wait for all services to be healthy
docker compose -f deploy/compose/docker-compose.complete.yml ps
```

---

## 🧪 Testing Your Setup

### Test 1: Check Services Are Running

```bash
# List running containers
docker ps

# Check logs
docker compose logs -f app
```

### Test 2: Test ArangoDB

```bash
# Open in browser
open http://localhost:8529

# Or test with curl
curl http://localhost:8529/_api/version
```

### Test 3: Test Ollama (if using local)

```bash
# Check Ollama is responding
curl http://localhost:11434/api/tags

# Test generation
docker exec ollama-compose ollama run llama3.1:8b "Hello, how are you?"
```

### Test 4: Test Frontend

```bash
# Open in browser
open http://localhost:3001

# Should see the txt2kg interface
```

---

## 📁 Understanding the Architecture

```
┌─────────────────────────────────────────┐
│         Browser (localhost:3001)        │
│              Frontend (React)           │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│         Next.js API Routes              │
│        (Backend in Frontend)            │
└──┬────────┬──────────┬──────────────────┘
   │        │          │
   ↓        ↓          ↓
┌─────┐ ┌──────┐ ┌─────────────┐
│Ollama│ │Arango│ │Pinecone/etc│
│:11434│ │:8529 │ │  :5081     │
└─────┘ └──────┘ └─────────────┘
```

### Service Ports:
- **3001** - Frontend UI
- **8529** - ArangoDB (graph database)
- **11434** - Ollama (local LLM)
- **8001** - vLLM (optional)
- **8000** - Sentence Transformers (optional)
- **5081** - Pinecone (optional)

---

## 🔄 Common Operations

### Start Services
```bash
./start.sh                    # Minimal
./start.sh --complete        # Complete
```

### Stop Services
```bash
docker compose -f deploy/compose/docker-compose.yml down
# or
docker compose -f deploy/compose/docker-compose.complete.yml down
```

### Restart a Service
```bash
docker compose restart app
docker compose restart ollama
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f app
docker compose logs -f ollama
```

### Update Code
```bash
# Stop services
docker compose down

# Pull latest code
git pull

# Rebuild and restart
docker compose up -d --build
```

### Clear Data
```bash
# Stop everything
docker compose down

# Remove volumes (⚠️ deletes all data)
docker compose down -v

# Restart fresh
./start.sh
```

---

## 🐛 Troubleshooting

### Issue: Port Already in Use

```bash
# Find what's using port 3001
lsof -i :3001

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - '3002:3000'  # Use port 3002 instead
```

### Issue: Ollama Not Starting

```bash
# Check GPU is available
nvidia-smi

# Check Docker can access GPU
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi

# Check Ollama logs
docker logs ollama-compose
```

### Issue: Frontend Won't Build

```bash
# Clear and rebuild
docker compose down
docker compose up -d --build app
```

### Issue: Database Connection Failed

```bash
# Check ArangoDB is running
docker ps | grep arangodb

# Check logs
docker logs txt2kg-arangodb-1

# Restart ArangoDB
docker compose restart arangodb
```

### Issue: Out of Memory

```bash
# Check memory usage
docker stats

# Increase Docker memory limit in Docker Desktop:
# Settings → Resources → Memory (set to 8GB+)
```

---

## 🎯 Next Steps After Setup

1. **Upload Documents**
   - Go to "Upload" tab
   - Upload PDF, TXT, or DOCX files

2. **Process Documents**
   - Go to "Process" tab
   - Select your model
   - Click "Process Documents"

3. **View Knowledge Graph**
   - Go to "Edit" tab to review triples
   - Go to "Visualize" tab to see the graph

4. **Query with RAG**
   - Use the chat interface
   - Ask questions about your documents

---

## 📚 Additional Resources

- **NVIDIA API Catalog**: https://build.nvidia.com
- **Ollama Models**: https://ollama.com/library
- **ArangoDB Docs**: https://www.arangodb.com/docs/
- **Docker Docs**: https://docs.docker.com

---

## 💡 Tips

- **Start Small**: Use minimal setup first, add services as needed
- **Monitor Resources**: Use `docker stats` to watch CPU/memory
- **Save Your Work**: ArangoDB data persists in Docker volumes
- **Try Different Models**: Each LLM has different strengths
- **Use GPU Efficiently**: Only run one LLM service at a time

---

## 🆘 Getting Help

1. Check logs: `docker compose logs -f`
2. Check service health: `docker ps`
3. Restart services: `docker compose restart`
4. Full reset: `docker compose down -v && ./start.sh`

---

**Setup Complete! 🎉**

Your txt2kg platform is ready to use at http://localhost:3001
