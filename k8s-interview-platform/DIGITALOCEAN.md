# DigitalOcean Deployment Guide

The easiest and cheapest way to host the Interview Platform for remote candidates.

## Why DigitalOcean?

- **Cheapest**: ~$48/month (vs $73+ for AWS/GCP)
- **Simplest**: Control plane is FREE
- **Fast setup**: 10 minutes to live platform
- **Easy scaling**: Add/remove nodes anytime
- **Pausable**: Delete when not interviewing, recreate when needed

## Cost Breakdown

| Component | Cost |
|-----------|------|
| Control Plane | **FREE** |
| Worker Nodes (2 x $24) | $48/month |
| Container Registry (optional) | $5/month |
| LoadBalancer | Included |
| **Total** | **~$48-53/month** |

**Budget Option:** Use 1 node ($24/month) for light usage

## Prerequisites

1. **DigitalOcean Account**
   - Sign up at https://digitalocean.com
   - $200 free credit for new accounts!

2. **Install doctl** (DO CLI)
   ```bash
   # Mac
   brew install doctl

   # Linux
   snap install doctl

   # Windows
   # Download from: https://github.com/digitalocean/doctl/releases
   ```

3. **Authenticate**
   ```bash
   # Get API token from: https://cloud.digitalocean.com/account/api/tokens
   doctl auth init
   ```

4. **Install kubectl**
   ```bash
   # Mac
   brew install kubectl

   # Linux
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   chmod +x kubectl
   sudo mv kubectl /usr/local/bin/
   ```

## Quick Deploy (Automated)

```bash
cd k8s-interview-platform
./deploy-digitalocean.sh
```

That's it! The script will:
1. Create DOKS cluster
2. Install ingress controller
3. Build and push Docker images
4. Deploy the platform
5. Give you a public URL

**Time: ~10 minutes**

## Manual Deployment

### Step 1: Create Cluster

```bash
# Create cluster
doctl kubernetes cluster create k8s-interview-platform \
  --region nyc1 \
  --version latest \
  --size s-2vcpu-4gb \
  --count 2 \
  --wait

# Configure kubectl
doctl kubernetes cluster kubeconfig save k8s-interview-platform

# Verify
kubectl get nodes
```

### Step 2: Install Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# Wait for external IP
kubectl get svc ingress-nginx-controller -n ingress-nginx -w
```

### Step 3: Set Up Container Registry

**Option A: DigitalOcean Registry ($5/month)**
```bash
# Create registry
doctl registry create interview-platform --subscription-tier basic

# Login
doctl registry login

# Use registry
export REGISTRY="registry.digitalocean.com/interview-platform"
```

**Option B: Docker Hub (Free)**
```bash
docker login

export REGISTRY="docker.io/your-username"
```

### Step 4: Build and Push Images

```bash
# Build
docker build -t $REGISTRY/k8s-interview-backend:latest ./backend
docker build -t $REGISTRY/k8s-interview-frontend:latest ./frontend

# Push
docker push $REGISTRY/k8s-interview-backend:latest
docker push $REGISTRY/k8s-interview-frontend:latest

# Update manifests
sed -i "s|your-registry|$REGISTRY|g" kubernetes/*.yaml
```

### Step 5: Deploy Platform

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/rbac.yaml
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/ingress.yaml
```

### Step 6: Get Your URL

```bash
# Get external IP
kubectl get ingress -n k8s-interview-platform

# Your platform is at:
# http://<EXTERNAL-IP>
```

## Using Your Platform

### Create Interview Sessions

1. **Navigate to your platform**
   ```
   http://<your-external-ip>
   ```

2. **Create session** in the admin panel

3. **Send link to candidate**
   ```
   http://<your-external-ip>/interview/abc123-...
   ```

4. **Candidate accesses** from anywhere in the world!

### Monitor Sessions

```bash
# View all interview namespaces
kubectl get namespaces | grep interview-

# Check specific session
kubectl get pods -n interview-<session-id>

# View logs
kubectl logs -f deployment/interview-backend -n k8s-interview-platform
```

## Scaling

### Scale Worker Nodes

```bash
# Add more capacity
doctl kubernetes cluster node-pool update k8s-interview-platform <pool-id> \
  --count 3

# Or scale down
doctl kubernetes cluster node-pool update k8s-interview-platform <pool-id> \
  --count 1

# Get pool ID
doctl kubernetes cluster node-pool list k8s-interview-platform
```

### Scale Platform Pods

```bash
# Handle more concurrent interviews
kubectl scale deployment interview-backend --replicas=3 -n k8s-interview-platform
kubectl scale deployment interview-frontend --replicas=3 -n k8s-interview-platform
```

## Cost Optimization

### Option 1: Downscale When Not Interviewing

```bash
# Scale to minimum
doctl kubernetes cluster node-pool update k8s-interview-platform <pool-id> \
  --count 1

# Scale up before interviews
doctl kubernetes cluster node-pool update k8s-interview-platform <pool-id> \
  --count 2
```

**Cost:** $24/month minimum

### Option 2: Delete and Recreate

```bash
# Delete cluster (stop all charges)
doctl kubernetes cluster delete k8s-interview-platform

# Recreate when needed
./deploy-digitalocean.sh
```

**Cost:** $0 when deleted

### Option 3: Snapshot and Restore

```bash
# Take snapshot of volumes
doctl compute volume-snapshot create <volume-id> --snapshot-name interview-backup

# Delete cluster
doctl kubernetes cluster delete k8s-interview-platform

# Restore later from snapshot
```

## Adding a Custom Domain

### With DigitalOcean Networking

```bash
# Add domain in DO dashboard
# Or via CLI
doctl compute domain create interview.yourdomain.com

# Create A record
doctl compute domain records create yourdomain.com \
  --record-type A \
  --record-name interview \
  --record-data <EXTERNAL-IP>
```

### Update Ingress

Edit `kubernetes/ingress.yaml`:

```yaml
spec:
  rules:
  - host: interview.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: interview-frontend
            port:
              number: 80
```

Apply:
```bash
kubectl apply -f kubernetes/ingress.yaml
```

## Add HTTPS/TLS

### Install cert-manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### Create ClusterIssuer

```bash
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Update Ingress for TLS

```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - interview.yourdomain.com
    secretName: interview-tls
  rules:
  - host: interview.yourdomain.com
    # ... rest of config
```

Now access at: `https://interview.yourdomain.com`

## Monitoring and Maintenance

### View Platform Logs

```bash
# Backend logs
kubectl logs -f deployment/interview-backend -n k8s-interview-platform

# Frontend logs
kubectl logs -f deployment/interview-frontend -n k8s-interview-platform

# All pods
kubectl logs -f -l app=interview-backend -n k8s-interview-platform
```

### Check Resource Usage

```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -n k8s-interview-platform

# Interview namespaces
kubectl top pods --all-namespaces | grep interview-
```

### Cleanup Old Sessions

```bash
# List interview namespaces
kubectl get ns | grep interview-

# Delete old sessions (backend auto-deletes after 2 hours)
# Manual cleanup if needed:
kubectl delete ns interview-<old-session-id>
```

## Backup and Disaster Recovery

### Backup Configuration

```bash
# Export all platform configs
kubectl get all,ingress,configmap,secret -n k8s-interview-platform -o yaml > platform-backup.yaml

# Backup scenarios
tar -czf scenarios-backup.tar.gz scenarios/
```

### Restore

```bash
# Restore platform
kubectl apply -f platform-backup.yaml

# Restore scenarios
tar -xzf scenarios-backup.tar.gz
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n k8s-interview-platform

# Describe pod for events
kubectl describe pod <pod-name> -n k8s-interview-platform

# Check logs
kubectl logs <pod-name> -n k8s-interview-platform
```

### Can't Access Platform

```bash
# Check ingress
kubectl get ingress -n k8s-interview-platform

# Check ingress controller
kubectl get svc -n ingress-nginx

# Check DNS (if using domain)
dig interview.yourdomain.com
```

### Image Pull Errors

```bash
# For DOCR, create imagePullSecret
doctl registry kubernetes-manifest | kubectl apply -f -

# Verify secret exists
kubectl get secrets -n k8s-interview-platform
```

## Support

- **DigitalOcean Docs**: https://docs.digitalocean.com/products/kubernetes/
- **Community**: https://www.digitalocean.com/community/questions
- **Platform Issues**: Check main README.md

## Quick Reference

```bash
# Cluster management
doctl kubernetes cluster list
doctl kubernetes cluster get k8s-interview-platform
doctl kubernetes cluster delete k8s-interview-platform

# Node pool management
doctl kubernetes cluster node-pool list k8s-interview-platform
doctl kubernetes cluster node-pool update k8s-interview-platform <pool-id> --count 3

# Registry
doctl registry repository list
doctl registry repository delete-manifest <repo> <digest>

# Kubernetes
kubectl get all -n k8s-interview-platform
kubectl logs -f deployment/interview-backend -n k8s-interview-platform
kubectl get ingress -n k8s-interview-platform
```

## Next Steps

1. **Deploy the platform**: Run `./deploy-digitalocean.sh`
2. **Get your URL**: Check ingress external IP
3. **Test it**: Create a session and try it yourself
4. **Set up domain** (optional): Add custom domain for professional look
5. **Add HTTPS** (recommended): Install cert-manager for TLS
6. **Start interviewing**: Send links to candidates!

Happy interviewing on DigitalOcean! 🌊
