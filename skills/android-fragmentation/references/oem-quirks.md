# OEM Quirks

Read when: the app works on Pixel but fails on Samsung, Xiaomi, Oppo, Vivo, Huawei, OnePlus or similar; background work is killed; notifications arrive late; behavior differs by manufacturer.

## Core principle

OEM behavior is undocumented, varies by skin version, and changes between updates. Use documented Android APIs first, detect the problem at runtime, degrade gracefully, and guide the user only when needed. Never branch core logic on manufacturer.

## Common OEM behaviors

Names change between skin versions. Treat this table as a starting map, not a spec. Verify against current device behavior and community sources such as dontkillmyapp.com.

| OEM (skin) | Typical issue | Typical user-side setting |
|---|---|---|
| Samsung (One UI) | Apps put to "sleep" or "deep sleep" by Device Care or battery settings; unused apps auto-restricted | Battery > Background usage limits: remove app from sleeping/deep sleeping lists, set to Unrestricted |
| Xiaomi / Redmi / POCO (MIUI, HyperOS) | Aggressive background kill; Autostart off by default; apps killed when swiped from recents | Autostart on; Battery saver for app = No restrictions; lock app in recents |
| Oppo / Realme (ColorOS, realme UI) | Background freeze; auto-launch off | Auto-launch on; allow background activity; battery optimization off for app |
| Vivo / iQOO (Funtouch OS, OriginOS) | Aggressive background kill; Autostart and background power consumption limits | Autostart on; high background power consumption allowed |
| Huawei / Honor (EMUI, HarmonyOS, MagicOS) | App launch management kills background apps; many devices have no Google services | App launch: manage manually, enable auto-launch, secondary launch, run in background |
| OnePlus (OxygenOS) | Battery optimization and deep optimization kill background work | Battery optimization: Don't optimize; allow background activity |
| Pixel, Nothing, Motorola | Closest to stock; standard Doze and App Standby rules | Standard battery optimization settings |

## Standard Android limits that look like OEM bugs

Rule these out first:
- Doze and App Standby defer jobs, alarms, and network.
- App standby buckets (active, working set, frequent, rare, restricted) throttle jobs, alarms, and FCM.
- Background execution and foreground service start limits (API 26+, tighter on 12+).
- Exact alarm permission (API 31+, tighter on 33/34).
- Unused app hibernation: permissions auto-reset for apps unused for months.

## Making background work resilient

- Deferrable work: use WorkManager. Do not use custom services or `AlarmManager` for this.
- User-visible ongoing work: foreground service with the correct type and a notification.
- Time-critical messages: FCM high-priority messages. Keep payloads small.
- Exact timing (alarms, reminders): use `SCHEDULE_EXACT_ALARM` or `USE_EXACT_ALARM` only if the app qualifies; otherwise use inexact alarms or WorkManager.
- Persist state before the process can die. Make every task idempotent and restartable.
- Do not rely on `START_STICKY`, boot receivers, or keep-alive tricks. Many OEMs ignore them.
- Never poll in a loop to stay alive.

## Detecting and diagnosing kills

- `ApplicationExitInfo` (API 30+): read why the last process exited (`REASON_USER_REQUESTED`, `REASON_LOW_MEMORY`, `REASON_EXCESSIVE_RESOURCE_USAGE`, `REASON_OTHER`, and so on). Log it to crash reporting.
- `ActivityManager.isBackgroundRestricted()` (API 28+).
- `PowerManager.isIgnoringBatteryOptimizations(packageName)`.
- `UsageStatsManager.getAppStandbyBucket()` (API 28+).
- Compare per-OEM and per-version exit reasons in crash reporting before adding any workaround.

## Guiding users to settings

- Show guidance only after evidence of a problem (for example repeated missed work), with a clear reason and a way to dismiss it.
- Official intents to try first: `Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS`, then `Settings.ACTION_APPLICATION_DETAILS_SETTINGS`.
- `ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` is restricted by Google Play policy to specific app types. Using it incorrectly can get an app rejected. Check current policy before using it.
- OEM-specific settings screens (component names for Xiaomi, Oppo, Vivo, Huawei) change often and break silently. If used: wrap in try/catch, check `resolveActivity`, and fall back to app details.
- Keep any per-OEM instructions in remote config or string resources so they can be updated without an app release.

## Other manufacturer differences

- **Missing Google services:** some Huawei and Honor devices have none. Check `GoogleApiAvailability`. FCM, Play Billing, and Maps will not work there.
- **Forced dark mode:** some skins darken apps that do not declare dark theme support. Support dark theme properly and set `android:forceDarkAllowed` explicitly.
- **System font and display scaling:** OEM font changes and large density settings break fixed-size layouts.
- **Cameras:** vendor camera stacks differ, and behavior varies for multiple lenses, orientation, and capture. Use CameraX and its compatibility handling. Do not assume Camera2 behavior is identical across devices.
- **Keyboards and IME:** vendor keyboards differ in autofill, composing text, and inset behavior. Test text input flows.
- **WebView:** version varies with the system WebView provider and update status. Feature-detect.
- **Navigation and back:** gesture navigation and custom button layouts differ. Handle insets and the system gesture areas.
- **Notches and cutouts:** shapes and sizes vary. Use `WindowInsets` and display cutout handling.
- **Permission dialogs and auto-start screens:** custom UIs may appear on top of standard permission requests. Do not assume exact dialog flow.
- **File pickers and share sheets:** vendor variants can return unusual URIs or MIME types. Always use the Storage Access Framework or Photo Picker and handle null and unexpected results.
- **Memory limits:** low-RAM and Go-edition devices kill cached processes sooner. Save UI state, release large objects in `onTrimMemory`, and keep startup light.

## Anti-patterns to flag

- Keep-alive hacks: silent audio, empty foreground notifications, wake lock abuse
- Branching on `Build.MANUFACTURER` for core logic
- Hardcoded OEM settings component names without try/catch and fallback
- Requesting battery optimization exemption on first launch
- Assuming a boot receiver always runs
- No logging of process exit reasons
- No fallback when Google services are missing
- Assuming a notification arrives instantly with FCM normal priority

## Verify

- Test background work on at least one Samsung and one Xiaomi-family device, plus a Pixel for baseline. Add Oppo, Vivo, or Huawei if the target market uses them.
- Use real devices or a cloud device farm. Emulators do not reproduce OEM battery policies.
- Test cases: swipe the app from recents, leave it idle for hours, charge and unplug, enable battery saver, reboot.
- Check `ApplicationExitInfo` and the app standby bucket after each case.
- Confirm that the app still behaves correctly if the user changes no settings.