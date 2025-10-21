#!/usr/bin/env python3
"""
C2 Beaconing Simulator
Simulates APT29 command-and-control beaconing behavior
"""

import time
import requests
import random

def run_c2_beacon(is_running):
    """Simulate C2 beaconing with regular intervals"""
    print("Starting C2 Beacon simulation...")

    c2_servers = [
        "http://malicious-c2-server.com",
        "http://apt29-infrastructure.net",
        "http://cozy-bear-c2.tk",
    ]

    beacon_interval = 60  # seconds

    while is_running():
        try:
            # Generate beacon request
            server = random.choice(c2_servers)
            endpoint = random.choice(["/api/check", "/update", "/status"])

            # Add jitter to avoid perfect timing detection
            jitter = random.uniform(-5, 5)

            print(f"[C2] Sending beacon to {server}{endpoint}")

            # Try to make request (will fail, but generates network traffic)
            try:
                requests.get(
                    f"{server}{endpoint}",
                    timeout=5,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                        "X-Session-ID": f"session-{random.randint(1000, 9999)}",
                    }
                )
            except Exception as e:
                # Expected to fail, we just want to generate traffic
                pass

            time.sleep(beacon_interval + jitter)

        except Exception as e:
            print(f"[C2] Error: {e}")
            time.sleep(10)

    print("C2 Beacon simulation stopped")
