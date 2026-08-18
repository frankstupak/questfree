#!/system/bin/sh
# Quest 1 — Stage 1 ADB Strip Script
# Headless inference node preparation
# Requires: ADB shell with dev mode enabled (no root needed)
# Reversible: re-enable with `pm enable <package>`
# Run via: adb shell < QUEST1_ADB_STRIP_SCRIPT.sh
# Generated from live firmware analysis 2026-08-18
#
# ============================================================
# SAFETY RULES (READ BEFORE RUNNING)
# ============================================================
# 1. Run PHASE 1 only first. Reboot. Confirm ADB still works.
# 2. Run PHASE 2. Reboot. Confirm.
# 3. Do NOT disable SettingsProvider, PackageInstaller, or Shell
#    unless you are certain you have another access path (root).
# 4. If the device goes offline after a disable, recovery:
#    adb shell pm enable <last_disabled_package>
#    If ADB is lost entirely: factory reset is the recovery.
# 5. Verify after each phase: adb shell pm list packages -d
#
# ============================================================
# PHASE 1: Meta social/account/commerce layer
# Safe to run first — no core OS services affected
# Estimated RAM savings: ~200MB working set
# ============================================================

echo "[PHASE 1] Disabling Meta social/commerce/account layer..."

# Horizon OS social features (Meta Horizon Home, parties)
pm disable-user --user 0 com.oculus.socialplatform 2>/dev/null || echo "SocialPlatform: not found"
# Meta avatar editor — not needed headless
pm disable-user --user 0 com.oculus.avatar2 2>/dev/null || echo "Avatar: not found"
# Presence/social status service
pm disable-user --user 0 com.oculus.presence 2>/dev/null || echo "PresenceService: not found"
# Horizon web store — not needed
pm disable-user --user 0 com.oculus.store 2>/dev/null || echo "Store: not found"
# Explore/discovery app
pm disable-user --user 0 com.oculus.explore 2>/dev/null || echo "ExploreApp: not found"
# Fitness tracker
pm disable-user --user 0 com.oculus.fitnesstracker 2>/dev/null || echo "FitnessTracker: not found"
# VR casting service (Chromecast-style)
pm disable-user --user 0 com.oculus.vrcast 2>/dev/null || echo "VrCastService: not found"
# Accounts center (Meta account linking PWA)
pm disable-user --user 0 com.oculus.accountscenter 2>/dev/null || echo "AccountsCenterPWA: not found"
# Gaming activity feed
pm disable-user --user 0 com.oculus.gamingactivity 2>/dev/null || echo "GamingActivity: not found"
# Web safety/parental controls
pm disable-user --user 0 com.oculus.websafety 2>/dev/null || echo "WebSafety: not found"
# App safety (content rating enforcement)
pm disable-user --user 0 com.oculus.appsafety 2>/dev/null || echo "AppSafety: not found"
# Voice assistant (Oculus/Meta assistant)
pm disable-user --user 0 com.oculus.assistant 2>/dev/null || echo "Assistant: not found"
# MTP file transfer mode (not needed headless — ADB covers this)
pm disable-user --user 0 com.oculus.vrusb 2>/dev/null || echo "VrUsbApp: not found"
# Guidebook (in-VR help system)
pm disable-user --user 0 com.oculus.guidebook 2>/dev/null || echo "Guidebook: not found"
# Environment/skybox renderer
pm disable-user --user 0 com.oculus.environmentdome 2>/dev/null || echo "EnvironmentDome: not found"
# XR streaming client (PC VR link)
pm disable-user --user 0 com.oculus.xrstreaming 2>/dev/null || echo "xrstreamingclient: not found"
# Bug report service
pm disable-user --user 0 com.oculus.bugreportservice 2>/dev/null || echo "BugReportService: not found"
# Stats/telemetry collector
pm disable-user --user 0 com.oculus.statscollector 2>/dev/null || echo "StatsCollector: not found"
# WFD (WiFi Display/Miracast) — not needed
pm disable-user --user 0 com.oculus.wfd 2>/dev/null || echo "WfdService: not found"
# Spatial persistence (map data for shared spaces)
pm disable-user --user 0 com.oculus.spatialpersistenceservice 2>/dev/null || echo "SpatialPersistenceService: not found"
# MR service (mixed reality, passthrough)
pm disable-user --user 0 com.oculus.mrservice 2>/dev/null || echo "MrServiceMonterey: not found"
# Body API (body tracking — Quest 1 doesn't have it but the service still loads)
pm disable-user --user 0 com.oculus.bodyapi 2>/dev/null || echo "BodyApiService: not found"
# Carmel (web browser engine)
pm disable-user --user 0 com.oculus.carmel 2>/dev/null || echo "Carmel: not found"
# Metacam (passthrough camera app) — Quest 1 has no color camera
pm disable-user --user 0 com.oculus.metacam 2>/dev/null || echo "Metacam: not found"
# Social platform
pm disable-user --user 0 com.oculus.social 2>/dev/null || echo "SocialPlatform alt: not found"

echo "[PHASE 1] Complete. Reboot and verify ADB before Phase 2."
echo "Verify: adb shell pm list packages -d | grep oculus"
echo ""

# ============================================================
# PHASE 2: VR shell/UI layer + tracking
# Run AFTER Phase 1 verified safe
# Estimated additional savings: ~400MB working set
# WARNING: Phase 2 will make the headset display a black screen
# or minimal UI. This is expected. ADB access is preserved.
# ============================================================

echo "[PHASE 2] Disabling VR shell and tracking layer..."

# VrHome (the VR home environment — the 3D "living room")
# WARNING: without VrHome, the headset displays nothing on the panels
# This is fine in headless mode — ADB still works
pm disable-user --user 0 com.oculus.vrhome 2>/dev/null || echo "VrHome: not found"
# VrLockscreen (the PIN lock screen overlay)
pm disable-user --user 0 com.oculus.vrlockscreen 2>/dev/null || echo "VrLockscreen: not found"
# VrAlertService (popups, system dialogs in VR space)
pm disable-user --user 0 com.oculus.vralertservice 2>/dev/null || echo "VrAlertService: not found"
# NuxOta (the OTA/update NUX flow — safe to disable post-setup)
pm disable-user --user 0 com.oculus.nuxota 2>/dev/null || echo "NuxOta: not found"
# OSUpdater (OTA update client — disable to prevent Meta from pushing updates)
pm disable-user --user 0 com.oculus.osupdater 2>/dev/null || echo "OSUpdater: not found"
# OCMS (app manager/updater) — WARNING: disabling breaks app installation
# Only disable if you will NEVER install new apps
# pm disable-user --user 0 com.oculus.ocms 2>/dev/null || echo "OCMS: skipped (keeps app install)"
# Preloader (app preload service)
pm disable-user --user 0 com.oculus.preloader 2>/dev/null || echo "Preloader: not found"
# Horizon app (the main Meta companion integration)
pm disable-user --user 0 com.oculus.horizon 2>/dev/null || echo "Horizon: not found"
# Guardian (boundary system — not needed headless)
pm disable-user --user 0 com.oculus.guardian 2>/dev/null || echo "Guardian: not found"
# IdentityManagement (Meta account identity service — WARNING: may affect dev mode)
# Only disable after confirming dev mode / ADB survives
pm disable-user --user 0 com.oculus.identitymanagement 2>/dev/null || echo "IdentityManagement: not found"
# UserServer2 (multi-user/account manager)
pm disable-user --user 0 com.oculus.userserver2 2>/dev/null || echo "UserServer2: not found"
# OculusGeocoder (location — not needed)
pm disable-user --user 0 com.oculus.geocoder 2>/dev/null || echo "OculusGeocoder: not found"
# MicService (microphone routing service — not needed headless)
pm disable-user --user 0 com.oculus.micservice 2>/dev/null || echo "MicService: not found"
# ChargeControl (battery charge limiting — keep if using battery, disable if bench power)
# pm disable-user --user 0 com.oculus.chargecontrol 2>/dev/null
# LineFrequencyService (60/50hz display flicker detection — irrelevant headless)
pm disable-user --user 0 com.oculus.linefrequencyservice 2>/dev/null || echo "LineFrequencyService: not found"
# DeviceAuthServer (Meta hardware attestation — WARNING: may affect companion pairing)
# Only disable if pairing is complete and you do not need it again
pm disable-user --user 0 com.oculus.deviceauthserver 2>/dev/null || echo "DeviceAuthServer: not found"
# SystemSearch (VR universal search)
pm disable-user --user 0 com.oculus.systemsearch 2>/dev/null || echo "SystemSearch: not found"
# VrCast (casting)
pm disable-user --user 0 com.oculus.vrcast 2>/dev/null || echo "VrCast: skipped"
# YADI (yet another device installer — a secondary app install path)
pm disable-user --user 0 com.oculus.yadi 2>/dev/null || echo "YADI: not found"

echo "[PHASE 2] Complete."
echo ""

# ============================================================
# PHASE 3: Tracking/sensor stack (run LAST, careful)
# Only if spatial tracking is NOT needed for your use case
# WARNING: trackingservice crash-loops without cameras
# These stop the crash-looping, not the underlying driver
# ============================================================

echo "[PHASE 3] Disabling spatial tracking stack..."

# Direct shell stop commands (services, not packages)
stop trackingservice 2>/dev/null
stop slamworker 2>/dev/null
stop slam_service 2>/dev/null

# To make permanent across reboots (requires writing to /system — needs root)
# Or use setprop to prevent auto-start:
setprop persist.oculus.tracking.disable 1 2>/dev/null

echo "[PHASE 3] Note: tracking services will restart on reboot until root allows permanent disable."
echo ""

# ============================================================
# VERIFICATION
# ============================================================
echo "=== Disabled packages ==="
pm list packages -d

echo "=== Running memory after strip ==="
cat /proc/meminfo | grep -E 'MemTotal|MemFree|MemAvailable'

echo "=== Active processes (should be much shorter list) ==="
ps -A | grep -v kworker | grep -v "\[" | head -30

echo ""
echo "Stage 1 strip complete."
echo "Estimated free RAM gained: 400-600MB of ~3.5GB total"
echo "Next step for deeper strip: root access -> Stage 2"
