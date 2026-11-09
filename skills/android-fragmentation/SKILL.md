---
name: android-fragmentation
description: Audits and fixes Android device fragmentation issues. Use when the user asks about supporting multiple screen sizes, densities, tablets, foldables, or multi-window; choosing minSdk or handling API-level differences; OEM-specific bugs such as Samsung, Xiaomi, Oppo, Vivo battery optimization or background kills; device-specific crashes; or building a device test matrix.
---

# Android Device Fragmentation

Fragmentation has four axes: screen, OS/API level, OEM behavior, hardware. Identify the axis first, then load only the matching reference.

## Workflow

1. **Gather context.** Ask for or find: minSdk, targetSdk, UI toolkit (Compose or XML), device categories, target markets, and the exact symptom (crash, layout bug, killed background work).
2. **Audit.** If `scripts/audit_project.py` exists, run it on the project root. Otherwise inspect `AndroidManifest.xml`, `build.gradle(.kts)`, and layouts by hand.
3. **Classify** each finding by axis using the router below.
4. **Report** findings before changing anything (format below).
5. **Fix** the highest-impact issues first. Keep changes minimal.
6. **Verify** against the test matrix in `references/testing-matrix.md`. State what was and was not verified.

## Router

| Symptom or question | Read |
|---|---|
| Layout breaks on tablets, foldables, landscape, split-screen, odd densities | `references/screens-and-foldables.md` |
| Crash or behavior change on specific Android versions, choosing minSdk/targetSdk | `references/api-level-changes.md` |
| Works on Pixel, fails on Samsung/Xiaomi/etc., background work killed, notification delays | `references/oem-quirks.md` |
| Which devices and APIs to test, emulator vs real device, CI setup | `references/testing-matrix.md` |

## Rules

- Decide with data (Play Console device catalog, Android vitals, crash reports), not guesses.
- Branch on window size classes and feature checks, never on device model or manufacturer, for UI.
- Guard newer APIs with `Build.VERSION.SDK_INT` or an AndroidX compat wrapper.
- Detect hardware at runtime with `PackageManager.hasSystemFeature`, and mark optional features `required="false"` in the manifest.
- Do not lock orientation or disable resizing to avoid layout work.
- Treat OEM behavior as unreliable. Use documented APIs, degrade gracefully, and tell the user when a workaround is OEM-specific.
- If information is missing, state your assumption instead of guessing silently.

## Report format

For each finding give:
- **Axis:** screen | API | OEM | hardware
- **Where:** file and line, or component
- **Why it breaks:** one sentence
- **Fix:** minimal change
- **Priority:** high | medium | low

End with a short list of what to test and on which devices or API levels.