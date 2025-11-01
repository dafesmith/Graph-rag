# ⚡ QUICK START GUIDE

## 🎯 Choose Your Path

### Path A: Using NVIDIA API (Cloud) - **EASIEST, NO GPU NEEDED**

```bash
# 1. Edit .env and add your NVIDIA API key
nano .env
# Add: NVIDIA_API_KEY=nvapi-your-key-here

# 2. Start services
docker compose -f deploy/compose/docker-compose.yml up -d

# 3. Open browser
open http://localhost:3001
```

**In the UI:**
- Go to "Process" tab
- Select "NVIDIA API" as provider
- Choose model: `meta/llama-3.1-70b-instruct`

---

### Path B: Using Local GPU (Ollama) - **REQUIRES NVIDIA GPU**

```bash
# 1. Start services
./start.sh

# 2. Pull model (wait 30 seconds first)
docker exec ollama-compose ollama pull llama3.1:8b

# 3. Open browser
open http://localhost:3001
```

---

## 📊 Check Status

```bash
# See running containers
docker ps

# Watch logs
docker compose logs -f app
```

---

## 🛑 Stop Everything

```bash
docker compose down
```

---

## 📖 Full Documentation

See [setup-guide.md](setup-guide.md) for detailed instructions.
