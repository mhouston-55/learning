#!/usr/bin/env python3
"""
Threat Hunting Lab Control Panel
Central dashboard for managing and accessing all lab components
"""

from flask import Flask, render_template
import requests
import json
import os

app = Flask(__name__)

SCENARIOS_DIR = "/scenarios"

def load_scenarios():
    """Load scenario descriptions"""
    scenarios = []
    if os.path.exists(SCENARIOS_DIR):
        for filename in sorted(os.listdir(SCENARIOS_DIR)):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(SCENARIOS_DIR, filename)) as f:
                        scenario = json.load(f)
                        scenarios.append(scenario)
                except:
                    pass
    return scenarios

@app.route('/')
def index():
    scenarios = load_scenarios()
    return render_template('index.html', scenarios=scenarios)

@app.route('/api/health')
def health():
    """Check health of all services"""
    services = {
        'elasticsearch': 'http://elasticsearch:9200/_cluster/health',
        'kibana': 'http://kibana:5601/api/status',
    }

    status = {}
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            status[service] = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            status[service] = 'unhealthy'

    return status

if __name__ == '__main__':
    print("Threat Hunting Lab Control Panel Starting...")
    print("Access dashboard at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
