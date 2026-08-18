"""
ADB client — runs post-pairing operations on the Quest via ADB over WiFi.
  - Confirms ADB connection
  - Checks /persist/srt_push/token (anti-piracy killswitch)
  - Verifies build fingerprint matches our reference firmware
  - Runs Stage 1 strip script
"""

import subprocess
import shutil

REFERENCE_BUILD = "49845030443200410"  # Last Quest 1 firmware (Jul 31 2024)
PERSIST_TOKEN   = "/persist/srt_push/token"

# Stage 1 strip — packages safe to disable without root
# Full list in tools/stage1_strip.sh; this is the programmatic version
STAGE1_DISABLE = [
    "com.oculus.socialplatform", "com.oculus.avatar2", "com.oculus.presence",
    "com.oculus.store", "com.oculus.explore", "com.oculus.fitnesstracker",
    "com.oculus.vrcast", "com.oculus.gamingactivity", "com.oculus.websafety",
    "com.oculus.appsafety", "com.oculus.assistant", "com.oculus.vrusb",
    "com.oculus.guidebook", "com.oculus.environmentdome", "com.oculus.xrstreaming",
    "com.oculus.bugreportservice", "com.oculus.statscollector", "com.oculus.wfd",
    "com.oculus.spatialpersistenceservice", "com.oculus.mrservice",
    "com.oculus.bodyapi", "com.oculus.carmel", "com.oculus.metacam",
    # Phase 2 (run separately — blanks the display, ADB stays alive):
    # "com.oculus.vrhome", "com.oculus.horizon", "com.oculus.guardian",
    # "com.oculus.nuxota", "com.oculus.osupdater",
]


def adb(device_ip: str, *args) -> str:
    if not shutil.which("adb"):
        raise RuntimeError("adb not found — install android-tools-adb")
    result = subprocess.run(
        ["adb", "-s", device_ip, *args],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()


def connect(device_ip: str) -> bool:
    out = adb(device_ip, "connect", device_ip)
    return "connected" in out.lower()


def check_token(device_ip: str) -> bool:
    """Returns True if /persist/srt_push/token EXISTS (anti-piracy armed)."""
    out = adb(device_ip, "shell", f"ls {PERSIST_TOKEN} 2>/dev/null")
    return PERSIST_TOKEN in out


def get_build(device_ip: str) -> str:
    return adb(device_ip, "shell", "getprop ro.build.version.incremental")


def verify_firmware(device_ip: str) -> bool:
    build = get_build(device_ip)
    match = build == REFERENCE_BUILD
    print(f"[ADB] Build: {build} {'✓ matches reference' if match else '! differs from reference'}")
    return match


def run_stage1_strip(device_ip: str):
    print("[ADB] Running Stage 1 strip (Phase 1 — Meta social/commerce layer)...")
    for pkg in STAGE1_DISABLE:
        result = adb(device_ip, "shell", f"pm disable-user --user 0 {pkg}")
        status = "✓" if "disabled" in result else "·"
        print(f"  {status} {pkg}")
    print("[ADB] Stage 1 Phase 1 complete.")
