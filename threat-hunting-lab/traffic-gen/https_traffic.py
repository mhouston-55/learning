#!/usr/bin/env python3
"""
Suspicious HTTPS Traffic Simulator
Generates HTTPS traffic with suspicious patterns
"""

import time
import requests
import random

def run_https_traffic(is_running):
    """Simulate suspicious HTTPS traffic"""
    print("Starting Suspicious HTTPS Traffic simulation...")

    suspicious_domains = [
        "https://ngrok-tunnel-abc123.io",
        "https://dyndns-host-xyz.net",
        "https://temporary-host-456.tk",
    ]

    while is_running():
        try:
            domain = random.choice(suspicious_domains)
            endpoint = random.choice(["/api", "/upload", "/download", "/cmd"])

            print(f"[HTTPS] Connecting to {domain}{endpoint}")

            try:
                requests.get(
                    f"{domain}{endpoint}",
                    timeout=5,
                    verify=False,
                    headers={
                        "User-Agent": "CustomAgent/1.0",
                    }
                )
            except:
                pass

            time.sleep(random.uniform(45, 90))

        except Exception as e:
            print(f"[HTTPS] Error: {e}")
            time.sleep(10)

    print("Suspicious HTTPS Traffic simulation stopped")
