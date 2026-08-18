# QuestFree

Open-source Linux tool to repurpose discontinued Meta Quest 1 headsets.

Pairs the headset, completes NUX setup, enables developer mode and ADB — **no Meta account required for ongoing device operation**. Works completely offline once paired.

## What it does

1. **BLE pairing** — speaks the STELLA/ALOHA companion protocol directly (no Horizon app needed)
2. **NUX spoof server** — answers Meta's server calls locally so setup completes with WAN dark
3. **WiFi provisioning** — sends your home network credentials to the headset via BLE
4. **Dev mode + ADB** — enables developer mode and confirms ADB over WiFi
5. **Stage 1 strip** — optionally disables Meta social/telemetry services (reversible, no root)

## Requirements

- Linux with BlueZ 5.x (`bluetoothd`)
- Bluetooth adapter (built-in or USB)
- Python 3.10+
- `pip install -r requirements.txt`
- `android-tools-adb` for the ADB strip step

## Usage

```bash
git clone http://100.121.17.5:3000/lumen/questfree.git
cd questfree
pip install -r requirements.txt
# Generate self-signed cert (once):
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=graph.facebook-hardware.com"
# Run:
sudo python3 questfree.py --wifi-ssid "YourNetwork" --wifi-pass "YourPassword"
```

## Status

🔬 **Pre-release / research phase** — BLE client and signed-challenge verification are stubs pending first live pairing capture. The NUX spoof server and ADB strip are complete.

## Architecture

```
questfree/
  protocol.py      — STELLA/ALOHA BLE protocol constants (UUIDs, message types)
  crypto.py        — X25519 ECDH handshake (libsodium-equivalent)
  ble_client.py    — BlueZ BLE scan + GATT pairing flow
  nux_spoof_server.py — Local HTTPS server spoofing Meta endpoints
  dns_spoof.py     — /etc/hosts or dnsmasq DNS redirect
  adb_client.py    — Post-pairing ADB operations
tools/
  stage1_strip.sh  — Shell version of the Stage 1 ADB strip
```

## Background

Based on firmware RE of the final Quest 1 build (49845030443200410, Jul 31 2024).
Protocol mapped from CompanionServer.apk decompile + QuestEscape research.
See `docs/` for the full firmware inventory and protocol documentation.

## License

MIT
