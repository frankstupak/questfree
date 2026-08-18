"""
BLE client — finds Quest 1 over Bluetooth, runs the STELLA pairing handshake.
Uses bleak (BlueZ D-Bus on Linux).

Status: STUB — to be implemented after first live pairing capture.
The full BLE characteristic UUID set and protocol flow are documented in protocol.py.
Reference implementation: QuestEscape ble_companion_client.py
"""

import asyncio
from bleak import BleakScanner, BleakClient
from questfree.protocol import (
    COMPANION_SERVICE_UUID, AUTH_CHAR_UUID, DATA_CHAR_UUID,
    WRITE_CHAR_UUID, NOTIFY_CHAR_UUID
)


async def find_quest(timeout: float = 10.0):
    """Scan for a Quest 1 advertising the companion service UUID."""
    print(f"[BLE] Scanning for Quest 1 (timeout={timeout}s)...")
    devices = await BleakScanner.discover(timeout=timeout, service_uuids=[COMPANION_SERVICE_UUID])
    if not devices:
        print("[BLE] No Quest 1 found. Make sure the headset is powered on.")
        return None
    device = devices[0]
    print(f"[BLE] Found: {device.name} ({device.address})")
    return device


async def pair(device_address: str, wifi_ssid: str, wifi_password: str):
    """
    Full pairing flow:
      1. Connect BLE
      2. ECDH handshake (crypto.py)
      3. HelloRequest / HelloResponse
      4. AuthenticateRequest
      5. WifiConnectRequest
      6. DevModeSet (if /persist/srt_push/token absent)
      7. AdbModeRequest

    STUB — implement after first live capture confirms exact frame sequence.
    """
    raise NotImplementedError("BLE pairing — implement after first live capture")
