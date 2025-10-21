from flask import Flask, render_template, jsonify, request
import json
import os
import glob
from datetime import datetime

app = Flask(__name__)

ZEEK_LOG_DIR = "/zeek-logs"

def parse_zeek_log(file_path):
    """Parse Zeek JSON logs"""
    logs = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        log_entry = json.loads(line)
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return logs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/logs')
def get_logs():
    log_type = request.args.get('type', 'conn')
    limit = int(request.args.get('limit', 100))

    # Find log files
    pattern = os.path.join(ZEEK_LOG_DIR, f"{log_type}.log")
    log_files = glob.glob(pattern)

    all_logs = []
    for log_file in log_files:
        logs = parse_zeek_log(log_file)
        all_logs.extend(logs)

    # Sort by timestamp and limit
    all_logs.sort(key=lambda x: x.get('ts', 0), reverse=True)

    return jsonify(all_logs[:limit])

@app.route('/api/stats')
def get_stats():
    """Get statistics about Zeek logs"""
    stats = {
        'total_connections': 0,
        'total_http_requests': 0,
        'total_dns_queries': 0,
        'unique_ips': set(),
        'suspicious_events': 0
    }

    # Count connections
    conn_logs = parse_zeek_log(os.path.join(ZEEK_LOG_DIR, 'conn.log'))
    stats['total_connections'] = len(conn_logs)
    for log in conn_logs:
        if 'id.orig_h' in log:
            stats['unique_ips'].add(log['id.orig_h'])
        if 'id.resp_h' in log:
            stats['unique_ips'].add(log['id.resp_h'])

    # Count HTTP requests
    http_logs = parse_zeek_log(os.path.join(ZEEK_LOG_DIR, 'http.log'))
    stats['total_http_requests'] = len(http_logs)

    # Count DNS queries
    dns_logs = parse_zeek_log(os.path.join(ZEEK_LOG_DIR, 'dns.log'))
    stats['total_dns_queries'] = len(dns_logs)

    # Look for suspicious indicators
    for log in dns_logs:
        if log.get('query', '').count('.') > 10:  # Potential DNS tunneling
            stats['suspicious_events'] += 1

    stats['unique_ips'] = len(stats['unique_ips'])

    return jsonify(stats)

@app.route('/api/log-types')
def get_log_types():
    """List available log types"""
    log_files = glob.glob(os.path.join(ZEEK_LOG_DIR, '*.log'))
    log_types = [os.path.basename(f).replace('.log', '') for f in log_files]
    return jsonify(log_types)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
