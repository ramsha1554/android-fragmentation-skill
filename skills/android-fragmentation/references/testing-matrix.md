# Testing Matrix

Read when: deciding which devices and API levels to test, choosing between emulators and real devices, or setting up CI and device-farm testing.

## Principle

Test across the axes that actually break apps, not across every device. Pick a small matrix from real usage data, and cover the extremes of each axis.

## Step 1: Build the matrix from data

Sources, in order of trust:
1. The app's own crash reports and Android vitals (Play Console).
2. Play Console device catalog and statistics: top devices, API levels, RAM tiers, screen sizes for your users.
3. Market-level device share data for new apps with no data yet.

Pick devices that cover:
- **API levels:** lowest supported, current targetSdk, newest release, and one middle version that changed major behavior (for example the permission or storage model change).
- **Screen:** small phone (compact width), large phone, tablet, and foldable or resizable window.
- **Density and font:** one low-density device, one high-density device, plus font scale 200% on any device.
- **OEM:** at least Pixel (baseline), Samsung, and one Xiaomi-family device. Add Oppo, Vivo, or Huawei if the target market uses them.
- **RAM:** one low-RAM or Go-edition device (2 GB or less).
- **Network:** slow and offline cases on at least one device.

Keep the core matrix to roughly 6-10 configurations. Add devices only when a real bug appears that the matrix missed.

## Step 2: Choose where to run each test

| Need | Use |
|---|---|
| Screen sizes, densities, API levels, foldable postures, rotation | Android Studio emulators (resizable emulator, foldable and tablet profiles) |
| OEM battery policy, vendor camera, vendor keyboard, real performance, thermal | Real devices |
| Broad coverage without owning devices | Cloud device farm (Firebase Test Lab or similar) |
| Unknown device-specific crashes before release | Play Console pre-launch report |
| Per-device crash trends after release | Play Console Android vitals, crash reporting |

Rule of thumb: emulators for layout and API, real devices for OEM and hardware behavior.

## Step 3: Automate

- Run unit tests on JVM in every build.
- Run instrumented UI tests on an API-level and form-factor matrix in CI. Gradle managed devices can define emulators in the build file.
- Use screenshot tests (Paparazzi, Roborazzi, or Compose preview screenshot testing) across window sizes, font scales, locales, and dark mode.
- Use Espresso or Compose UI tests with a test rule that sets window size.
- Run lint in CI with `NewApi`, `ExportedReceiver`, and `UnspecifiedImmutableFlag` as errors.
- Run a baseline performance check (startup time, jank) on a low-end device or emulator profile.
- Run a smoke test on a device farm for each release candidate.

## Step 4: Manual checklist per release

Screen and layout:
- Rotate on every key screen and check that state is preserved.
- Split-screen at several ratios, and resize a resizable window.
- Fold and unfold, tabletop posture, if foldables are supported.
- Font scale 200% and largest display size.
- Dark mode, and a device with a notch or cutout.
- Gesture navigation and three-button navigation.

OS and permissions:
- Fresh install and upgrade from the previous release on the lowest API.
- Each runtime permission: grant, deny, deny permanently, and revoke from settings.
- Notifications on API 33+ (permission requested and denied).
- Process death: enable "Don't keep activities", background the app, return.

OEM and background:
- Swipe the app from recents, wait, and check whether scheduled work still runs.
- Battery saver on, device idle for a few hours, reboot.
- Missing Google services, if the market includes such devices.

Hardware:
- Cameras, biometrics, and sensors on devices that lack them (app must not crash).
- Low storage and low memory.

## Triaging a device-specific bug

1. Reproduce on the same device model and OS version, or in a device farm.
2. Collect: device model, API level, OEM skin version, app version, stack trace, `adb bugreport`.
3. Check whether it is a standard Android behavior (Doze, permissions, storage) before blaming the OEM.
4. Add a regression test or matrix entry for it.
5. Fix with a feature check or an API guard. Branch on manufacturer only as a last resort, and document why.

## Release safety

- Use staged rollouts (for example 1%, 5%, 20%, 100%) and watch Android vitals between steps.
- Halt the rollout if the crash or ANR rate rises on any device group or API level.
- Keep a kill switch or remote config for risky workarounds.

## Anti-patterns to flag

- Testing only on one personal phone or only on emulators
- No test for the lowest supported API level
- No real-device test for background work
- A giant device list that nobody runs
- Matrix chosen by guesswork instead of usage data
- No staged rollout or no monitoring after release
- Skipping the upgrade path (only fresh installs tested)