#!/usr/bin/env python3
"""
Port Scanning Simulator
Simulates network reconnaissance
"""

import time
import socket
import random

def run_port_scan(is_running):
    """Simulate port scanning"""
    print("Starting Port Scan simulation...")

    # Common target ports
    common_ports = [21, 22, 23, 25, 80, 443, 445, 3389, 8080, 8443]

    while is_running():
        try:
            # Scan random internal IP
            target_ip = f"10.0.0.{random.randint(1, 254)}"

            print(f"[SCAN] Scanning {target_ip}")

            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    sock.connect((target_ip, port))
                    print(f"[SCAN] Port {port} open on {target_ip}")
                    sock.close()
                except:
                    pass

            time.sleep(random.uniform(120, 300))

        except Exception as e:
            print(f"[SCAN] Error: {e}")
            time.sleep(10)

    print("Port Scan simulation stopped")
