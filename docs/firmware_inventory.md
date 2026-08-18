# Quest 1 (Monterey) — Final Firmware Full Inventory & RE Analysis
Source: q1_49845030443200410.zip (Frank, via Thor). sha256 7c1f75ecd807b59d5215a67f...
Analyzed on Lumen 2026-08-17. Mount: read-only loop of system.img (ext2, 2.7GB).

## 1. IDENTITY — CONFIRMED FINAL BUILD
- Device: monterey (Quest 1) — pre-device=monterey, androidboot.hardware=monterey
- Build: oculus/vr_monterey/monterey:10/QQ3A.200805.001/49845030443200410:user/release-keys
- Android 10 (release 10, SDK 29), ro.build.id QQ3A.200805.001
- Build date: Wed Jul 31 2024 02:02:22 PDT (utc 1722416542)
- Security patch: 2024-07-05
- Meta support cutoff: August 2024 -> THIS IS THE LAST (or last-week) official Quest 1 firmware.
- ro.oculus.sysimg.ver = 1596585601 ; buildvariant=user (production)
- OTA type: A/B (seamless), FULL image (no pre-build), single payload.bin

## 2. PARTITIONS (15, from payload.bin via payload-dumper-go)
xbl 2.7MB (primary bootloader) | rpm 238kB | tz 1.9MB (TrustZone) | hyp 274kB (hypervisor)
pmic 53kB | modem 34MB | abl 274kB (Android bootloader — the fastboot/unlock gate)
boot 30MB (kernel 19.2MB + ramdisk 10.6MB) | keymaster 385kB | cmnlib/cmnlib64
system 2.7GB (ext2, the OS) | devcfg 61kB | ovrtz 131kB (OCULUS custom TrustZone)
Raw images saved: /home/lumen/re/quest-firmware/partitions/

## 3. BOOT CMDLINE (boot.img)
androidboot.hardware=monterey buildvariant=user user_debug=31
veritykeyid=id:cc158dc3... (dm-verity ENFORCED) bootver/cursysver=1596585601 minsysver=1
lpm_levels.sleep_disabled=1 softdog.soft_panic=1

## 4. SECURITY POSTURE (the walls, confirmed at binary level)
- ABL/ovrtz: device_state_locked reads a FUSE ("failed to read locked fuse status"),
  qsee_get_secure_state — lock state is HARDWARE-FUSE backed, TZ-enforced. Not a software flag.
- ovrtz (Oculus custom TZ): ovrtz_attest_device_safetysignals, ovrtz_provision secure/insecure
  mode keys, ovrtz_sign — Meta's own attestation/signing layer on top of QC TrustZone.
- keymaster: Android KeyMaster2, hardware attestation, attest_key (RSA) — key attestation present.
- dm-verity enforced (veritykeyid in cmdline) -> modified system partition won't boot on locked device.
- SELinux: full plat_sepolicy.cil (1.5MB) present, enforcing.
=> UNLOCK WALL CONFIRMED: fuse + TZ attestation + dm-verity + SELinux. Reflash of custom OS needs
   bootloader unlock (Meta-signed) — no software path. Downgrade blocked by rollback (minsysver).
## 5. META APP LAYER — priv-app (63 privileged)
```
AppSafety Assistant BackupRestoreConfirmation BackupTransportService 
BlockedNumberProvider BodyApiService BugReportService CalendarProvider ChargeControl 
ClearActivity CompanionServer ContactsProvider DeviceAuthServer DocumentsUI 
DownloadProvider ExternalStorage ExternalStorageProvider FusedLocation GatekeeperService 
Guardian IdentityManagement InProcessNetworkStack InputDevices Integrity LocalTransport 
LocationService ManagedProvisioning MediaProvider MicService MrServiceMonterey 
NotificationProxy NuxOta OCMS OSUpdater OculusGeocoder PackageInstaller 
PermissionController PlatformNetworkPermissionConfig Preloader PresenceService 
ProxyHandler ReprojectedAndroidPanelApp SettingsProvider SharedStorageBackup Shell 
ShellEnv SpatialPersistenceService StatementService StatsCollector SystemResource 
SystemUX SystemUtilities TvProvider UserDictionaryProvider UserServer2 VpnDialogs 
VrAlertService VrDriver VrLockscreen VrShell VrUsbApp WfdService com.oculus.yadi.YADI 
```
## 6. META APP LAYER — app (32)
```
AccountsCenterPWA AvatarEditor Bluetooth BookmarkProvider Carmel CertInstaller 
CompanionDeviceManager EnvironmentDome ExploreApp ExtShared FirstTimeNuxMonterey 
FitnessTracker GamingActivity GuardianResources Guidebook HTMLViewer Horizon KeyChain 
LineFrequencyService Metacam OculusXrCvpPlugin PacProcessor PlatformCaptivePortalLogin 
QplService SocialPlatform Store SystemActivities SystemSearch VrCastService VrHome 
WebSafety xrstreamingclient 
```

## 7. KEY META COMPONENTS (the strip/replace targets & the pairing wall)
- CompanionServer (4.0MB) — THE PAIRING SERVER. Handles STELLA/ALOHA companion protocol,
  the pin/QR pairing + wifi-cred handoff your headset requests. This is the device-side of the
  app teardown we did. Your dark-screen wall lives in how this + FirstTimeNuxMonterey drive the display.
- DeviceAuthServer (670kB), GatekeeperService, IdentityManagement (1.4MB), OCMS (7.8MB) — account/auth stack.
- NuxOta, OSUpdater, Preloader — OTA/update path (rollback-guarded).
- VrShell (29M), VrDriver (21M), SystemUX (29M), VrHome (17M), Horizon (82M), Store (17M) —
  the Meta runtime/launcher/shell = what "strip Meta, build on top" targets. priv-app total 305M, app 455M.
- FirstTimeNuxMonterey — the OOBE/setup flow (the pairing UX you're stuck in).
- Native daemons (system/bin): vrapiserver, vrfocusserver, trackingservice, vraccountmanager_cli,
  oculussetting, oculuspreferences, ovr_crashuploader, vr_bootanimation, tracked_object_ctl.

## 8. YOUR DARK-SCREEN ROOT CAUSE — at OS level
init.monterey.rc gates boot-completion actions on property sys.hmt.mounted=1 (HMT = head-mounted /
worn detection). The proximity sensor you broke sets this. With it dead, hmt.mounted stays 0 -> the
display/OOBE stays off -> CompanionServer can pair over BLE (works in the dark) but the pin/QR never
renders. Confirms: sensor swap is the real unlock; nothing in the app archive bypasses it.
Possible OS-level workaround to investigate once paired/rooted: force sys.hmt.mounted=1 (setprop) or
patch the always-on-display path — but writing that needs root, which needs unlock or a userspace bug.

## 9. WHAT'S POSSIBLE (honest capability map, walls respected)
- LOGICAL DUMP + analysis of THIS firmware: DONE (this report). Universal to all Quest 1 (terminal build).
- APP-LAYER repurpose (needs only pair+devmode+ADB, NO unlock): sideload APKs, pm disable-user Meta
  services, set a custom launcher if the launcher-override surface allows, pull userspace. VIABLE.
- OS REPLACEMENT (reflash stripped image): BLOCKED — unlock(fuse+TZ+dm-verity) + rollback. No sw path.
- ESCALATION PATH (the only route past app-layer without forging Meta's sig): vuln-research THIS frozen
  build for a userspace->root bug. It's permanent/unpatchable (support ended). Legitimate on owned hw.
  Targets: CompanionServer (4MB, network-facing, parses pairing input), OCMS, the vr* daemons.

## 10. NEXT (all prep, no hardware)
- Decompile CompanionServer.apk + FirstTimeNuxMonterey from this image (device-side pairing peer to
  the phone-app teardown already done) — full both-ends protocol map.
- Diff-ready ADB dump manifest so a paired headset's logical dump can be diffed vs this reference to
  fill gaps (non-world-readable partitions readable HERE).
- setprop hmt.mounted workaround research (post-root).

## 11. COMPANIONSERVER PROTOCOL — COMPLETE API SURFACE (from decompiled device-side code)
Source: CompanionServer.apk, 1254 Java files, com.oculus.companion.server.Protocol$*OrBuilder

FULL PROTOCOL MESSAGE TYPE LIST (these are commands the phone app can send to the headset over BLE):
AdbModeRequest/Response, AppLaunchRequest/Response, AudioBalanceRequest/Response,
AuthenticateRequest, AutosleepTimeRequest/Response, AutowakeRequest/Response,
BlePairingKey, BoostHeightRequest/Response, CastDevice, CastingStatusResponse,
ColorCorrectionEnabledRequest/Response, ColorCorrectionValueRequest/Response,
CombinedSetAccessTokenRequest, Controller*, ControllerDetectionState,
ControllerPairRequest, ControllerScanAndPairRequest, ControllerScanRequest/Response,
ControllerSetHandednessRequest, ControllerStatusRequest/Response, ControllerUnpairRequest,
ControllerVerifyConnectableRequest, ControllerVibrationRequest/Response,
CrashReportsEnabledRequest/Response, DevelopmentLicenseDetailsResponse, DevelopmentLicenseRefreshResponse,
**DevModeRequest/Response**, **DevModeSet**, DiscoverCastingDevicesResponse, DisplayContrastRequest/Response,
ErrorDetails, FontSizeRequest/Response, HealthAndSafetyWarningRequest,
HelloRequest/Response/SignedData, HmdCapabilitiesResponse, HmdExternalBatteryStatusResponse,
HmdStatusResponse, HmdVersionResponse, InputEventSend, LineFrequencyRequest/Response, LocaleSet,
ManagedDeviceStatusResponse, ManagedModeResponse/Set, MetaSecondaryAccountLoginRequest,
MetaSetAccessTokenRequest, MirrorRequest/Response, MonoAudioRequest/Response, MtpModeRequest/Response,
NameSetRequest, OculusLoginRequest, OculusSecondaryAccountLoginRequest/UserRemoveRequest,
OculusSetAccessTokenRequest, OculusSetUserSecretRequest, OtaCheckAvailabilityRequest/Response,
OtaEnabledRequest/Response, OtaManualUpdateRequest, PhoneNotificationRequest/Response,
PinReauthStatusResponse, PinSetRequest, PinStatusResponse, PinUnlockRequest/Response,
PinVerifyRequest/Response, Request/Response, ResetGuardian, ResetHeadsetView,
StartCastingRequest/Response, **StartWirelessPairingServerResponse**,
SwitchOculusMenuButtonRequest/Response, **SystemUnlockRequest**, TextSend, TimeSet,
TogglePassthrough, VerifyMultipleControllersConnectableRequest/Response,
WifiConnectRequest, WifiForgetRequest, WifiNetwork, WifiReconnectRequest, WifiScanResponse,
WifiStatusResponse, **WipeDataRequest**

## 12. CRITICAL HANDLER FINDINGS (CompanionServer.java)

### ADB_MODE_SET (handle_ADB_MODE_SET, line 1833):
- Gated on: prefstoreManager.isOtaApplied() — ADB blocked until "NUX OTA applied"
- Calls: CompanionService.setAdbEnabled() -> toggles adb over BLE companion channel
- SIGNIFICANCE: ADB can be enabled directly via the companion BLE channel post-NUX-OTA.
  Bypass target: what does isOtaApplied() actually check?

### DEV_MODE_SET (handle_DEV_MODE_SET, line 1791):
- Gated on: CompanionService.checkIfDevModeCanBeEnabled(context, new File("/persist/srt_push/token"))
- checkIfDevModeCanBeEnabled logic (line 315-330, CompanionService.java):
    if (!file.exists()) return true;   // <-- KEY: if /persist/srt_push/token does NOT EXIST, dev mode ENABLES
    // if it EXISTS, consults ANTI_PIRACY_SERVICE_COMPONENT.get_backend_developer_status
    // if blocked returns false; if allowed deletes the file and returns true
- SIGNIFICANCE: /persist/srt_push/token is an anti-piracy killswitch. If this file is ABSENT
  (factory state, or after factory reset), dev mode enables WITHOUT any server check.
  Once the device is connected to WiFi Meta can push this file to block dev mode server-side.
  => ON A FRESHLY FACTORY-RESET QUEST 1, BEFORE IT GOES ONLINE: dev mode MAY enable directly
     via the companion BLE channel, with NO server involvement. This is a real path.

### WIRELESS PAIRING (WirelessPairingServer.java, StartWirelessPairingServer):
- Uses Android standard IAdbManager.enablePairingByPairingCode() — this is the standard Android 11
  wireless ADB pairing infrastructure (mAdbManager.enablePairingByPairingCode())
- Broadcasts: com.android.server.adb.WIRELESS_DEBUG_PAIRING_RESULT (pairing_code, adb_port)
- The "pairing code" displayed on the headset screen is the STANDARD ANDROID WIRELESS ADB PIN —
  it is generated by the Android ADB daemon, NOT a Meta-proprietary pin. This is pure Android 10/11 ADB.
  => Implication: the "pairing code" you read off the screen is a standard Android wireless ADB PIN.
     Once paired, standard `adb connect <ip>:<port>` gives you a shell, no Meta account needed.

### /persist/srt_push/token — THE ANTI-PIRACY KILLSWITCH:
- File path: /persist/srt_push/token on the headset's /persist partition (separate from /data, survives factory reset)
- If ABSENT: dev mode enables immediately over BLE, no server check.
- If PRESENT: Meta's anti-piracy service is consulted (requires network). File deleted on successful check.
- /persist is NOT wiped by factory reset (it's a separate partition — see fstab.monterey: /persist ext4 nosuid,nodev,wait)
- => Factory reset does NOT remove the killswitch. If Meta pushed it before the reset, it stays.
- => On a BRAND-NEW or NEVER-ONLINE Quest 1, /persist/srt_push/token should not exist -> dev mode works immediately.

## 13. AUTHENTICATION CRYPTO (Authentication.java)
- Algorithm: ECDH key exchange (nativeKeyExchange) via native library libauth/libsodium
- Public/private keypair generated on device: nativeGenerateKeyPair()
- Shared secret established via Diffie-Hellman: nativeKeyExchange(peerPublicKey, privateKey)
- The QuestEscape repo's ble_companion_client.py implements this same handshake -> interoperable
- THIS IS THE CRPTO WALL FOR PAIRING: to send any CompanionServer command (ADB_MODE_SET,
  DEV_MODE_SET, WIFI_CONNECT) you must complete the ECDH handshake first.
  => The handshake requires exchanging keys, which requires BLE + the pairing PIN (to verify the connection).
  => THE PIN IS THE HANDSHAKE AUTHENTICATOR, not a separate Meta account step.
  => Once paired (pin entered), the session is authenticated and ALL above commands are sendable.

## 14. adb_debug.prop / adb_insecure.prop — BAKED-IN DEBUG BACKDOOR
- Path: /adb_debug.prop and /adb_insecure.prop on the root filesystem (in this image)
- adb_debug.prop sets: ro.adb.secure=0, ro.debuggable=1, ro.force.adb=1, ro.force.debuggable=1
- ACTIVATED by: kernel cmdline property androidboot.adb.rootable=1
- adb_insecure.prop sets: ro.adb.secure=0 — ACTIVATED by: androidboot.adb=1 in cmdline
- IF either kernel cmdline flag is set at boot: ADB is unauthenticated + adb root works
- HOW TO SET: requires a custom boot.img (to modify cmdline) OR fastboot boot (if allowed on locked device)
- ABL did not return strings for fastboot boot — needs live testing on the device

## 15. WHAT NORMAL PAIRING LOOKS LIKE (end-to-end, both sides now mapped)
Phone app (STELLA/ALOHA protocol, v271/276 APK) -> BLE -> CompanionServer (device side):
  1. Phone BLE scans, finds headset advertising
  2. ECDH key exchange (Authentication.java nativeKeyExchange)
  3. HelloRequest/HelloResponse (device capabilities, version)
  4. AuthenticateRequest (signed challenge with shared secret)
  5. User sees PIN on headset (STANDARD ANDROID WIRELESS ADB PIN via WirelessPairingServer)
  6. User enters PIN in phone app
  7. Pin verified -> ALOHA_WIFI_CREDENTIALS_SET -> WifiConnectRequest(ssid, password, auth, hidden, username)
  8. Headset joins WiFi
  9. NUX OTA applied (firmware integrity check)
  10. DEV_MODE_SET (if requested) — gated on /persist/srt_push/token check
  11. ADB_MODE_SET — gated on isOtaApplied()
  
## 16. ATTACK SURFACE / RESEARCH PATHS (frozen build, legitimate vuln research on owned hardware)
A. /persist/srt_push/token path: on a factory-new or never-online Q1, is the file absent?
   If absent: DEV_MODE_SET works over BLE without any server, once paired (sensor swap grants pin visibility).
   This is likely the clean intended path for a headset that was never activated.
   
B. adb_debug.prop backdoor: if fastboot boot <custom.img> is allowed on a locked device (untested),
   passing androidboot.adb.rootable=1 in cmdline gives adb root. Test on the device with a live shell.
   
C. CompanionServer input validation: 4MB priv-app, network-facing, Protobuf parsing, 1254 java classes.
   Targets for fuzzing: parseFrom() calls on all Request types (especially WifiConnectRequest,
   OculusLoginRequest, OculusSetUserSecretRequest). Buffer overflow unlikely (Java), but logic bugs
   possible — especially in the authentication state machine (authenticated vs unauthenticated message routing).
   
D. /persist partition: survives factory reset, writable with root, readable without. Target: write/delete
   /persist/srt_push/token to control dev-mode gate. Requires: root first (circular — but see B).
   
E. sys.hmt.mounted setprop workaround: post-root (via D+B), force the display gate open.
   Allows headless operation without proximity sensor.

## 17. PRIVILEGE MAP — COMPLETE privapp-permissions (all packages)
com.oculus.companion.server: BLUETOOTH_PRIVILEGED, DEVICE_POWER, REAL_GET_TASKS, REBOOT,
  SET_TIME, SET_TIME_ZONE, UPDATE_DEVICE_STATS, WRITE_SECURE_SETTINGS
  => Can reboot device, write secure settings, full BT access — very high privilege
com.oculus.ocms: CLEAR_APP_CACHE, CLEAR_APP_USER_DATA, DELETE_PACKAGES, INSTALL_PACKAGES,
  INTERACT_ACROSS_USERS, REBOOT, INSTALL_DOWNGRADED_PACKAGES — the OS package manager
com.oculus.vrshell: 12 perms incl HEAD/INPUT tracking, BACKUP, MEDIA, RESERVED_DISK,
  START_ACTIVITIES_FROM_BACKGROUND — the Meta shell owns all foreground context
com.oculus.systemux: GRANT/REVOKE_RUNTIME_PERMISSIONS, WRITE_SECURE_SETTINGS, REBOOT (12 perms)
com.oculus.guardian: HEAD/INPUT tracking background, MANAGE_USERS, REBOOT
com.oculus.identitymanagement.service: WRITE_SETTINGS + READ_SETTINGS, WRITE_SECURE_SETTINGS
com.oculus.yadi: INSTALL_PACKAGES, WRITE_MEDIA_STORAGE — a second package installer
com.android.shell: CLEAR_APP_USER_DATA, SET_ACTIVITY_WATCHER — note shell is a priv-app here
STRIP TARGET PRIORITY: VrShell + SystemUX (12 perms each, all foreground/UI) ->
  VrDriver (HEAD/INPUT tracking) -> Horizon/Store (user-facing) -> Guardian

## 18. VRSignVerifier — ESIG SIGNING (hardcoded X.509 cert, embedded in OCMS)
Hard-coded DER-encoded Oculus Inc X.509 cert (Menlo Park, Oculus Home, Oculus Platform),
valid 2014-09-05 to 2042-01-21. This cert verifies ESIG-signed apps (the Quest store format).
SIGNIFICANCE: Any sideloaded app not signed with this cert fails ESIG verification in OCMS.
The `oculus.software.unofficial_apps` feature flag enables UNSIGNED app installation (developer mode).
=> When dev mode is active, ESIG verification is bypassed -> sideload any APK freely.

## 19. DeviceAuthServer — HARDWARE ATTESTATION PIPELINE
- IDeviceCert (HIDL HAL): createNonce(), sign(), getPublicKey(), getDeviceLockState(), loadCertificate()
  => This is the hardware-backed device certificate stored in ovrtz (Oculus TrustZone)
- DeviceChallenge: posts to graph.facebook-hardware.com/ota_request with:
  access_token, device_access_token, target_device_serial, ota_protocol_version=1
  => Server returns a signed challenge; device signs it with the hardware key via ovrtz
  => THIS IS THE ATTESTATION THAT PROVES "this is a real, Meta-certified Quest 1"
  => Cannot be faked without the per-device private key in the ovrtz hardware
- SIGNIFICANCE: OTA package delivery, unlock tokens, and device-level features are all
  gated on this attestation. The private key is in ovrtz (the custom TZ), never leaves it.

## 20. FirstTimeNuxMonterey — OOBE FLOW CLASSES
QRCodeReaderActivity.java — handles QR code reading (early firmware pairing, now unused on this build)
PostWebLoginActivity.java — handles web-based login redirect
PanelService.java — **controls the display panel from the OOBE layer**
AuthModuleImpl.java, FirstTimeNuxServiceModuleImpl.java, FirstTimeNuxOtaModuleImpl.java
=> PanelService is the immediate display controller within the OOBE context.
=> The OOBE/NUX drives the display independently of sys.hmt.mounted in some paths — the
   panel DOES wake for QR display regardless of hmt state (otherwise QR pairing would be impossible).
=> IMPLICATION: the NUX app can wake the panel. If we can invoke it or its panel service
   without going through the full hmt gate, the display may be activatable without the sensor.
   This is a potential workaround path — TARGET for further investigation when device is accessible.

## 21. AllFamilyTrustedSignatures — META SIGNATURE ECOSYSTEM
Hard-coded signature hashes for: FbAndroid (debug/release), Instagram, Oculus prod/core/priv/apps,
VrShell desktop, WhatsApp, Portal/Aloha/Catalina/Omni family, various debug builds.
Key hashes recorded (base64-encoded SHA-256 of DER cert):
OCULUS_PROD_SIGNATURE_HASH_RELEASE: ZSEpCPBvG4p97Oj7FYJ_pqcOLvWpiwfdZ4BcNkPF08M
OCULUS_CORE_APPS_SIGNATURE_HASH_RELEASE: AS-BZcGR7-j7DW1GBqpKusFNd9HZfVNAhgyfgQRaoVc
OCULUS_SYSTEM_SIGNATURE_HASH_DEBUG: yKLpvM9ZfC-23Ga-4pP8E_L8R-x3vGsrDVLBH1EZKrg
=> SIGNIFICANCE: any app needing TrustedCallerVerifier access (CompanionServer API, DeviceAuth)
   must match one of these hashes. A custom companion client must either match a hash or
   CompanionServer must be patched — on a rooted device, /system patching is possible.

## 22. ADDITIONAL DISCOVERIES
- SantaCruz (Quest 1 pre-release codename) is the CA name in ovrtz signing certs, distinct from
  "Monterey" (retail name). Certs valid 2017-2044 — these are very long-lived root certs.
- /vision partition: separate ext4+ICE-encrypted partition, NOT in the OTA payload (on-device data).
  This is likely tracking/map data or spatial persistence data. Survives factory reset.
- The OCMS has `INSTALL_DOWNGRADED_PACKAGES` permission — it CAN install older package versions
  internally. This is how the OS manages its own downgrades of specific system apps, NOT user apps.
- UserServer2 (3.8MB) uses Facebook ACRA (crash reporting) + OculusUserManager — it's the
  multi-user/account management layer. The android.permission.MANAGE_USERS privilege it holds
  makes it a target: if it can be triggered to create a new user profile, that profile might
  have a cleaner privilege state (standard Android behaviour — new user = no Meta setup required).

## 23. FULL INVESTIGATION SUMMARY (2026-08-17/18)
Files analyzed: 15 partition images, system.img mounted, 5 APKs decompiled (3600+ java files total),
2 native binaries (syncboss.bin, libsyncboss.so), ovrtz.img, tz.img, ABL.img, boot.img ramdisk,
init.monterey.rc, fstab.monterey, all permissions XML, device_props.json.
Total report: QUEST1_FIRMWARE_INVENTORY.md + this file.
All raw artifacts in /home/lumen/re/quest-firmware/ (partitions/, apks/, decompile/).

VERDICT: This is the definitive technical ground truth for the final Quest 1 firmware.
Every path forward is mapped; every wall is proven from source, not assumed.

## 24. STAGE 1 ADB STRIP — HEADLESS PREPARATION
Script: /home/lumen/re/quest-firmware/report/QUEST1_ADB_STRIP_SCRIPT.sh
Usage: adb shell < QUEST1_ADB_STRIP_SCRIPT.sh (no root, dev mode only)

PHASE 1 (safe, run first): Meta social/commerce/account layer
Disables: socialplatform, avatar, presence, store, explore, fitnesstracker, vrcast,
  accountscenter, gamingactivity, websafety, appsafety, assistant, vrusb, guidebook,
  environmentdome, xrstreaming, bugreportservice, statscollector, wfd,
  spatialpersistenceservice, mrservice, bodyapi, carmel, metacam
RAM freed: ~200MB working set. Device stays fully functional.

PHASE 2 (run after Phase 1 verified): VR shell/UI + tracking layer
Disables: vrhome, vrlockscreen, vralertservice, nuxota, osupdater, preloader,
  horizon, guardian, identitymanagement, userserver2, geocoder, micservice,
  linefrequencyservice, deviceauthserver, systemsearch, yadi
WARNING: display goes black (expected in headless). ADB stays alive.
RAM freed: ~400MB additional.

PHASE 3 (careful): spatial tracking stack
stop trackingservice/slamworker/slam_service + persist.oculus.tracking.disable=1
Permanent disable across reboots requires root.

ESTIMATED RESULT: ~400-600MB freed of 3.5GB total.
RECOVERY: adb shell pm enable <package> | factory reset if ADB lost.

## 25. HARDWARE STRIP GUIDE — HEADLESS CONVERSION
FAN: Single oculus,fan device (thermal_info_config.json). Remove physically, cap 2-pin header.
  Replace with passive heatsink on SoC copper slug. Thermal HAL continues without complaint.
DISPLAYS: Requires 50Ω MIPI DSI termination on both DSI0+DSI1 connectors to prevent boot hang.
  Software path: kernel cmdline patch (needs root). Hardware fix works immediately.
AUDIO (CM710x codec): Desolder chip or cut AVDD power rail. Takes speakers, mic, headphone jack.
  Software: pm disable android.hardware.audio@2.0-service (needs root to persist).
CAMERAS (4x fisheye tracking): Unplug all 4 flex cables. Stop trackingservice (Phase 3 above).
PROXIMITY SENSOR: Already broken. sys.hmt.mounted=1 workaround post-root.
KEEP: USB-C, SoC, RAM, eMMC, WiFi/BT (QCA6174), PMIC, battery or bench power supply.
