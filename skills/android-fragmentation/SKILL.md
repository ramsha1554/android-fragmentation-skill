---
name: android-fragmentation
description: Use when the user asks about Android device fragmentation, including supporting multiple screen sizes, densities, OS/API versions, OEM-specific behavior, foldables, or choosing a device testing strategy.
---

# Android Device Fragmentation

## When to use
Apply this skill when the user is building, debugging, or planning an Android app that must work across many devices and OS versions.

## Approach
1. Clarify the target: minSdk, targetSdk, device categories (phones, tablets, foldables, Wear, TV), and key markets.
2. Identify which fragmentation axis is the problem, then apply the matching guidance below.
3. Recommend a testing plan for that axis before finishing.

## Axes of fragmentation

### Screen size and density
- Use dp/sp units, never px.
- Use responsive layouts: ConstraintLayout, Compose adaptive layouts, WindowSizeClass.
- Use resource qualifiers (sw600dp, land, night) for XML layouts.
- Provide vector drawables; supply density-specific bitmaps only when needed.
- Handle foldables and multi-window: react to window size changes, avoid locking orientation.

### OS / API level
- Choose minSdk from real usage data for the target market.
- Guard newer APIs with Build.VERSION.SDK_INT checks.
- Prefer AndroidX and Jetpack libraries for backward compatibility.
- Review behavior changes for each targetSdk bump (permissions, background limits, notifications, storage).

### OEM customizations
- Aggressive battery optimization and background process killing vary by manufacturer; test background work (WorkManager, foreground services) on several OEMs.
- Custom permission dialogs, skins, and system UI differences can change app behavior.
- Do not rely on undocumented OEM behavior; use documented APIs and degrade gracefully.

### Hardware differences
- Check for features at runtime (PackageManager.hasSystemFeature) and declare uses-feature with required=false when optional.
- Expect differences in cameras, sensors, biometrics, and memory.
- Optimize for low-RAM devices (smaller images, lazy loading, avoid memory leaks).

## Testing strategy
- Cover a matrix: small/large screens, low/high density, oldest and newest supported API, at least 2-3 OEMs.
- Use Android Studio emulators for size/API coverage.
- Use cloud device farms (for example Firebase Test Lab) for real-device coverage.
- Use the Play Console device catalog and pre-launch reports to find device-specific crashes.
- Add automated UI tests that run across the matrix in CI.

## Output guidance
- Give concrete, minimal recommendations tied to the user's stated minSdk and device targets.
- Prefer short checklists and code snippets over long explanations.
- State assumptions when information is missing.