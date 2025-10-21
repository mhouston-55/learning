#!/bin/bash
# Wait for all services to be healthy before proceeding

echo "Waiting for all services to start..."
echo ""

# Wait for Elasticsearch
echo -n "Waiting for Elasticsearch... "
until curl -s http://localhost:9200/_cluster/health | grep -q "yellow\|green"; do
    sleep 2
done
echo "READY"

# Wait for Kibana
echo -n "Waiting for Kibana... "
until curl -s http://localhost:5601/api/status | grep -q "available"; do
    sleep 2
done
echo "READY"

# Wait for Zeek Viewer
echo -n "Waiting for Zeek Viewer... "
until curl -s http://localhost:8080 > /dev/null 2>&1; do
    sleep 2
done
echo "READY"

# Wait for Traffic Generator
echo -n "Waiting for Traffic Generator... "
until curl -s http://localhost:8888 > /dev/null 2>&1; do
    sleep 2
done
echo "READY"

# Wait for Control Panel
echo -n "Waiting for Control Panel... "
until curl -s http://localhost:8000 > /dev/null 2>&1; do
    sleep 2
done
echo "READY"

echo ""
echo "========================================="
echo "All services are ready!"
echo "========================================="
echo ""
echo "Access your Threat Hunting Lab at:"
echo "  Main Dashboard:    http://localhost:8000"
echo "  Kibana:            http://localhost:5601"
echo "  Zeek Viewer:       http://localhost:8080"
echo "  Traffic Generator: http://localhost:8888"
echo ""
echo "Start hunting for threats!"
echo "========================================="
