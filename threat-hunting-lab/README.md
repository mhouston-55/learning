# APT Threat Hunting Lab

A complete browser-based threat hunting environment for learning to detect APT29 (Cozy Bear) techniques. Everything runs in Docker and is accessible through your web browser - no SSH or terminal required for hunting!

## Don't Have Docker Installed?

**No problem!** Run this lab entirely in your browser using these free cloud options:

### Option 1: GitHub Codespaces (Recommended)
- **Free:** 60 hours/month
- **Best for:** Extended learning sessions
- **Setup:** 2 minutes
- **[Full Guide →](CODESPACES.md)**

**Quick start:**
1. Go to your GitHub repo
2. Click "Code" → "Codespaces" → "Create codespace"
3. Wait for it to load, then run `docker-compose up -d`
4. Access web interfaces via the "Ports" tab

### Option 2: Play with Docker
- **Free:** Unlimited sessions
- **Session length:** 4 hours each
- **Setup:** 3 minutes
- **[Full Guide →](PLAY-WITH-DOCKER.md)**

**Quick start:**
1. Visit https://labs.play-with-docker.com/
2. Login and click "Add New Instance"
3. Clone this repo and run `docker-compose up -d`
4. Click port numbers at top to access services

Both options give you the complete lab experience without installing anything locally!

---

## Quick Start (Local Docker)

Get up and running in under 5 minutes:

```bash
# 1. Start the lab
cd threat-hunting-lab
docker-compose up -d

# 2. Wait for all services to be ready (takes 2-3 minutes)
./init/wait-for-services.sh

# 3. Set up Kibana index patterns
./init/setup-kibana.sh

# 4. Open your browser and start hunting!
# Visit http://localhost:8000 for the main dashboard
```

That's it! You're ready to hunt for threats.

## What You Get

This lab provides a complete threat hunting environment with:

- **ELK Stack** (Elasticsearch, Logstash, Kibana) for log analysis
- **Zeek** network monitoring with web-based log viewer
- **Sysmon** event simulation (Windows security events)
- **APT29 traffic generators** simulating real attack techniques
- **10 guided hunting scenarios** teaching specific detection methods
- **Pre-built detection queries** ready to use in Kibana

All components run in Docker containers and are accessible via localhost web interfaces.

## Web Interfaces

Once running, access these URLs in your browser:

| Service | URL | Purpose |
|---------|-----|---------|
| **Main Dashboard** | http://localhost:8000 | Central control panel with all scenarios |
| **Kibana** | http://localhost:5601 | Primary threat hunting interface |
| **Zeek Viewer** | http://localhost:8080 | Real-time network traffic logs |
| **Traffic Generator** | http://localhost:8888 | Trigger APT attack simulations |
| **Elasticsearch** | http://localhost:9200 | Raw log database (API) |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR BROWSER                             │
│  Dashboard │ Kibana │ Zeek Viewer │ Traffic Generator       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│   Kibana       │   │  Zeek Network  │   │  Traffic Gen   │
│   (Port 5601)  │   │  Monitor       │   │  (Port 8888)   │
└───────┬────────┘   │  (Port 8080)   │   └───────┬────────┘
        │            └───────┬────────┘           │
        │                    │                    │
        │            ┌───────▼────────┐           │
        │            │  Sysmon Event  │           │
        │            │  Simulator     │◄──────────┘
        │            └───────┬────────┘
        │                    │
┌───────▼────────────────────▼────────┐
│         Logstash Pipeline           │
│    (Processes and enriches logs)    │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         Elasticsearch               │
│      (Stores all log data)          │
└─────────────────────────────────────┘
```

## 10 Hunting Scenarios

Each scenario teaches you how to detect a specific APT technique:

### Beginner Level
1. **C2 Beaconing** - Detect regular command and control communications
2. **DNS Tunneling** - Identify data exfiltration via DNS
3. **Encoded PowerShell** - Find obfuscated malicious commands
4. **Network Scanning** - Spot reconnaissance activity
5. **Suspicious User-Agents** - Detect custom malware User-Agent strings

### Intermediate Level
6. **Lateral Movement** - Track SMB-based network movement
7. **Credential Dumping** - Detect LSASS memory access
8. **Malware Droppers** - Find suspicious file creation

### Advanced Level
9. **Data Exfiltration** - Identify large data uploads
10. **Persistence Mechanisms** - Detect scheduled tasks and registry modifications

## How to Use This Lab

### Step 1: Start the Lab

```bash
cd threat-hunting-lab
docker-compose up -d
```

Wait for all containers to start (check with `docker-compose ps`).

### Step 2: Access the Main Dashboard

Open http://localhost:8000 in your browser. This shows:
- All available web interfaces
- The 10 hunting scenarios with descriptions
- Detection queries for each scenario

### Step 3: Generate APT Traffic

Visit http://localhost:8888 to access the Traffic Generator.

Click buttons to simulate:
- C2 Beaconing
- DNS Tunneling
- Lateral Movement
- Data Exfiltration
- Port Scanning
- Suspicious HTTPS Traffic

Each generates realistic APT29 traffic patterns.

### Step 4: Hunt in Kibana

1. Open http://localhost:5601
2. Go to **Discover** (hamburger menu → Analytics → Discover)
3. Select a data view:
   - **zeek-logs-*** for network traffic
   - **sysmon-logs-*** for Windows events
4. Use the detection queries from scenarios to find threats

### Step 5: Follow the Scenarios

Start with Scenario 1 and work your way up:

1. Read the scenario description on the dashboard
2. Start the relevant traffic generator
3. Use the provided Kibana query to search for indicators
4. Analyze the results and understand the technique

## Example: Detecting C2 Beaconing

**Scenario 1: C2 Beaconing**

1. Visit http://localhost:8888
2. Click "Start C2 Beacon"
3. Open Kibana at http://localhost:5601
4. Go to Discover and select "zeek-logs-*"
5. Search for: `service:http AND method:POST`
6. Look for:
   - Regular time intervals between requests
   - Suspicious domains (.tk, .ml)
   - Non-standard User-Agent headers

You'll see the beaconing pattern in the logs!

## Detection Queries Cheat Sheet

Copy these into Kibana's search bar:

```
# C2 Beaconing
service:http AND method:POST

# DNS Tunneling
threat_indicator:potential_dns_tunneling OR (qtype_name:TXT AND query.length > 50)

# Lateral Movement
service:smb OR dest_port:445 OR threat_indicator:potential_lateral_movement

# Credential Dumping
EventID:10 AND TargetImage:*lsass.exe* AND threat_indicator:credential_dumping_attempt

# Encoded PowerShell
EventID:1 AND (CommandLine:*-enc* OR CommandLine:*-encodedcommand*)

# Suspicious Files
EventID:11 AND TargetFilename:(*.exe OR *.dll) AND TargetFilename:(*temp* OR *public*)

# Port Scanning
EventID:3 AND (DestinationPort:22 OR DestinationPort:445 OR DestinationPort:3389)

# Data Exfiltration
method:POST AND (uri:*/upload* OR host:*pastebin*)
```

## Understanding the Logs

### Zeek Network Logs

Zeek monitors network traffic and creates logs for:
- **conn.log** - All network connections
- **http.log** - HTTP requests and responses
- **dns.log** - DNS queries
- **ssl.log** - SSL/TLS connections
- **smb.log** - SMB file sharing traffic

Access these via:
- Zeek Viewer at http://localhost:8080 (simple web interface)
- Kibana at http://localhost:5601 (advanced searching)

### Sysmon Events

Simulated Windows security events:
- **Event ID 1** - Process Creation
- **Event ID 3** - Network Connection
- **Event ID 10** - Process Access (credential dumping)
- **Event ID 11** - File Creation
- **Event ID 22** - DNS Query

These appear in the `sysmon-logs-*` index in Kibana.

## MITRE ATT&CK Coverage

This lab covers these APT29 techniques:

| MITRE ID | Technique | Scenario |
|----------|-----------|----------|
| T1071.001 | Application Layer Protocol: Web | 1, 8 |
| T1071.004 | Application Layer Protocol: DNS | 2 |
| T1021.002 | SMB/Windows Admin Shares | 3 |
| T1003.001 | LSASS Memory Dumping | 4 |
| T1027 | Obfuscated Files or Information | 5 |
| T1105 | Ingress Tool Transfer | 6 |
| T1046 | Network Service Scanning | 7 |
| T1041 | Exfiltration Over C2 Channel | 9 |
| T1053.005 | Scheduled Task/Job | 10 |

## Troubleshooting

### Services won't start

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Restart everything
docker-compose down
docker-compose up -d
```

### No data in Kibana

1. Make sure index patterns are created: `./init/setup-kibana.sh`
2. Start traffic generators at http://localhost:8888
3. Wait 1-2 minutes for logs to appear
4. Refresh the Kibana Discover page

### Elasticsearch out of memory

Edit `docker-compose.yml` and increase:
```yaml
ES_JAVA_OPTS: "-Xms1g -Xmx1g"
```

Then restart: `docker-compose restart elasticsearch`

### Port conflicts

If ports are already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "5601:5601"  # Change left number to different port
```

## System Requirements

- **Docker** and **Docker Compose** installed
- **8GB RAM** minimum (16GB recommended)
- **10GB disk space**
- **Ports required:** 5601, 8000, 8080, 8888, 9200

## Stopping the Lab

```bash
# Stop all containers
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Learning Resources

### Recommended Learning Path

1. **Start with Scenario 1** (C2 Beaconing) - Easiest to understand
2. Work through scenarios 2-5 (Beginner level)
3. Move to scenarios 6-8 (Intermediate)
4. Tackle scenarios 9-10 (Advanced)
5. Try combining techniques - real attacks use multiple methods!

### Additional Practice

- Run multiple traffic generators simultaneously
- Create your own custom Kibana queries
- Build visualizations and dashboards
- Time yourself - how fast can you detect each technique?
- Practice writing detection rules based on what you find

### APT29 Background

APT29 (Cozy Bear, The Dukes) is a Russian threat actor known for:
- Sophisticated spear-phishing campaigns
- Use of multiple malware families
- Long-term persistence in networks
- Credential harvesting and lateral movement
- Data exfiltration focused on intelligence gathering

This lab simulates their common techniques to help you learn detection methods.

## Project Structure

```
threat-hunting-lab/
├── docker-compose.yml          # Main configuration
├── README.md                   # This file
├── init/                       # Setup scripts
│   ├── setup-kibana.sh
│   └── wait-for-services.sh
├── elasticsearch/              # ES configuration
├── logstash/                   # Log processing pipelines
│   └── pipeline/
│       ├── zeek.conf
│       └── sysmon.conf
├── kibana/                     # Kibana settings
├── zeek/                       # Network monitoring
│   ├── Dockerfile
│   └── local.zeek
├── zeek-viewer/                # Web-based log viewer
│   ├── Dockerfile
│   ├── app.py
│   └── templates/
├── sysmon-sim/                 # Sysmon event generator
│   ├── Dockerfile
│   └── sysmon-generator.py
├── traffic-gen/                # APT traffic simulators
│   ├── Dockerfile
│   ├── control-server.py
│   ├── c2_beacon.py
│   ├── dns_tunnel.py
│   ├── lateral_movement.py
│   └── ...
├── control-panel/              # Main dashboard
│   ├── Dockerfile
│   ├── app.py
│   └── templates/
└── scenarios/                  # Hunting scenario definitions
    ├── scenario-01-c2-beaconing.json
    ├── scenario-02-dns-tunneling.json
    └── ...
```

## Security Notice

This lab is designed for **EDUCATION ONLY**:

- Run only in isolated environments
- Do not use on production networks
- Traffic generation scripts are for learning defensive security
- All "attacks" are simulated and harmless
- No actual malware is included

## Contributing

Found a bug or want to add scenarios? Contributions welcome!

## License

MIT License - Free to use for education and training

## Credits

Built for threat hunters, by threat hunters. Inspired by real APT29 campaigns and MITRE ATT&CK framework.

---

**Ready to hunt?** Run `docker-compose up -d` and visit http://localhost:8000

Happy Hunting! 🎯
