# Quick Start (Without Zeek)

If you want to start the lab faster and focus on Sysmon events and endpoint detection, you can skip Zeek:

```bash
cd threat-hunting-lab

# Start without Zeek (faster, less memory)
docker-compose up -d elasticsearch kibana logstash sysmon-sim traffic-gen control-panel

# Wait for services
./init/wait-for-services.sh

# Setup Kibana
./init/setup-kibana.sh
```

This starts the lab in ~60 seconds instead of 3-5 minutes and uses less memory.

**What you still get:**
- ✅ All 10 hunting scenarios
- ✅ Sysmon event logs (process creation, network connections, file creation, etc.)
- ✅ Kibana for log analysis
- ✅ Traffic generators
- ✅ Full learning experience

**What you miss:**
- ❌ Zeek network packet analysis
- ❌ Zeek log viewer at port 8080

For most learning scenarios, the Sysmon logs are sufficient!

## Starting Full Lab (With Zeek)

If you want the complete experience with network packet analysis:

```bash
docker-compose up -d
```

Note: First build takes 5-10 minutes as it compiles Zeek from source.
