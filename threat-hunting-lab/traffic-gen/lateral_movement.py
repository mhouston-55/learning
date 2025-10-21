#!/usr/bin/env python3
"""
Lateral Movement Simulator
Simulates SMB/RPC lateral movement patterns
"""

import time
import socket
import random

def run_lateral_movement(is_running):
    """Simulate lateral movement via SMB"""
    print("Starting Lateral Movement simulation...")

    # Common internal IP ranges
    target_ips = [
        f"10.0.0.{i}" for i in range(1, 255)
    ]

    # SMB and RPC ports
    lateral_ports = [
        445,   # SMB
        135,   # RPC
        139,   # NetBIOS
        5985,  # WinRM
    ]

    while is_running():
        try:
            target_ip = random.choice(target_ips)
            target_port = random.choice(lateral_ports)

            print(f"[LATERAL] Attempting connection to {target_ip}:{target_port}")

            # Attempt connection (will fail but generates traffic)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((target_ip, target_port))
                sock.close()
            except:
                pass

            time.sleep(random.uniform(10, 30))

        except Exception as e:
            print(f"[LATERAL] Error: {e}")
            time.sleep(10)

    print("Lateral Movement simulation stopped")
