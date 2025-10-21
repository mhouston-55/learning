#!/bin/bash
# Kibana Initial Setup Script
# This script creates index patterns and sample data

set -e

echo "Waiting for Kibana to be ready..."
until curl -s http://localhost:5601/api/status | grep -q "available"; do
    echo "Waiting for Kibana..."
    sleep 5
done

echo "Kibana is ready! Setting up index patterns..."

# Create Zeek logs data view
echo "Creating Zeek logs data view..."
curl -X POST "http://localhost:5601/api/data_views/data_view" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{
    "data_view": {
      "title": "zeek-logs-*",
      "name": "Zeek Network Logs",
      "timeFieldName": "@timestamp"
    }
  }'

# Create Sysmon logs data view
echo "Creating Sysmon logs data view..."
curl -X POST "http://localhost:5601/api/data_views/data_view" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{
    "data_view": {
      "title": "sysmon-logs-*",
      "name": "Sysmon Event Logs",
      "timeFieldName": "@timestamp"
    }
  }'

echo "Index patterns created successfully!"
echo "You can now access Kibana at http://localhost:5601"
