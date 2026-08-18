"""
STELLA/ALOHA BLE companion protocol constants.
Derived from Quest 1 firmware RE (CompanionServer.apk decompile, 2026-08-18).
Both sides of the protocol are mapped — phone app (STELLA/ALOHA) + device CompanionServer.

UUIDs from QuestEscape research + firmware verification:
"""

# Meta companion BLE service UUIDs (128-bit, custom)
COMPANION_SERVICE_UUID      = "7a442881-5f3e-4aff-a880-4f8d7a9c5c5f"
AUTH_CHAR_UUID              = "094e9319-c6b6-43b8-9e81-790772fc6893"
DATA_CHAR_UUID              = "0cb0a3cc-887a-4442-85ff-5d693c9a6ee0"
WRITE_CHAR_UUID             = "a0eecc11-3212-4956-b87b-d0805d76565f"
NOTIFY_CHAR_UUID            = "b1fe0e73-ba7a-4035-a1b5-ebc960797aca"

# Pairing protocol names (confirmed from CompanionServer.java)
PROTOCOL_STELLA = "STELLA"   # Device pairing + auth layer
PROTOCOL_ALOHA  = "ALOHA"   # Device setup/OOBE/wifi provisioning layer

# Key STELLA message types (device-side handlers confirmed from CompanionServer.java)
MSG_HELLO_REQUEST           = "HelloRequest"
MSG_HELLO_RESPONSE          = "HelloResponse"
MSG_AUTHENTICATE_REQUEST    = "AuthenticateRequest"
MSG_WIFI_CONNECT_REQUEST    = "WifiConnectRequest"        # {ssid, password, auth, hidden, username}
MSG_WIFI_STATUS_RESPONSE    = "WifiStatusResponse"
MSG_DEV_MODE_SET            = "DevModeSet"                # gated on /persist/srt_push/token
MSG_ADB_MODE_REQUEST        = "AdbModeRequest"            # gated on isOtaApplied()
MSG_SYSTEM_UNLOCK_REQUEST   = "SystemUnlockRequest"
MSG_WIPE_DATA_REQUEST       = "WipeDataRequest"
MSG_OTA_CHECK_REQUEST       = "OtaCheckAvailabilityRequest"
MSG_HMD_STATUS_RESPONSE     = "HmdStatusResponse"
MSG_HMD_VERSION_RESPONSE    = "HmdVersionResponse"

# WifiConnectRequest auth types
WIFI_AUTH_OPEN      = 0
WIFI_AUTH_WPA_PSK   = 2
WIFI_AUTH_WPA2_PSK  = 4
WIFI_AUTH_WPA3      = 5

# Dev mode gate (from CompanionService.checkIfDevModeCanBeEnabled)
# If this file is ABSENT on device: dev mode enables with no server check
# If PRESENT: Meta anti-piracy server is consulted
PERSIST_SRT_PUSH_TOKEN = "/persist/srt_push/token"
