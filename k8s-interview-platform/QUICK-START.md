# Quick Start Guide

Get the Kubernetes Interview Platform running in 5 minutes!

## Prerequisites

Choose ONE option:

### Option A: Have Kubernetes Cluster
- Docker installed
- Access to any Kubernetes cluster
- kubectl configured

### Option B: No Kubernetes Cluster
- Docker installed
- We'll create a local cluster with KinD

## Setup

### Option A: With Existing Cluster

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd k8s-interview-platform

# 2. Verify kubectl works
kubectl get nodes

# 3. Start the platform
docker-compose up -d

# 4. Open your browser
open http://localhost:3000

# Done! 🎉
```

### Option B: Create Local Cluster First

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd k8s-interview-platform

# 2. Install KinD (Kubernetes in Docker)
# Linux/Mac:
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-$(uname)-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# 3. Create local Kubernetes cluster
kind create cluster --name interview

# 4. Start the platform
docker-compose up -d

# 5. Open your browser
open http://localhost:3000

# Done! 🎉
```

## First Interview Session

1. **Select a scenario**
   - Start with "Basic Troubleshooting" for beginners
   - Choose "Advanced Multi-Service" for senior candidates

2. **Click "Create Interview Link"**
   - Wait a few seconds for the environment to spin up

3. **Copy the link**
   - It looks like: `http://localhost:3000/interview/abc123-...`

4. **Send to your candidate**
   - Via email, Slack, or any messaging platform

5. **Candidate opens link**
   - They'll see a terminal with kubectl access
   - They can start debugging immediately

## Testing It Yourself

Want to try it first? Create a session and open the link yourself!

```bash
# In the terminal that appears, try:
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

You should see broken pods and deployments to fix!

## What's Next?

- **Customize scenarios**: Edit files in `scenarios/` directory
- **Deploy to production**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Add authentication**: Protect admin panel with auth middleware
- **Monitor usage**: Add logging and analytics

## Common Issues

### "Connection failed" error
```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs backend
```

### "kubectl: command not found" in terminal
```bash
# Check backend logs
docker-compose logs backend

# Rebuild backend
docker-compose build backend
docker-compose up -d
```

### Can't access http://localhost:3000
```bash
# Check if port is already in use
lsof -i :3000

# Or change port in docker-compose.yml
```

## Stop the Platform

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Delete KinD cluster (if you created one)
kind delete cluster --name interview
```

## Questions?

Check the main [README.md](README.md) for detailed documentation!
