#!/usr/bin/env python3
"""
Traffic Generation Control Server
Provides web interface to trigger various APT scenarios
"""

from flask import Flask, jsonify, request, render_template_string
import subprocess
import threading
import time

app = Flask(__name__)

# Store active scenarios
active_scenarios = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>APT Traffic Generator</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #0a0e27;
            color: #00ff00;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }
        .scenarios {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .scenario-card {
            background: #1a1f3a;
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 20px;
        }
        .scenario-card h3 {
            color: #00ff00;
            margin-top: 0;
        }
        .scenario-card p {
            color: #88ff88;
            font-size: 0.9em;
        }
        button {
            background: #0a0e27;
            color: #00ff00;
            border: 2px solid #00ff00;
            padding: 10px 20px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            border-radius: 3px;
            margin: 5px;
        }
        button:hover {
            background: #1a1f3a;
            box-shadow: 0 0 10px #00ff00;
        }
        button.stop {
            border-color: #ff0000;
            color: #ff0000;
        }
        button.stop:hover {
            box-shadow: 0 0 10px #ff0000;
        }
        .status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            margin-left: 10px;
            font-size: 0.8em;
        }
        .status.running {
            background: #00ff00;
            color: #000;
        }
        .status.stopped {
            background: #ff0000;
            color: #fff;
        }
        .mitre {
            background: #2a2f4a;
            padding: 10px;
            border-radius: 3px;
            margin: 10px 0;
            font-size: 0.85em;
            color: #ffff00;
        }
    </style>
</head>
<body>
    <h1>APT TRAFFIC GENERATOR</h1>
    <p style="text-align: center; color: #88ff88;">Simulate APT29 (Cozy Bear) Attack Techniques</p>

    <div class="scenarios">
        <div class="scenario-card">
            <h3>C2 Beaconing <span class="status" id="status-c2">STOPPED</span></h3>
            <p>Simulates regular command-and-control traffic with consistent intervals</p>
            <div class="mitre">MITRE: T1071.001 - Application Layer Protocol: Web Protocols</div>
            <button onclick="startScenario('c2')">Start C2 Beacon</button>
            <button class="stop" onclick="stopScenario('c2')">Stop</button>
        </div>

        <div class="scenario-card">
            <h3>DNS Tunneling <span class="status" id="status-dns">STOPPED</span></h3>
            <p>Exfiltrates data through DNS queries using encoded subdomain names</p>
            <div class="mitre">MITRE: T1071.004 - Application Layer Protocol: DNS</div>
            <button onclick="startScenario('dns')">Start DNS Tunnel</button>
            <button class="stop" onclick="stopScenario('dns')">Stop</button>
        </div>

        <div class="scenario-card">
            <h3>Lateral Movement <span class="status" id="status-lateral">STOPPED</span></h3>
            <p>Simulates SMB/RPC traffic patterns used in lateral movement</p>
            <div class="mitre">MITRE: T1021.002 - SMB/Windows Admin Shares</div>
            <button onclick="startScenario('lateral')">Start Lateral Movement</button>
            <button class="stop" onclick="stopScenario('lateral')">Stop</button>
        </div>

        <div class="scenario-card">
            <h3>Data Exfiltration <span class="status" id="status-exfil">STOPPED</span></h3>
            <p>Large data transfers to external servers</p>
            <div class="mitre">MITRE: T1041 - Exfiltration Over C2 Channel</div>
            <button onclick="startScenario('exfil')">Start Exfiltration</button>
            <button class="stop" onclick="stopScenario('exfil')">Stop</button>
        </div>

        <div class="scenario-card">
            <h3>Port Scanning <span class="status" id="status-scan">STOPPED</span></h3>
            <p>Network reconnaissance scanning for open ports</p>
            <div class="mitre">MITRE: T1046 - Network Service Scanning</div>
            <button onclick="startScenario('scan')">Start Port Scan</button>
            <button class="stop" onclick="stopScenario('scan')">Stop</button>
        </div>

        <div class="scenario-card">
            <h3>Suspicious HTTPS <span class="status" id="status-https">STOPPED</span></h3>
            <p>HTTPS traffic to suspicious domains with unusual patterns</p>
            <div class="mitre">MITRE: T1071.001 - Web Protocols</div>
            <button onclick="startScenario('https')">Start HTTPS Traffic</button>
            <button class="stop" onclick="stopScenario('https')">Stop</button>
        </div>
    </div>

    <script>
        function startScenario(scenario) {
            fetch(`/api/start/${scenario}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    updateStatus(scenario, 'running');
                });
        }

        function stopScenario(scenario) {
            fetch(`/api/stop/${scenario}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    updateStatus(scenario, 'stopped');
                });
        }

        function updateStatus(scenario, status) {
            const statusEl = document.getElementById(`status-${scenario}`);
            statusEl.textContent = status.toUpperCase();
            statusEl.className = 'status ' + status;
        }

        // Auto-refresh status every 5 seconds
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    for (const [scenario, status] of Object.entries(data)) {
                        updateStatus(scenario, status ? 'running' : 'stopped');
                    }
                });
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/start/<scenario>', methods=['POST'])
def start_scenario(scenario):
    if scenario in active_scenarios and active_scenarios[scenario].get('running'):
        return jsonify({"message": f"Scenario {scenario} is already running"})

    # Start scenario in background thread
    thread = threading.Thread(target=run_scenario, args=(scenario,))
    thread.daemon = True
    thread.start()

    active_scenarios[scenario] = {"running": True, "thread": thread}
    return jsonify({"message": f"Started scenario: {scenario}"})

@app.route('/api/stop/<scenario>', methods=['POST'])
def stop_scenario(scenario):
    if scenario in active_scenarios:
        active_scenarios[scenario]['running'] = False
        return jsonify({"message": f"Stopped scenario: {scenario}"})
    return jsonify({"message": f"Scenario {scenario} was not running"})

@app.route('/api/status')
def get_status():
    status = {}
    for scenario in ['c2', 'dns', 'lateral', 'exfil', 'scan', 'https']:
        status[scenario] = active_scenarios.get(scenario, {}).get('running', False)
    return jsonify(status)

def run_scenario(scenario):
    """Run the appropriate scenario script"""
    print(f"Starting scenario: {scenario}")

    if scenario == 'c2':
        from c2_beacon import run_c2_beacon
        run_c2_beacon(lambda: active_scenarios.get('c2', {}).get('running', False))
    elif scenario == 'dns':
        from dns_tunnel import run_dns_tunnel
        run_dns_tunnel(lambda: active_scenarios.get('dns', {}).get('running', False))
    elif scenario == 'lateral':
        from lateral_movement import run_lateral_movement
        run_lateral_movement(lambda: active_scenarios.get('lateral', {}).get('running', False))
    elif scenario == 'exfil':
        from data_exfil import run_data_exfil
        run_data_exfil(lambda: active_scenarios.get('exfil', {}).get('running', False))
    elif scenario == 'scan':
        from port_scan import run_port_scan
        run_port_scan(lambda: active_scenarios.get('scan', {}).get('running', False))
    elif scenario == 'https':
        from https_traffic import run_https_traffic
        run_https_traffic(lambda: active_scenarios.get('https', {}).get('running', False))

if __name__ == '__main__':
    print("Traffic Generation Control Server Starting...")
    print("Access at http://localhost:8888")
    app.run(host='0.0.0.0', port=8888, debug=False)
