#!/bin/bash

set -e

echo "🌊 DigitalOcean Kubernetes Interview Platform Deployment"
echo "========================================================"
echo ""

# Check prerequisites
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl (DigitalOcean CLI) is not installed"
    echo ""
    echo "Install it with:"
    echo "  brew install doctl  # Mac"
    echo "  snap install doctl  # Linux"
    echo ""
    echo "Then authenticate:"
    echo "  doctl auth init"
    echo ""
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed"
    exit 1
fi

echo "✅ Prerequisites installed"
echo ""

# Configuration
CLUSTER_NAME="k8s-interview-platform"
REGION="nyc1"  # Change to your preferred region: nyc1, sfo3, sgp1, lon1, fra1, etc.
NODE_SIZE="s-2vcpu-4gb"  # $24/month per node
NODE_COUNT=2

echo "Configuration:"
echo "  Cluster Name: $CLUSTER_NAME"
echo "  Region: $REGION"
echo "  Node Size: $NODE_SIZE ($24/month per node)"
echo "  Node Count: $NODE_COUNT"
echo "  Total Cost: ~$48/month for worker nodes (control plane is FREE)"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Check if cluster already exists
if doctl kubernetes cluster list --format Name --no-header | grep -q "^${CLUSTER_NAME}$"; then
    echo "⚠️  Cluster '$CLUSTER_NAME' already exists"
    read -p "Use existing cluster? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    echo "📦 Using existing cluster..."
else
    echo "🚀 Creating DOKS cluster..."
    echo "   This takes about 5 minutes..."

    doctl kubernetes cluster create $CLUSTER_NAME \
        --region $REGION \
        --version latest \
        --size $NODE_SIZE \
        --count $NODE_COUNT \
        --wait

    echo "✅ Cluster created!"
fi

# Get kubeconfig
echo "🔧 Configuring kubectl..."
doctl kubernetes cluster kubeconfig save $CLUSTER_NAME

# Verify connection
echo "✅ kubectl configured"
kubectl get nodes

echo ""
echo "📦 Installing nginx ingress controller..."

# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

echo "⏳ Waiting for LoadBalancer to get external IP..."
echo "   This may take 2-3 minutes..."

# Wait for external IP
for i in {1..60}; do
    EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [ -n "$EXTERNAL_IP" ]; then
        echo "✅ LoadBalancer ready! External IP: $EXTERNAL_IP"
        break
    fi
    echo -n "."
    sleep 5
done

if [ -z "$EXTERNAL_IP" ]; then
    echo ""
    echo "⚠️  External IP not ready yet. Check with:"
    echo "   kubectl get svc -n ingress-nginx"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo ""
echo "🏗️  Building and pushing Docker images..."

# Check if user has container registry
echo ""
echo "You need a container registry to store images."
echo ""
echo "Options:"
echo "  1. DigitalOcean Container Registry (DOCR) - $5/month"
echo "  2. Docker Hub - Free (public images)"
echo "  3. Skip build (use pre-built images)"
echo ""

read -p "Choose option (1/2/3): " -n 1 -r
echo ""

if [[ $REPLY == "1" ]]; then
    echo "Setting up DigitalOcean Container Registry..."

    read -p "Enter registry name (lowercase, no spaces): " REGISTRY_NAME

    # Create registry if it doesn't exist
    if ! doctl registry get 2>/dev/null; then
        echo "Creating registry..."
        doctl registry create $REGISTRY_NAME --subscription-tier basic
    fi

    # Login to registry
    doctl registry login

    REGISTRY="registry.digitalocean.com/$REGISTRY_NAME"

    echo "Building images..."
    docker build -t $REGISTRY/k8s-interview-backend:latest ./backend
    docker build -t $REGISTRY/k8s-interview-frontend:latest ./frontend

    echo "Pushing images..."
    docker push $REGISTRY/k8s-interview-backend:latest
    docker push $REGISTRY/k8s-interview-frontend:latest

    # Update Kubernetes manifests
    sed -i.bak "s|your-registry|$REGISTRY|g" kubernetes/*.yaml

elif [[ $REPLY == "2" ]]; then
    read -p "Enter your Docker Hub username: " DOCKER_USERNAME

    echo "Login to Docker Hub:"
    docker login

    REGISTRY="docker.io/$DOCKER_USERNAME"

    echo "Building images..."
    docker build -t $REGISTRY/k8s-interview-backend:latest ./backend
    docker build -t $REGISTRY/k8s-interview-frontend:latest ./frontend

    echo "Pushing images..."
    docker push $REGISTRY/k8s-interview-backend:latest
    docker push $REGISTRY/k8s-interview-frontend:latest

    # Update Kubernetes manifests
    sed -i.bak "s|your-registry|$REGISTRY|g" kubernetes/*.yaml

else
    echo "⚠️  Skipping image build. You'll need to update kubernetes/*.yaml manually"
fi

echo ""
echo "🚀 Deploying Interview Platform to Kubernetes..."

# Deploy platform
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/rbac.yaml
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml

# Update ingress with IP
if [ -n "$EXTERNAL_IP" ]; then
    # Create a simple ingress without domain
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: interview-platform-ingress
  namespace: k8s-interview-platform
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: interview-frontend
            port:
              number: 80
EOF
fi

echo ""
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=interview-backend -n k8s-interview-platform --timeout=300s || true
kubectl wait --for=condition=ready pod -l app=interview-frontend -n k8s-interview-platform --timeout=300s || true

echo ""
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""

if [ -n "$EXTERNAL_IP" ]; then
    echo "🌐 Your Interview Platform is live at:"
    echo "   http://$EXTERNAL_IP"
    echo ""
    echo "📋 Send this URL to candidates:"
    echo "   http://$EXTERNAL_IP/interview/<session-id>"
    echo ""
    echo "💡 Recommended: Set up a domain name"
    echo "   1. Point your domain to: $EXTERNAL_IP"
    echo "   2. Update kubernetes/ingress.yaml with your domain"
    echo "   3. kubectl apply -f kubernetes/ingress.yaml"
fi

echo ""
echo "📊 Cluster Info:"
echo "   Cluster: $CLUSTER_NAME"
echo "   Region: $REGION"
echo "   Nodes: $NODE_COUNT x $NODE_SIZE"
echo "   Cost: ~\$48/month"
echo ""
echo "🔧 Useful Commands:"
echo "   View pods:     kubectl get pods -n k8s-interview-platform"
echo "   View logs:     kubectl logs -f deployment/interview-backend -n k8s-interview-platform"
echo "   Get ingress:   kubectl get ingress -n k8s-interview-platform"
echo ""
echo "💰 To PAUSE cluster (stop charges):"
echo "   doctl kubernetes cluster delete $CLUSTER_NAME"
echo ""
echo "   To recreate later, just run this script again!"
echo ""
echo "Happy interviewing! 🚀"
