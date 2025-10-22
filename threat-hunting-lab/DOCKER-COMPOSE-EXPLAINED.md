# Docker Compose Explained - Line by Line

A beginner-friendly guide to understanding the `docker-compose.yml` file.

## What is Docker Compose?

**Think of it like this:**
- **Docker** = A way to run applications in isolated "containers" (like lightweight virtual machines)
- **Docker Compose** = A tool to manage multiple containers that work together
- **docker-compose.yml** = The recipe/blueprint that tells Docker Compose what to build

Instead of running 7 separate `docker run` commands, we define everything in one file and run `docker-compose up`.

---

## Overall Structure

```yaml
services:        # All the containers we want to run
  elasticsearch: # Container 1
  kibana:        # Container 2
  ...

volumes:         # Persistent storage (survives container restarts)
  elastic-data:
  ...

networks:        # How containers talk to each other
  threat-lab:
```

**Analogy:** Think of it like a restaurant:
- **Services** = The kitchen stations (prep, grill, dessert)
- **Volumes** = The pantry (persistent storage)
- **Networks** = The communication system between stations

---

## Line 1: `services:`

```yaml
services:
```

**What it means:** "Here are all the containers I want to run"

Everything indented under this is a separate container.

---

## Service 1: Elasticsearch (Lines 3-21)

### The Basics

```yaml
elasticsearch:                    # Name of this service
  image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  container_name: threat-lab-elasticsearch
```

**Line by line:**
- `elasticsearch:` - This is the service name (we can reference it as "elasticsearch")
- `image:` - Download a pre-built container from the internet
  - Like downloading an app from an app store
  - `docker.elastic.co` = where to download from
  - `elasticsearch:8.11.0` = what app, which version
- `container_name:` - The actual name of the running container
  - Like naming your phone "John's iPhone"

### Environment Variables

```yaml
environment:
  - discovery.type=single-node
  - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
  - xpack.security.enabled=false
  - xpack.security.http.ssl.enabled=false
```

**What it means:** Configuration settings for Elasticsearch

**Line by line:**
- `discovery.type=single-node` - Run as a single server (not a cluster)
- `ES_JAVA_OPTS=-Xms512m -Xmx512m` - Use 512MB of RAM
  - `-Xms` = minimum memory
  - `-Xmx` = maximum memory
- `xpack.security.enabled=false` - Turn off password protection (easier for learning)
- `xpack.security.http.ssl.enabled=false` - Don't require HTTPS

**Analogy:** Like settings on your phone - WiFi on/off, brightness level, etc.

### Ports

```yaml
ports:
  - "9200:9200"
```

**What it means:** Map ports from container to your computer

**Format:** `"HOST_PORT:CONTAINER_PORT"`
- `9200` (left) = Port on your computer
- `9200` (right) = Port inside the container

**Analogy:** Like forwarding your home phone to your cell phone
- Someone calls your home (port 9200 on host)
- The call reaches you on your cell (port 9200 in container)

**Result:** You can access Elasticsearch at `http://localhost:9200`

### Volumes

```yaml
volumes:
  - elastic-data:/usr/share/elasticsearch/data
```

**What it means:** Save data permanently (even if container is deleted)

**Format:** `VOLUME_NAME:PATH_IN_CONTAINER`
- `elastic-data` = Named storage space (defined at bottom of file)
- `/usr/share/elasticsearch/data` = Where Elasticsearch stores data inside container

**Analogy:** Like an external hard drive
- If you delete the app (container), the hard drive (volume) keeps your files
- Reinstall the app, and your files are still there

### Networks

```yaml
networks:
  - threat-lab
```

**What it means:** Connect this container to the `threat-lab` network

**Why?** So containers can talk to each other
- Kibana needs to talk to Elasticsearch
- All containers on same network can communicate

**Analogy:** Like connecting devices to the same WiFi network so they can share files

### Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 5
```

**What it means:** Check if Elasticsearch is actually working

**Line by line:**
- `test:` - Command to check health
  - `curl` = Make a web request
  - `http://localhost:9200/_cluster/health` = Ask Elasticsearch "are you healthy?"
  - `|| exit 1` = If that fails, return error
- `interval: 30s` - Check every 30 seconds
- `timeout: 10s` - Wait 10 seconds for response
- `retries: 5` - Try 5 times before giving up

**Analogy:** Like a heart monitor
- Checks pulse every 30 seconds
- If no response after 10 seconds, it's a problem
- Only declare patient dead after 5 failed attempts

---

## Service 2: Kibana (Lines 24-41)

```yaml
kibana:
  image: docker.elastic.co/kibana/kibana:8.11.0
  container_name: threat-lab-kibana
  ports:
    - "5601:5601"
  environment:
    - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    - xpack.security.enabled=false
```

**New concept here:**

```yaml
environment:
  - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

**What it means:** Tell Kibana where to find Elasticsearch

Notice: We use `elasticsearch` (the service name), not an IP address!
- Docker's network automatically converts `elasticsearch` to the right IP
- Like using a contact name instead of phone number

### Depends On

```yaml
depends_on:
  elasticsearch:
    condition: service_healthy
```

**What it means:** Don't start Kibana until Elasticsearch is healthy

**Why?** Kibana needs Elasticsearch to be running first

**The flow:**
1. Start Elasticsearch
2. Wait for healthcheck to pass
3. THEN start Kibana

**Analogy:** Don't open the restaurant (Kibana) until the kitchen (Elasticsearch) is ready

---

## Service 3: Logstash (Lines 44-59)

```yaml
logstash:
  image: docker.elastic.co/logstash/logstash:8.11.0
  ports:
    - "5044:5044"
    - "9600:9600"
```

**New concept:** Multiple ports
- `5044` - Receives log data
- `9600` - Monitoring/status API

### File Mounts

```yaml
volumes:
  - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
  - ./logstash/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
  - zeek-logs:/zeek-logs:ro
  - sysmon-logs:/sysmon-logs:ro
```

**Two types of volumes here:**

**Type 1: Local Files** (note the `./`)
```yaml
- ./logstash/pipeline:/usr/share/logstash/pipeline:ro
```
- `./logstash/pipeline` = Folder on your computer
- `:ro` = Read-only (container can't modify these files)

**Type 2: Named Volumes**
```yaml
- zeek-logs:/zeek-logs:ro
```
- `zeek-logs` = Shared storage space
- Other containers can write here, Logstash reads from it

**Analogy:**
- Local files = Your personal notebook (reference material)
- Named volumes = Shared inbox (multiple people can put mail in it)

---

## Service 4: Zeek (Lines 62-73)

```yaml
zeek:
  build:
    context: ./zeek
    dockerfile: Dockerfile
  container_name: threat-lab-zeek
```

**New concept: Build instead of Image**

```yaml
build:
  context: ./zeek           # Look in this folder
  dockerfile: Dockerfile     # Use this file to build the image
```

**What's the difference?**
- `image:` = Download pre-built container
- `build:` = Build container from source code

**Analogy:**
- `image` = Buy frozen pizza from store
- `build` = Make pizza from scratch using a recipe (Dockerfile)

### Capabilities

```yaml
cap_add:
  - NET_ADMIN
  - NET_RAW
```

**What it means:** Give container special permissions

- `NET_ADMIN` = Can configure network settings
- `NET_RAW` = Can capture network packets

**Why?** Zeek needs to monitor network traffic (like Wireshark)

**Analogy:** Like giving an app "camera access" or "location access" on your phone

---

## Service 5: Zeek Viewer (Lines 76-86)

```yaml
zeek-viewer:
  build:
    context: ./zeek-viewer
    dockerfile: Dockerfile
  ports:
    - "8080:8080"
  volumes:
    - zeek-logs:/zeek-logs:ro
```

**Key point:**
- Zeek writes to `zeek-logs` volume
- Zeek-viewer reads from same `zeek-logs` volume
- They share data through the volume!

**Analogy:** Two apps sharing the same Google Drive folder

---

## Service 6: Sysmon Simulator (Lines 89-97)

```yaml
sysmon-sim:
  build:
    context: ./sysmon-sim
    dockerfile: Dockerfile
  volumes:
    - sysmon-logs:/sysmon-logs
```

**Note:** No `:ro` (read-only) this time
- This container WRITES log files
- Logstash (earlier) READS them

---

## Service 7: Traffic Generator (Lines 100-110)

```yaml
traffic-gen:
  depends_on:
    - zeek
```

**What it means:** Start Zeek before traffic-gen

**Why?**
- Traffic generator creates network activity
- Zeek needs to be running to capture that activity
- Order matters!

---

## Service 8: Control Panel (Lines 113-126)

```yaml
control-panel:
  volumes:
    - ./scenarios:/scenarios:ro
  depends_on:
    kibana:
      condition: service_healthy
```

**Two key points:**

1. **Local file mount:**
   ```yaml
   - ./scenarios:/scenarios:ro
   ```
   - Maps the `scenarios` folder from your computer into the container
   - Control panel can read scenario JSON files

2. **Wait for Kibana:**
   - Don't show dashboard until Kibana is ready
   - Otherwise, users might click links before services are up

---

## Volumes Section (Lines 128-131)

```yaml
volumes:
  elastic-data:
  zeek-logs:
  sysmon-logs:
```

**What it means:** Define named storage volumes

These are like declaring variables:
- Just names here
- Used throughout the file
- Docker creates the actual storage

**Analogy:** Like creating shared folders in Dropbox
- You declare the folders exist
- Multiple apps can access them
- Data persists even if you uninstall apps

---

## Networks Section (Lines 133-135)

```yaml
networks:
  threat-lab:
    driver: bridge
```

**What it means:** Create a private network for our containers

- `threat-lab` = Network name
- `driver: bridge` = Type of network (most common)

**How it works:**
- All containers on `threat-lab` network can see each other
- They're isolated from the rest of your computer
- They can use service names (like `elasticsearch`) instead of IP addresses

**Analogy:** Like a private WiFi network
- All devices on network can talk to each other
- Devices outside can't see your traffic
- You can use device names instead of IP addresses

---

## Putting It All Together

### The Flow When You Run `docker-compose up`:

1. **Create network:** `threat-lab`
2. **Create volumes:** `elastic-data`, `zeek-logs`, `sysmon-logs`
3. **Start Elasticsearch** (no dependencies)
4. **Wait** for Elasticsearch healthcheck ✓
5. **Start Kibana** (depends on Elasticsearch)
6. **Start Logstash** (depends on Elasticsearch)
7. **Build and start Zeek** (no dependencies)
8. **Start Traffic Generator** (depends on Zeek)
9. **Start Sysmon Simulator** (no dependencies)
10. **Start Zeek Viewer** (no dependencies)
11. **Wait** for Kibana healthcheck ✓
12. **Start Control Panel** (depends on Kibana)

### Data Flow:

```
[Sysmon Simulator] → writes → [sysmon-logs volume]
                                      ↓
[Zeek] → writes → [zeek-logs volume]  ↓
                         ↓             ↓
            [Logstash] ← reads ← ← ← ←
                   ↓
            processes & enriches
                   ↓
            [Elasticsearch] ← stores logs
                   ↓
            [Kibana] ← visualizes data
                   ↓
            [You!] ← hunt for threats
```

---

## Common Modifications

### Change Memory Allocation

```yaml
environment:
  - "ES_JAVA_OPTS=-Xms256m -Xmx256m"  # Reduce to 256MB
```

### Change Port Mapping

```yaml
ports:
  - "8081:8080"  # Access on port 8081 instead of 8080
```

### Add New Service

```yaml
services:
  my-new-service:
    image: some-image:latest
    ports:
      - "9999:9999"
    networks:
      - threat-lab
```

---

## Key Concepts Summary

| Concept | What It Is | Example |
|---------|------------|---------|
| **Service** | A container to run | `elasticsearch:` |
| **Image** | Pre-built container | `image: elasticsearch:8.11.0` |
| **Build** | Build from Dockerfile | `build: ./zeek` |
| **Port** | Expose to host | `"8080:8080"` |
| **Volume** | Persistent storage | `elastic-data:/path` |
| **Network** | Container communication | `networks: - threat-lab` |
| **Environment** | Configuration variables | `ES_JAVA_OPTS=-Xms512m` |
| **Depends On** | Start order | `depends_on: - elasticsearch` |
| **Health Check** | Is service ready? | `curl http://localhost:9200` |

---

## Troubleshooting Tips

### Check What's Running
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs elasticsearch
docker-compose logs -f  # Follow all logs
```

### Restart Single Service
```bash
docker-compose restart kibana
```

### Check Network
```bash
docker network ls
docker network inspect threat-hunting-lab_threat-lab
```

### Check Volumes
```bash
docker volume ls
docker volume inspect threat-hunting-lab_elastic-data
```

---

## Questions & Answers

**Q: Why not just use one big container?**
A: Separation of concerns. Each service does one thing. Easier to debug, update, and scale.

**Q: What happens to volumes when I run `docker-compose down`?**
A: Volumes persist! Use `docker-compose down -v` to remove them.

**Q: Can containers access the internet?**
A: Yes! They can access outside, but outside can't access them (unless you map ports).

**Q: Why use service names instead of IP addresses?**
A: Docker handles DNS. Service names always work even if IPs change.

**Q: How much disk space does this use?**
A: Images ~2GB, volumes grow with data (typically <1GB for this lab).

---

## Further Reading

- [Docker Compose Official Docs](https://docs.docker.com/compose/)
- [Docker Networking](https://docs.docker.com/network/)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)

---

**Now you understand every line!** 🎉

The docker-compose.yml is just a blueprint that tells Docker:
1. What containers to run
2. How to configure them
3. How they communicate
4. Where to store data

Everything else is just details!
