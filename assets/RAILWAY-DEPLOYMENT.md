# Deploy txt2kg to Railway using DockerHub

Complete guide for deploying the txt2kg Knowledge Graph Builder to Railway.com using DockerHub.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Prepare Docker Images](#prepare-docker-images)
4. [Push to DockerHub](#push-to-dockerhub)
5. [Deploy to Railway](#deploy-to-railway)
6. [Configuration](#configuration)
7. [Post-Deployment](#post-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What You'll Deploy

**txt2kg** consists of multiple services:
- **Frontend (Next.js)** - Web UI on port 3000
- **ArangoDB** - Graph database on port 8529
- **Sentence Transformers** - Embedding service on port 8002
- **Pinecone** - Vector database on port 5081 (optional)
- **Ollama** - Local LLM inference (requires GPU, optional)

### Architecture

```
Railway.app
├── Frontend Service (Next.js + Node.js)
│   └── Port: 3000 (public)
├── ArangoDB Service
│   └── Port: 8529 (internal)
├── Sentence Transformers Service
│   └── Port 8002 (internal)
└── Pinecone Service (optional)
    └── Port: 5081 (internal)
```

### Cost Estimate

| Plan | Resources | Cost | Suitable For |
|------|-----------|------|--------------|
| **Trial** | $5 credit | Free | Testing only |
| **Developer** | 8GB RAM, shared CPU | $20/month | Small projects |
| **Team** | Custom resources | Variable | Production |

**Estimated monthly cost**: $30-80 depending on usage

---

## Prerequisites

### Required Accounts
1. **GitHub** account (for code repository)
2. **DockerHub** account (free)
   - Sign up at: https://hub.docker.com/
3. **Railway** account (free trial)
   - Sign up at: https://railway.app/
4. **NVIDIA API** key
   - Get from: https://build.nvidia.com/

### Local Requirements
- Docker Desktop installed
- Git installed
- Terminal/Command Prompt access
- txt2kg repository cloned

---

## Prepare Docker Images

### Step 1: Login to DockerHub

```bash
docker login
# Enter your DockerHub username and password
```

### Step 2: Build Frontend Image

```bash
cd /path/to/Graph-rag/assets

# Build the frontend image
docker build -f deploy/app/Dockerfile -t YOUR_DOCKERHUB_USERNAME/txt2kg-frontend:latest .

# Test locally (optional)
docker run -p 3000:3000 \
  -e NVIDIA_API_KEY="your-key" \
  YOUR_DOCKERHUB_USERNAME/txt2kg-frontend:latest
```

Expected output:
```
▲ Next.js 14.x.x
- Local: http://localhost:3000
✓ Ready in 2.3s
```

### Step 3: Build ArangoDB Image (Use Official)

For ArangoDB, we'll use the official image:
```bash
# No need to build, we'll use: arangodb:latest
```

### Step 4: Build Sentence Transformers Image

```bash
cd /path/to/Graph-rag/assets

# Build sentence transformers service
docker build -f deploy/services/sentence-transformers/Dockerfile \
  -t YOUR_DOCKERHUB_USERNAME/txt2kg-sentence-transformers:latest \
  deploy/services/sentence-transformers

# Test locally (optional)
docker run -p 8002:80 YOUR_DOCKERHUB_USERNAME/txt2kg-sentence-transformers:latest
```

### Step 5: Build Pinecone Image (Optional)

```bash
# Use official Pinecone image
# We'll configure this in Railway directly
```

---

## Push to DockerHub

### Push All Images

```bash
# Push frontend
docker push YOUR_DOCKERHUB_USERNAME/txt2kg-frontend:latest

# Push sentence transformers
docker push YOUR_DOCKERHUB_USERNAME/txt2kg-sentence-transformers:latest
```

**Verify on DockerHub**:
1. Go to https://hub.docker.com/
2. Login and check your repositories
3. You should see:
   - `YOUR_USERNAME/txt2kg-frontend`
   - `YOUR_USERNAME/txt2kg-sentence-transformers`

---

## Deploy to Railway

### Step 1: Create New Project

1. Go to https://railway.app/
2. Click **"New Project"**
3. Select **"Empty Project"**
4. Name it: `txt2kg-production`

### Step 2: Deploy ArangoDB Service

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add ArangoDB"** (if available)
3. OR click **"Empty Service"** and configure manually:

**Manual ArangoDB Setup**:
```
Service Name: arangodb
Image: arangodb:latest
Port: 8529
Environment Variables:
  ARANGO_NO_AUTH=1
```

4. Click **"Settings"** → **"Generate Domain"** to get internal URL
5. Note the internal URL: `arangodb.railway.internal:8529`

### Step 3: Deploy Sentence Transformers Service

1. Click **"+ New"** → **"Empty Service"**
2. Configure:

```
Service Name: sentence-transformers
Docker Image: YOUR_DOCKERHUB_USERNAME/txt2kg-sentence-transformers:latest
Port: 80
Internal Port: 80
```

3. Note internal URL: `sentence-transformers.railway.internal`

### Step 4: Deploy Pinecone Service (Optional)

1. Click **"+ New"** → **"Empty Service"**
2. Configure:

```
Service Name: pinecone
Docker Image: ghcr.io/pinecone-io/pinecone-index:latest
Port: 5081
Internal Port: 5081
Environment Variables:
  PINECONE_DIMENSION=384
```

### Step 5: Deploy Frontend Service

1. Click **"+ New"** → **"Empty Service"**
2. Configure:

```
Service Name: frontend
Docker Image: YOUR_DOCKERHUB_USERNAME/txt2kg-frontend:latest
Port: 3000
```

3. Click **"Settings"** → **"Generate Domain"**
4. This gives you a public URL like: `txt2kg-production.up.railway.app`

---

## Configuration

### Frontend Environment Variables

In Railway, go to **frontend service** → **"Variables"** and add:

```bash
# Required
NVIDIA_API_KEY=nvapi-YOUR-ACTUAL-KEY
NODE_ENV=production

# ArangoDB Connection
ARANGODB_URL=http://arangodb.railway.internal:8529
ARANGODB_DB=txt2kg
ARANGODB_USER=
ARANGODB_PASSWORD=

# Sentence Transformers
SENTENCE_TRANSFORMERS_URL=http://sentence-transformers.railway.internal

# Pinecone (if deployed)
PINECONE_URL=http://pinecone.railway.internal:5081

# Optional: Ollama (if you have GPU service)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:1.7b

# Next.js
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

### ArangoDB Initialization

Railway doesn't directly support init scripts, so we need to initialize ArangoDB after deployment:

1. **Option A**: Use Railway's **"Terminal"** feature:
```bash
# Connect to ArangoDB container
# Create database
curl -X POST http://arangodb.railway.internal:8529/_api/database \
  -H "Content-Type: application/json" \
  -d '{"name":"txt2kg"}'
```

2. **Option B**: Create init job service:
```bash
# Add to frontend startup script
if [ "$INIT_DB" = "true" ]; then
  node /scripts/init-arangodb.js
fi
```

---

## Post-Deployment

### Step 1: Verify Deployment

**Check Frontend**:
```bash
curl https://your-app.up.railway.app
```

**Check Health Endpoints**:
```bash
# Sentence transformers
curl https://your-app.up.railway.app/api/health

# ArangoDB
curl http://arangodb.railway.internal:8529/_api/version
```

### Step 2: Upload Sample Data

1. Go to your Railway app URL
2. Navigate to **"Upload"** tab
3. Upload a sample document
4. Process it in **"Process Documents"** tab

### Step 3: Test Query

1. Go to **RAG Search** page
2. Try a Traditional Graph query:
   ```
   What entities are in the knowledge graph?
   ```

### Step 4: Monitor Logs

In Railway dashboard:
1. Click on each service
2. View **"Logs"** tab
3. Check for errors

---

## Troubleshooting

### Issue 1: Frontend Won't Start

**Error**: `ECONNREFUSED` or `Cannot connect to database`

**Solution**:
```bash
# Check if all services are running
# In Railway dashboard, ensure all services show "Active"

# Verify environment variables
# Check ARANGODB_URL points to: http://arangodb.railway.internal:8529
```

### Issue 2: Out of Memory

**Error**: `JavaScript heap out of memory`

**Solution**:
1. Increase Railway plan resources
2. OR add to frontend environment:
   ```
   NODE_OPTIONS=--max-old-space-size=4096
   ```

### Issue 3: Can't Connect Services

**Error**: `Service unreachable`

**Solution**:
- Railway services communicate via **internal domains**
- Format: `service-name.railway.internal`
- NOT `localhost` or external domains

### Issue 4: Database Not Persisting

**Solution**:
1. In Railway ArangoDB service
2. Go to **"Settings"** → **"Volumes"**
3. Add volume mount:
   ```
   Mount Path: /var/lib/arangodb3
   ```

### Issue 5: Slow Performance

**Solutions**:
- Upgrade Railway plan (more RAM/CPU)
- Enable Railway's **"Shared Database"** for better performance
- Use Redis caching (add Redis service)

---

## Advanced Configuration

### Custom Domain

1. In Railway project → **"Settings"** → **"Domains"**
2. Click **"Add Custom Domain"**
3. Enter your domain: `kg.yourdomain.com`
4. Add DNS records as shown:
   ```
   Type: CNAME
   Name: kg
   Value: your-app.up.railway.app
   ```

### Auto-Deploy from GitHub

1. In Railway project → **"+ New"** → **"GitHub Repo"**
2. Connect your txt2kg repository
3. Configure build settings:
   ```
   Root Directory: assets
   Dockerfile Path: deploy/app/Dockerfile
   ```
4. Each git push will auto-deploy

### Monitoring & Alerts

1. In Railway project → **"Metrics"**
2. Set up alerts for:
   - High CPU usage (>80%)
   - High memory (>90%)
   - Request errors (>5%)

### Backup Strategy

**Automated Backups**:
```bash
# Create backup service
# Add to Railway as scheduled job
*/6 * * * * docker exec arangodb arangodump --output-directory /backups
```

---

## Railway CLI (Alternative Deployment)

### Install Railway CLI

```bash
# Mac/Linux
brew install railway

# Windows
npm install -g @railway/cli
```

### Deploy via CLI

```bash
# Login
railway login

# Create project
railway init

# Add services
railway service create frontend
railway service create arangodb

# Deploy frontend
railway up -s frontend --dockerfile deploy/app/Dockerfile

# Set variables
railway variables set NVIDIA_API_KEY=your-key -s frontend
```

---

## Cost Optimization Tips

1. **Use Shared Database**: Railway offers managed databases ($5-10/month cheaper)
2. **Downgrade Inactive Services**: Stop services you're not using
3. **Use NVIDIA API**: Instead of running Ollama (saves GPU costs)
4. **Implement Caching**: Add Redis to reduce database queries
5. **Monitor Usage**: Railway shows resource usage - optimize accordingly

---

## Scaling for Production

### Horizontal Scaling

1. In Railway → **Service Settings** → **"Replicas"**
2. Increase to 2-3 instances
3. Railway auto-load balances

### Vertical Scaling

1. Upgrade Railway plan for more resources
2. Developer ($20) → Team ($50) → Enterprise (custom)

### Database Optimization

```bash
# Add indexes in ArangoDB
# Create index on frequently queried fields
db.entities.ensureIndex({ type: "hash", fields: ["name"] })
db.relationships.ensureIndex({ type: "hash", fields: ["type"] })
```

---

## CI/CD Pipeline Example

Create `.github/workflows/deploy-railway.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and Push
        run: |
          cd assets
          docker build -f deploy/app/Dockerfile -t ${{ secrets.DOCKERHUB_USERNAME }}/txt2kg-frontend:latest .
          docker push ${{ secrets.DOCKERHUB_USERNAME }}/txt2kg-frontend:latest

      - name: Deploy to Railway
        run: |
          railway up -s frontend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## Security Best Practices

### 1. Environment Variables
- ✅ Store API keys in Railway **"Variables"** (encrypted)
- ❌ Never hardcode in Dockerfile or code

### 2. ArangoDB Security
```bash
# For production, enable authentication:
ARANGO_ROOT_PASSWORD=secure-password-here
ARANGO_NO_AUTH=0
```

### 3. HTTPS Only
- Railway provides free SSL/TLS
- Enforce HTTPS in Next.js config

### 4. Rate Limiting
```typescript
// Add to frontend API routes
import rateLimit from 'express-rate-limit'

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
})
```

---

## Checklist: Pre-Deployment

- [ ] All Docker images built and tested locally
- [ ] DockerHub account created and images pushed
- [ ] Railway account created with payment method
- [ ] NVIDIA API key obtained
- [ ] Environment variables documented
- [ ] Database initialization script ready
- [ ] Sample data prepared for testing
- [ ] Domain name configured (if using custom domain)
- [ ] Monitoring alerts configured
- [ ] Backup strategy planned

---

## Checklist: Post-Deployment

- [ ] All services showing "Active" in Railway
- [ ] Frontend accessible via public URL
- [ ] Database connection working
- [ ] Sample document uploaded and processed
- [ ] Traditional Graph query tested
- [ ] NVIDIA API integration working
- [ ] Logs reviewed for errors
- [ ] Performance metrics acceptable
- [ ] Cost estimate reviewed
- [ ] Documentation updated with production URLs

---

## Resources

- **Railway Docs**: https://docs.railway.app/
- **DockerHub**: https://hub.docker.com/
- **Railway Community**: https://discord.gg/railway
- **txt2kg Repository**: https://github.com/your-repo/txt2kg

---

## Example: Complete Deployment Script

```bash
#!/bin/bash
set -e

echo "==================================="
echo "txt2kg Railway Deployment Script"
echo "==================================="

# Configuration
DOCKERHUB_USER="your-username"
APP_NAME="txt2kg-production"

# Step 1: Build images
echo "Building Docker images..."
cd assets
docker build -f deploy/app/Dockerfile -t $DOCKERHUB_USER/txt2kg-frontend:latest .
docker build -f deploy/services/sentence-transformers/Dockerfile \
  -t $DOCKERHUB_USER/txt2kg-sentence-transformers:latest \
  deploy/services/sentence-transformers

# Step 2: Push to DockerHub
echo "Pushing to DockerHub..."
docker push $DOCKERHUB_USER/txt2kg-frontend:latest
docker push $DOCKERHUB_USER/txt2kg-sentence-transformers:latest

# Step 3: Deploy to Railway (using CLI)
echo "Deploying to Railway..."
railway login
railway init
railway service create frontend --image $DOCKERHUB_USER/txt2kg-frontend:latest
railway service create sentence-transformers --image $DOCKERHUB_USER/txt2kg-sentence-transformers:latest
railway service create arangodb --image arangodb:latest

# Step 4: Set environment variables
echo "Configuring environment..."
railway variables set NVIDIA_API_KEY=$NVIDIA_API_KEY -s frontend
railway variables set ARANGODB_URL=http://arangodb.railway.internal:8529 -s frontend

echo "==================================="
echo "Deployment complete!"
echo "Check Railway dashboard for status"
echo "==================================="
```

---

## Summary

**Total Deployment Time**: 1-2 hours
**Monthly Cost**: $30-80
**Difficulty**: Intermediate

**Recommended Flow**:
1. Test locally with Docker Compose first
2. Build and push images to DockerHub
3. Deploy to Railway one service at a time
4. Configure environment variables
5. Test thoroughly before sharing URL

---

*Generated for txt2kg - NVIDIA Knowledge Graph Builder*
*Railway Deployment Guide v1.0*
*Last Updated: November 2025*
