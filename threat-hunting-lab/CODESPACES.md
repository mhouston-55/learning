# Running Threat Hunting Lab in GitHub Codespaces

GitHub Codespaces provides a free, browser-based environment to run this lab without installing Docker locally.

## Quick Start (5 minutes)

### Step 1: Create a Codespace

1. Go to your GitHub repository: https://github.com/mhouston-55/learning
2. Click the green **"Code"** button
3. Click the **"Codespaces"** tab
4. Click **"Create codespace on [your-branch]"**
5. Wait 1-2 minutes for the environment to initialize

### Step 2: Start the Lab

Once your Codespace loads, you'll see VS Code in your browser with a terminal at the bottom.

In the terminal, run:

```bash
cd threat-hunting-lab
docker-compose up -d
```

Wait 2-3 minutes for all containers to start.

### Step 3: Access Web Interfaces

Codespaces automatically forwards ports. You'll see notifications pop up saying "Your application running on port XXXX is available."

**To access the services:**

1. Click the **"Ports"** tab at the bottom (next to Terminal)
2. You'll see all forwarded ports (5601, 8000, 8080, 8888, 9200)
3. Hover over a port and click the **globe icon** to open in browser
4. Or right-click → "Open in Browser"

**Main interfaces:**
- Port 8000: Main Dashboard (start here!)
- Port 5601: Kibana
- Port 8080: Zeek Viewer
- Port 8888: Traffic Generator

### Step 4: Initialize Kibana

In the terminal, run:

```bash
./init/wait-for-services.sh
./init/setup-kibana.sh
```

### Step 5: Start Hunting!

Click on Port 8000 to open the main dashboard and start your first scenario.

## Important Tips

### Managing Your Free Hours

- **Free tier:** 60 hours/month
- **Stop your Codespace when not using it:**
  - Go to https://github.com/codespaces
  - Click the three dots next to your Codespace
  - Click "Stop codespace"
- **Auto-timeout:** Codespaces auto-stop after 30 minutes of inactivity (configurable)

### Checking Resource Usage

Monitor your usage at: https://github.com/settings/billing

### Reducing Memory Usage

If you hit memory limits, edit `docker-compose.yml`:

```yaml
elasticsearch:
  environment:
    - "ES_JAVA_OPTS=-Xms256m -Xmx256m"  # Reduced from 512m
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### Saving Your Progress

Your Codespace persists between sessions. All logs and data remain saved.

### Accessing Logs

```bash
# View logs for specific service
docker-compose logs -f kibana

# View all logs
docker-compose logs -f

# Check container status
docker-compose ps
```

## Troubleshooting

### Port Not Accessible

1. Go to "Ports" tab
2. Check if port is listed
3. Right-click port → "Port Visibility" → "Public"

### Services Won't Start

```bash
# Check what's running
docker-compose ps

# Restart everything
docker-compose down
docker-compose up -d

# Check available memory
free -h
```

### Out of Memory

Codespaces free tier provides 4GB RAM. To reduce usage:

1. Stop unused containers:
   ```bash
   docker-compose stop zeek
   ```

2. Reduce Elasticsearch memory (see above)

3. Upgrade to larger Codespace (paid):
   - Settings → Change machine type → 8-core (16GB RAM)

## Alternative: Use Play with Docker

If you run out of Codespaces hours, use Play with Docker:

1. Visit: https://labs.play-with-docker.com/
2. Login with Docker Hub account
3. Click "Start" → "Add New Instance"
4. Run:
   ```bash
   git clone https://github.com/mhouston-55/learning.git
   cd learning/threat-hunting-lab

   # Reduce memory first
   sed -i 's/512m/256m/g' docker-compose.yml

   docker-compose up -d
   ```
5. Click port numbers that appear at top to access services

**Note:** Play with Docker sessions last 4 hours, then reset.

## Cost-Free Options Summary

| Platform | Free Tier | Session Length | Memory | Best For |
|----------|-----------|----------------|--------|----------|
| **GitHub Codespaces** | 60 hrs/month | Until you stop | 4GB (free) | Extended learning |
| **Play with Docker** | Unlimited | 4 hours | ~4GB | Quick testing |
| **Gitpod** | 50 hrs/month | Until you stop | 4GB | Alternative to Codespaces |

## Upgrading Codespaces (Optional)

For better performance:

1. Go to your Codespace settings
2. Change machine type to 4-core or 8-core
3. Costs: ~$0.18/hour for 4-core

This gives you more memory and faster performance, but uses free hours faster.

## Next Steps

Once your Codespace is running:

1. Open the Main Dashboard (Port 8000)
2. Read the scenarios
3. Start with Scenario 1: C2 Beaconing
4. Have fun hunting!

---

**Questions?** Check the main [README.md](README.md) or GitHub Codespaces docs: https://docs.github.com/en/codespaces
