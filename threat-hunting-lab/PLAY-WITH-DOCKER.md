# Running on Play with Docker

Play with Docker is a free, browser-based Docker playground. Perfect for trying this lab without any installation!

## Quick Start (3 minutes)

### Step 1: Access Play with Docker

1. Visit: **https://labs.play-with-docker.com/**
2. Click **"Login"** (sign in with Docker Hub - it's free)
3. Click **"Start"**
4. Click **"+ ADD NEW INSTANCE"** (creates a new virtual machine)

You'll see a terminal in your browser!

### Step 2: Clone and Setup

In the terminal, run:

```bash
# Clone the repository
git clone https://github.com/mhouston-55/learning.git
cd learning/threat-hunting-lab

# Reduce memory usage for Play with Docker environment
sed -i 's/512m/256m/g' docker-compose.yml

# Start the lab
docker-compose up -d
```

### Step 3: Wait for Services

```bash
# Check status (wait until all are "Up")
docker-compose ps

# This should take 2-3 minutes
```

### Step 4: Access Web Interfaces

Play with Docker automatically detects open ports and shows them at the top of the screen.

Look for port numbers like **5601**, **8000**, **8080**, **8888** appearing as blue clickable links at the top.

**Click these ports to access:**
- **8000** - Main Dashboard (START HERE!)
- **5601** - Kibana
- **8080** - Zeek Viewer
- **8888** - Traffic Generator

### Step 5: Initialize Kibana

Back in the terminal:

```bash
# Wait for services
./init/wait-for-services.sh

# Setup Kibana index patterns
./init/setup-kibana.sh
```

### Step 6: Start Hunting!

Click port **8000** at the top to open the Main Dashboard and begin with Scenario 1!

## Important Notes

### Session Duration
- **4-hour limit** - Sessions automatically end after 4 hours
- You'll need to start over if you return later
- Plan your learning sessions accordingly

### Memory Constraints
- Play with Docker provides limited RAM
- We reduced Elasticsearch memory to 256MB (line 13 above)
- All scenarios will still work, just with less historical data

### Saving Your Work
- Sessions don't persist
- Take screenshots of interesting findings
- Copy any detection queries you create
- All code is in GitHub, so you can always restart

### If Services Fail to Start

```bash
# Check logs
docker-compose logs

# Try restarting specific service
docker-compose restart elasticsearch

# Or restart everything
docker-compose down
docker-compose up -d
```

### Viewing Logs in Real-Time

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f sysmon-sim

# Stop following: Ctrl+C
```

## Optimized docker-compose for Play with Docker

If you want to manually optimize further, edit `docker-compose.yml`:

```yaml
elasticsearch:
  environment:
    - "ES_JAVA_OPTS=-Xms256m -Xmx256m"  # Already done by sed command

# You can also disable Zeek if needed:
# Comment out the zeek service to save memory
```

## Troubleshooting

### Ports Not Showing Up

Wait 30 seconds after starting containers. If still not visible:

```bash
# Manually check what ports are open
docker-compose ps

# Restart the service
docker-compose restart control-panel
```

### Out of Memory Errors

```bash
# Stop optional services
docker-compose stop zeek

# Or reduce running scenarios
# Just use Kibana and Sysmon simulator
```

### Slow Performance

This is normal on Play with Docker's free tier. The lab is fully functional, just a bit slower than running locally.

### Connection Timeouts

Play with Docker may have network restrictions. Some external DNS queries in scenarios won't resolve, but this doesn't affect learning - you'll still see the traffic patterns in logs.

## Tips for Best Experience

1. **Use full screen** - Click the fullscreen icon in terminal
2. **Split terminal** - Right-click terminal → "Split Horizontally" to run multiple commands
3. **Bookmark the session** - Save your Play with Docker session URL to return within 4 hours
4. **Focus on 2-3 scenarios per session** - Given the 4-hour limit
5. **Start with Scenario 1** - Easiest to understand and detect

## Alternative Commands

### Quick Status Check
```bash
# One-liner to check everything
docker-compose ps && docker stats --no-stream
```

### Generate Sample Traffic Immediately
```bash
# Sysmon events generate automatically
# For network traffic, visit port 8888 and click buttons

# Or via command line:
docker exec -it threat-lab-traffic-gen python -c "from c2_beacon import run_c2_beacon; run_c2_beacon(lambda: True)"
```

### Clean Stop
```bash
# Before session ends, clean shutdown
docker-compose down

# Remove all data
docker-compose down -v
```

## Extending Your Session

Play with Docker sessions are strictly 4 hours. To continue:

1. Take notes on what you learned
2. Copy any custom queries you created
3. Let the session end
4. Start a new session and repeat the setup (takes 3 minutes)

## Comparison: Play with Docker vs Codespaces

| Feature | Play with Docker | GitHub Codespaces |
|---------|------------------|-------------------|
| **Cost** | Free (unlimited) | Free (60 hrs/month) |
| **Session Length** | 4 hours | Until you stop it |
| **Memory** | ~4GB | 4-16GB |
| **Persistence** | None | Full persistence |
| **Setup Time** | 3 minutes | 2 minutes |
| **Best For** | Quick testing | Serious learning |

## Next Steps

Once running:
1. Click port 8000 for Main Dashboard
2. Read Scenario 1: C2 Beaconing
3. Click port 8888 to start the C2 traffic generator
4. Click port 5601 to open Kibana
5. Use the provided query to hunt for beacons!

Happy Hunting! 🎯

---

**Need help?** Check the main [README.md](README.md) or [CODESPACES.md](CODESPACES.md) for alternatives.
