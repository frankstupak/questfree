"""
Local DNS spoofer — redirects Meta server hostnames to localhost
so the NUX spoof server handles all device calls.

Two modes:
  hosts_file: appends to /etc/hosts (requires root, reversible)
  dnsmasq:    writes a dnsmasq drop-in config and reloads (if dnsmasq is running)

Hostnames to redirect (from firmware analysis 2026-08-18):
  graph.facebook-hardware.com  -> loopback (NUX auth endpoints)
  graph.oculus.com             -> loopback (NUX graphql queries)
  graph.facebook.com           -> loopback (NUX account queries)
  portal.fb.com                -> loopback (connectivity probe)
"""

import os
import subprocess
import signal

SPOOF_HOSTS = [
    "graph.facebook-hardware.com",
    "graph.oculus.com",
    "graph.facebook.com",
    "portal.fb.com",
    "meta.graph.meta.com",
]

HOSTS_MARKER = "# questfree-spoof-start"
HOSTS_MARKER_END = "# questfree-spoof-end"


def apply_hosts(target_ip: str = "127.0.0.1"):
    """Add spoof entries to /etc/hosts. Requires root."""
    lines = [HOSTS_MARKER]
    for host in SPOOF_HOSTS:
        lines.append(f"{target_ip}  {host}")
    lines.append(HOSTS_MARKER_END)
    block = "\n".join(lines) + "\n"
    with open("/etc/hosts", "a") as f:
        f.write(block)
    print(f"[DNS] /etc/hosts updated — {len(SPOOF_HOSTS)} hostnames -> {target_ip}")


def remove_hosts():
    """Remove spoof entries from /etc/hosts."""
    with open("/etc/hosts", "r") as f:
        content = f.read()
    if HOSTS_MARKER not in content:
        return
    # Remove the block between markers
    start = content.find(HOSTS_MARKER)
    end = content.find(HOSTS_MARKER_END, start) + len(HOSTS_MARKER_END) + 1
    cleaned = content[:start] + content[end:]
    with open("/etc/hosts", "w") as f:
        f.write(cleaned)
    print("[DNS] /etc/hosts restored")


def apply_dnsmasq(target_ip: str = "127.0.0.1"):
    """Write dnsmasq drop-in for Meta hostnames. Requires dnsmasq."""
    conf_path = "/etc/dnsmasq.d/questfree.conf"
    lines = [f"address=/{h}/{target_ip}" for h in SPOOF_HOSTS]
    with open(conf_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    subprocess.run(["systemctl", "reload", "dnsmasq"], check=True)
    print(f"[DNS] dnsmasq drop-in written -> {conf_path}")


def remove_dnsmasq():
    conf_path = "/etc/dnsmasq.d/questfree.conf"
    if os.path.exists(conf_path):
        os.remove(conf_path)
        subprocess.run(["systemctl", "reload", "dnsmasq"])
        print("[DNS] dnsmasq config removed")
