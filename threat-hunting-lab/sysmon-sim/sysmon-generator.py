#!/usr/bin/env python3
"""
Sysmon Event Generator - Simulates Windows Sysmon Events
Generates realistic Sysmon events for threat hunting practice
"""

import json
import random
import time
from datetime import datetime, timedelta
import hashlib
import os

OUTPUT_DIR = "/sysmon-logs"

# Common legitimate processes
LEGIT_PROCESSES = [
    "C:\\Windows\\System32\\svchost.exe",
    "C:\\Windows\\System32\\explorer.exe",
    "C:\\Windows\\System32\\lsass.exe",
    "C:\\Program Files\\Microsoft Office\\WINWORD.EXE",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Windows\\System32\\cmd.exe",
]

# Suspicious processes for APT scenarios
SUSPICIOUS_PROCESSES = [
    "C:\\Windows\\Temp\\update.exe",
    "C:\\Users\\Public\\Downloads\\installer.exe",
    "C:\\ProgramData\\Microsoft\\beacon.exe",
    "powershell.exe -enc JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQ==",
    "cmd.exe /c whoami & ipconfig /all",
    "wmic.exe process call create",
]

# DNS queries
LEGIT_DOMAINS = [
    "www.microsoft.com",
    "www.google.com",
    "api.office.com",
    "www.github.com",
]

SUSPICIOUS_DOMAINS = [
    "malicious-c2.tk",
    "data-exfil.ml",
    "ngrok-tunnel-12345.io",
    "pastebin.com/raw/suspicious",
    "dyndns-c2-server.net",
]

# Common ports
COMMON_PORTS = [80, 443, 53, 445, 3389]
SUSPICIOUS_PORTS = [4444, 5555, 8080, 31337, 1337]

class SysmonEventGenerator:
    def __init__(self):
        self.event_id = 1000
        self.process_guid = 1000

    def generate_guid(self):
        """Generate a realistic Windows GUID"""
        self.process_guid += 1
        return f"{{12345678-90AB-{self.process_guid:04X}-CDEF-1234567890AB}}"

    def generate_hash(self, filename):
        """Generate a fake but realistic hash"""
        return hashlib.md5(filename.encode()).hexdigest().upper()

    def get_timestamp(self):
        """Get current timestamp"""
        return datetime.utcnow().isoformat() + 'Z'

    def generate_process_create(self, suspicious=False):
        """Event ID 1 - Process Creation"""
        if suspicious:
            image = random.choice(SUSPICIOUS_PROCESSES)
            parent = "C:\\Windows\\System32\\cmd.exe"
            command_line = image
        else:
            image = random.choice(LEGIT_PROCESSES)
            parent = "C:\\Windows\\System32\\services.exe"
            command_line = image

        event = {
            "EventID": 1,
            "EventType": "ProcessCreate",
            "UtcTime": self.get_timestamp(),
            "ProcessGuid": self.generate_guid(),
            "ProcessId": random.randint(1000, 9999),
            "Image": image,
            "CommandLine": command_line,
            "User": "DOMAIN\\user" if not suspicious else "DOMAIN\\admin",
            "ParentProcessGuid": self.generate_guid(),
            "ParentProcessId": random.randint(500, 5000),
            "ParentImage": parent,
            "Hashes": f"MD5={self.generate_hash(image)}",
        }

        if suspicious:
            event["Suspicious"] = True
            event["ThreatIndicator"] = "suspicious_process_execution"

        return event

    def generate_network_connection(self, suspicious=False):
        """Event ID 3 - Network Connection"""
        if suspicious:
            dest_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            dest_port = random.choice(SUSPICIOUS_PORTS)
            image = random.choice(SUSPICIOUS_PROCESSES)
        else:
            dest_ip = "8.8.8.8"
            dest_port = random.choice(COMMON_PORTS)
            image = random.choice(LEGIT_PROCESSES)

        event = {
            "EventID": 3,
            "EventType": "NetworkConnect",
            "UtcTime": self.get_timestamp(),
            "ProcessGuid": self.generate_guid(),
            "ProcessId": random.randint(1000, 9999),
            "Image": image,
            "User": "DOMAIN\\user",
            "Protocol": "tcp",
            "SourceIp": "10.0.0.100",
            "SourcePort": random.randint(49152, 65535),
            "DestinationIp": dest_ip,
            "DestinationPort": dest_port,
        }

        if suspicious:
            event["Suspicious"] = True
            event["ThreatIndicator"] = "suspicious_network_connection"

        return event

    def generate_process_access(self, suspicious=False):
        """Event ID 10 - Process Access (Credential Dumping)"""
        if suspicious:
            source = "C:\\Users\\admin\\mimikatz.exe"
            target = "C:\\Windows\\System32\\lsass.exe"
            granted_access = "0x1FFFFF"  # Full access
        else:
            source = "C:\\Windows\\System32\\svchost.exe"
            target = "C:\\Windows\\System32\\services.exe"
            granted_access = "0x1000"

        event = {
            "EventID": 10,
            "EventType": "ProcessAccess",
            "UtcTime": self.get_timestamp(),
            "SourceProcessGuid": self.generate_guid(),
            "SourceProcessId": random.randint(1000, 9999),
            "SourceImage": source,
            "TargetProcessGuid": self.generate_guid(),
            "TargetProcessId": random.randint(1000, 9999),
            "TargetImage": target,
            "GrantedAccess": granted_access,
        }

        if suspicious:
            event["Suspicious"] = True
            event["ThreatIndicator"] = "credential_dumping_attempt"
            event["MitreTechnique"] = "T1003.001 - LSASS Memory"

        return event

    def generate_file_create(self, suspicious=False):
        """Event ID 11 - File Creation"""
        if suspicious:
            target_file = f"C:\\Users\\Public\\{random.choice(['malware', 'backdoor', 'payload'])}.exe"
            image = "C:\\Windows\\Temp\\dropper.exe"
        else:
            target_file = f"C:\\Users\\user\\Documents\\report_{random.randint(1,100)}.docx"
            image = "C:\\Program Files\\Microsoft Office\\WINWORD.EXE"

        event = {
            "EventID": 11,
            "EventType": "FileCreate",
            "UtcTime": self.get_timestamp(),
            "ProcessGuid": self.generate_guid(),
            "ProcessId": random.randint(1000, 9999),
            "Image": image,
            "TargetFilename": target_file,
        }

        if suspicious:
            event["Suspicious"] = True
            event["ThreatIndicator"] = "suspicious_file_creation"

        return event

    def generate_dns_query(self, suspicious=False):
        """Event ID 22 - DNS Query"""
        if suspicious:
            query = random.choice(SUSPICIOUS_DOMAINS)
            image = random.choice(SUSPICIOUS_PROCESSES)
        else:
            query = random.choice(LEGIT_DOMAINS)
            image = random.choice(LEGIT_PROCESSES)

        event = {
            "EventID": 22,
            "EventType": "DnsQuery",
            "UtcTime": self.get_timestamp(),
            "ProcessGuid": self.generate_guid(),
            "ProcessId": random.randint(1000, 9999),
            "Image": image,
            "QueryName": query,
            "QueryResults": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        }

        if suspicious:
            event["Suspicious"] = True
            event["ThreatIndicator"] = "suspicious_dns_query"

        return event

    def write_event(self, event):
        """Write event to JSON log file"""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = os.path.join(OUTPUT_DIR, f"sysmon-{date_str}.json")

        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def run(self):
        """Main loop to generate events"""
        print("Starting Sysmon Event Generator...")
        print(f"Writing logs to {OUTPUT_DIR}")

        while True:
            # Generate mix of legitimate and suspicious events
            # 70% legitimate, 30% suspicious
            is_suspicious = random.random() < 0.3

            # Choose random event type
            event_generators = [
                self.generate_process_create,
                self.generate_network_connection,
                self.generate_process_access,
                self.generate_file_create,
                self.generate_dns_query,
            ]

            generator = random.choice(event_generators)
            event = generator(suspicious=is_suspicious)

            self.write_event(event)

            if is_suspicious:
                print(f"[SUSPICIOUS] Generated Event ID {event['EventID']}: {event.get('ThreatIndicator', 'N/A')}")
            else:
                print(f"[NORMAL] Generated Event ID {event['EventID']}")

            # Random delay between events (1-5 seconds)
            time.sleep(random.uniform(1, 5))

if __name__ == "__main__":
    generator = SysmonEventGenerator()
    generator.run()
