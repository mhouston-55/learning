#!/bin/bash

set -e

echo "🎯 Kubernetes Interview Platform - Setup Script"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker is installed"

# Check if docker-compose is available
if ! docker compose version &> /dev/null && ! docker-compose --version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose is installed"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "⚠️  kubectl is not installed"
    echo ""
    read -p "Do you want to create a local KinD cluster? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Check if kind is installed
        if ! command -v kind &> /dev/null; then
            echo "📦 Installing KinD (Kubernetes in Docker)..."

            # Detect OS
            OS=$(uname -s | tr '[:upper:]' '[:lower:]')
            ARCH=$(uname -m)

            if [ "$ARCH" = "x86_64" ]; then
                ARCH="amd64"
            fi

            curl -Lo ./kind "https://kind.sigs.k8s.io/dl/v0.20.0/kind-${OS}-${ARCH}"
            chmod +x ./kind
            sudo mv ./kind /usr/local/bin/kind

            echo "✅ KinD installed"
        fi

        echo "🚀 Creating KinD cluster..."
        kind create cluster --name interview-platform --wait 60s

        echo "✅ KinD cluster created"
    else
        echo "❌ You need a Kubernetes cluster to proceed."
        echo "   Please either:"
        echo "   1. Install kubectl and configure access to a cluster"
        echo "   2. Run this script again and choose to create a KinD cluster"
        exit 1
    fi
else
    echo "✅ kubectl is installed"

    # Check if kubectl can connect to a cluster
    if kubectl cluster-info &> /dev/null; then
        echo "✅ kubectl can connect to a cluster"
        CURRENT_CONTEXT=$(kubectl config current-context)
        echo "   Current context: $CURRENT_CONTEXT"
    else
        echo "⚠️  kubectl cannot connect to a cluster"
        echo ""
        read -p "Do you want to create a local KinD cluster? (y/n) " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if ! command -v kind &> /dev/null; then
                echo "📦 Installing KinD..."
                OS=$(uname -s | tr '[:upper:]' '[:lower:]')
                ARCH=$(uname -m)
                if [ "$ARCH" = "x86_64" ]; then
                    ARCH="amd64"
                fi
                curl -Lo ./kind "https://kind.sigs.k8s.io/dl/v0.20.0/kind-${OS}-${ARCH}"
                chmod +x ./kind
                sudo mv ./kind /usr/local/bin/kind
            fi

            echo "🚀 Creating KinD cluster..."
            kind create cluster --name interview-platform --wait 60s
            echo "✅ KinD cluster created"
        else
            echo "❌ Cannot proceed without a Kubernetes cluster"
            exit 1
        fi
    fi
fi

echo ""
echo "🚀 Starting the Interview Platform..."
echo ""

# Start docker-compose
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

echo ""
echo "✅ Platform is starting..."
echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker compose version &> /dev/null; then
    docker compose ps
else
    docker-compose ps
fi

echo ""
echo "=========================================="
echo "🎉 Setup Complete!"
echo "=========================================="
echo ""
echo "🌐 Admin Panel: http://localhost:3000"
echo "🔧 Backend API: http://localhost:3001"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Select a scenario"
echo "3. Click 'Create Interview Link'"
echo "4. Send the link to your candidate"
echo ""
echo "To stop the platform:"
echo "  docker-compose down"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "Happy interviewing! 🚀"
