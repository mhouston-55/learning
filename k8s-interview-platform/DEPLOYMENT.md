# Deployment Guide

## Deployment Options

### 1. Local Development with KinD

Perfect for testing the platform locally.

```bash
# Install KinD if not already installed
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create a KinD cluster
kind create cluster --name interview-platform

# Verify cluster
kubectl cluster-info --context kind-interview-platform

# Start the platform
docker-compose up -d

# Access admin panel
open http://localhost:3000
```

### 2. Docker Compose with Existing Cluster

Use if you already have a Kubernetes cluster.

```bash
# Ensure kubectl is configured
kubectl get nodes

# Update docker-compose.yml to mount your kubeconfig
# Already configured to mount ~/.kube

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Deploy to Cloud Kubernetes (GKE, EKS, AKS)

#### Step 1: Build and Push Images

```bash
# Set your container registry
export REGISTRY="gcr.io/your-project"  # or docker.io/username

# Build images
docker build -t $REGISTRY/k8s-interview-backend:latest ./backend
docker build -t $REGISTRY/k8s-interview-frontend:latest ./frontend

# Push to registry
docker push $REGISTRY/k8s-interview-backend:latest
docker push $REGISTRY/k8s-interview-frontend:latest
```

#### Step 2: Update Kubernetes Manifests

```bash
# Update image references in deployment files
sed -i "s|your-registry|$REGISTRY|g" kubernetes/*.yaml
```

#### Step 3: Deploy to Cluster

```bash
# Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Create RBAC (allows backend to manage interview namespaces)
kubectl apply -f kubernetes/rbac.yaml

# Deploy backend and frontend
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml

# Deploy ingress (update host first!)
# Edit kubernetes/ingress.yaml and set your domain
kubectl apply -f kubernetes/ingress.yaml
```

#### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods -n k8s-interview-platform

# Check services
kubectl get svc -n k8s-interview-platform

# Check ingress
kubectl get ingress -n k8s-interview-platform
```

### 4. Cloud-Specific Instructions

#### Google Kubernetes Engine (GKE)

```bash
# Create GKE cluster
gcloud container clusters create interview-platform \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2

# Get credentials
gcloud container clusters get-credentials interview-platform \
  --zone us-central1-a

# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# Deploy platform (follow Step 3 above)
```

#### Amazon EKS

```bash
# Create EKS cluster (using eksctl)
eksctl create cluster \
  --name interview-platform \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3

# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/aws/deploy.yaml

# Deploy platform (follow Step 3 above)
```

#### Azure AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group interview-rg \
  --name interview-platform \
  --node-count 3 \
  --node-vm-size Standard_DS2_v2 \
  --generate-ssh-keys

# Get credentials
az aks get-credentials \
  --resource-group interview-rg \
  --name interview-platform

# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# Deploy platform (follow Step 3 above)
```

## Production Considerations

### 1. Resource Quotas

Limit resources for interview namespaces:

```yaml
# Create this as a template and apply per namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: interview-quota
  namespace: interview-{sessionId}
spec:
  hard:
    requests.cpu: "2"
    requests.memory: "4Gi"
    limits.cpu: "4"
    limits.memory: "8Gi"
    pods: "20"
    services: "10"
```

### 2. Network Policies

Isolate interview namespaces:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: interview-isolation
  namespace: interview-{sessionId}
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  egress:
  - to:
    - podSelector: {}
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

### 3. TLS/HTTPS Setup

Using cert-manager:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
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

# Ingress will automatically request TLS certificate
```

### 4. Monitoring

Add Prometheus monitoring:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: interview-backend-metrics
  namespace: k8s-interview-platform
  labels:
    app: interview-backend
spec:
  ports:
  - name: metrics
    port: 9090
    targetPort: 9090
  selector:
    app: interview-backend
```

### 5. Backup and Restore

Backup scenario configurations:

```bash
# Backup scenarios
tar -czf scenarios-backup.tar.gz scenarios/

# Backup Kubernetes manifests
tar -czf k8s-config-backup.tar.gz kubernetes/
```

## Scaling

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: interview-backend-hpa
  namespace: k8s-interview-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: interview-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Cluster Autoscaling

Enable on your cloud provider:

```bash
# GKE
gcloud container clusters update interview-platform \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10

# EKS (eksctl)
eksctl scale nodegroup --cluster=interview-platform \
  --name=standard-workers \
  --nodes-min=3 \
  --nodes-max=10

# AKS
az aks update \
  --resource-group interview-rg \
  --name interview-platform \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10
```

## Maintenance

### Update Platform

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker build -t $REGISTRY/k8s-interview-backend:latest ./backend
docker build -t $REGISTRY/k8s-interview-frontend:latest ./frontend
docker push $REGISTRY/k8s-interview-backend:latest
docker push $REGISTRY/k8s-interview-frontend:latest

# Rolling update
kubectl rollout restart deployment/interview-backend -n k8s-interview-platform
kubectl rollout restart deployment/interview-frontend -n k8s-interview-platform

# Check status
kubectl rollout status deployment/interview-backend -n k8s-interview-platform
```

### Cleanup Old Sessions

```bash
# Find old interview namespaces
kubectl get namespaces | grep "interview-"

# Delete namespaces older than 2 hours (manual check)
kubectl delete namespace interview-<old-session-id>

# Or create a CronJob for automatic cleanup
```

## Troubleshooting

### Backend can't create namespaces

Check RBAC permissions:

```bash
kubectl auth can-i create namespaces \
  --as=system:serviceaccount:k8s-interview-platform:interview-backend-sa
```

### WebSocket connection issues

Check ingress annotations:

```yaml
nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
nginx.ingress.kubernetes.io/websocket-services: interview-backend
```

### High resource usage

Monitor namespace resource usage:

```bash
kubectl top pods -n interview-<session-id>
kubectl describe resourcequota -n interview-<session-id>
```
