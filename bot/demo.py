"""
telnoc demo data seeder.

Used for screenshots and local smoke tests. All values are synthetic
(RFC 5737 TEST-NET addresses, example hostnames) and safe to commit to docs.
"""

import time

DEMO_AGENTS = [
    {
        "hostname": "demo-lx-01",
        "ip": "198.51.100.11",
        "url": "http://198.51.100.11:7845",
        "os": "linux",
        "version": "0.1.0",
        "roles": ["web", "metrics"],
        "status": "online",
        "last_seen": time.time(),
        "cpu": 34,
        "memory": 62,
        "disk": 45,
        "uptime": "12d 4h 33m",
    },
    {
        "hostname": "demo-lx-02",
        "ip": "198.51.100.12",
        "url": "http://198.51.100.12:7845",
        "os": "linux",
        "version": "0.1.0",
        "roles": ["db"],
        "status": "online",
        "last_seen": time.time(),
        "cpu": 76,
        "memory": 81,
        "disk": 67,
        "uptime": "5d 19h 12m",
    },
    {
        "hostname": "demo-win-01",
        "ip": "198.51.100.21",
        "url": "http://198.51.100.21:7845",
        "os": "windows",
        "version": "0.1.0",
        "roles": ["ad", "dns"],
        "status": "offline",
        "last_seen": time.time() - 300,
        "cpu": 0,
        "memory": 0,
        "disk": 0,
        "uptime": "?",
    },
]

DEMO_SNMP_DEVICES = [
    {
        "name": "demo-switch-core",
        "ip": "203.0.113.10",
        "description": "Demo core switch - no real device",
        "uptime": "45d 2h 10m",
        "if_in": "12.3 GB",
        "if_out": "9.8 GB",
        "cpu_load": "23%",
        "memory": "34% (2.1 GB / 6.0 GB)",
        "status": "online",
        "last_seen": time.time(),
        "community": "public",
    },
    {
        "name": "demo-router-edge",
        "ip": "203.0.113.11",
        "description": "Demo edge router - no real device",
        "uptime": "120d 8h 45m",
        "if_in": "890.1 MB",
        "if_out": "1.2 GB",
        "cpu_load": "41%",
        "memory": "52% (512 MB / 1.0 GB)",
        "status": "online",
        "last_seen": time.time(),
        "community": "public",
    },
]


def seed_demo_data(agents: dict, snmp_devices: dict):
    """Populate the shared stores with synthetic demo data."""
    for agent in DEMO_AGENTS:
        agents[agent["hostname"]] = agent
    for device in DEMO_SNMP_DEVICES:
        snmp_devices[device["ip"]] = device
