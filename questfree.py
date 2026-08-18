#!/usr/bin/env python3
"""
QuestFree — repurpose your discontinued Meta Quest 1 on Linux.
No Meta account required for device operation.

Usage:
  sudo python3 questfree.py [--wifi-ssid SSID --wifi-pass PASS] [--no-strip] [--scan-only]

Requirements: bleak cryptography protobuf
  pip install -r requirements.txt
"""

import argparse
import asyncio
import threading
import sys
import os

def check_root():
    if os.geteuid() != 0:
        print("QuestFree requires root for BLE + DNS operations.")
        print("Run with: sudo python3 questfree.py")
        sys.exit(1)


def main():
    check_root()

    parser = argparse.ArgumentParser(
        description="QuestFree — repurpose Meta Quest 1 on Linux"
    )
    parser.add_argument("--wifi-ssid", help="Home WiFi SSID to provision to the Quest")
    parser.add_argument("--wifi-pass", help="Home WiFi password")
    parser.add_argument("--no-strip", action="store_true", help="Skip Stage 1 ADB strip")
    parser.add_argument("--scan-only", action="store_true", help="Just scan for Quest devices")
    parser.add_argument("--spoof-port", type=int, default=8443, help="Spoof server port")
    parser.add_argument("--dns-mode", choices=["hosts","dnsmasq"], default="hosts")
    args = parser.parse_args()

    print("QuestFree v0.1.0-dev")
    print("Quest 1 repurposing tool — github.com/frankstupak/questfree")
    print()

    # Step 1: Start NUX spoof server
    from questfree.nux_spoof_server import run as run_spoof
    spoof_thread = threading.Thread(
        target=run_spoof,
        kwargs={"port": args.spoof_port},
        daemon=True
    )
    spoof_thread.start()
    print(f"[*] NUX spoof server running on :{args.spoof_port}")

    # Step 2: DNS redirect
    from questfree.dns_spoof import apply_hosts, remove_hosts, apply_dnsmasq, remove_dnsmasq
    try:
        if args.dns_mode == "dnsmasq":
            apply_dnsmasq()
        else:
            apply_hosts()

        # Step 3: BLE scan + pairing
        from questfree.ble_client import find_quest, pair
        device = asyncio.run(find_quest())

        if args.scan_only or not device:
            return

        if not args.wifi_ssid:
            args.wifi_ssid = input("Home WiFi SSID: ")
            args.wifi_pass = input("Home WiFi password: ")

        asyncio.run(pair(device.address, args.wifi_ssid, args.wifi_pass))

        # Step 4: ADB operations post-pairing
        if not args.no_strip:
            from questfree.adb_client import connect, verify_firmware, check_token, run_stage1_strip
            quest_ip = input("Quest IP address (from WiFi): ").strip()
            if connect(f"{quest_ip}:5555"):
                verify_firmware(f"{quest_ip}:5555")
                armed = check_token(f"{quest_ip}:5555")
                print(f"[*] /persist/srt_push/token: {'PRESENT (server check needed)' if armed else 'ABSENT (dev mode enables freely)'}")
                run_stage1_strip(f"{quest_ip}:5555")

    finally:
        if args.dns_mode == "dnsmasq":
            remove_dnsmasq()
        else:
            remove_hosts()
        print("[*] DNS restored. Done.")


if __name__ == "__main__":
    main()
