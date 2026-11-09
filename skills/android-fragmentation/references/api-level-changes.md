# API Level Changes

Read when: a crash or behavior change appears on specific Android versions, or when choosing or raising minSdk/targetSdk.

## Choosing minSdk

- Decide from real data: Play Console statistics, Android vitals, and the Android Studio version distribution for the target market.
- Compare the cost of supporting an old API (compat code, test time) with the share of users it adds.
- Jetpack Compose requires minSdk 21 or higher.
- Raise minSdk only when the dropped user share is acceptable and the removed compat code is worth it.

## Choosing targetSdk

- targetSdk opts the app into new behavior. Raise it deliberately, one version at a time.
- Google Play requires new apps and updates to target a recent API level. Check the Play Console target API page for the current deadline.
- Use the Android Studio SDK Upgrade Assistant and the official behavior-changes pages for each version.

## Guarding newer APIs

- Check `Build.VERSION.SDK_INT >= Build.VERSION_CODES.X` before calling newer APIs.
- Annotate helpers with `@RequiresApi(X)` and checker functions with `@ChecksSdkIntAtLeast`.
- Keep lint `NewApi` enabled and treat it as an error.
- Prefer AndroidX compat wrappers (`ContextCompat`, `ActivityCompat`, `NotificationManagerCompat`, `WindowCompat`) over manual version checks.
- For `java.time` and other newer Java APIs on API < 26, enable core library desugaring.
- Do not call hidden or non-SDK APIs through reflection.

## Behavior changes that most often cause bugs

Scope: **OS** = affects the app on that OS version regardless of targetSdk. **Target** = applies only when targetSdk is at or above that level.

| API | Android | Change | Scope |
|---|---|---|---|
| 23 | 6.0 | Runtime permissions. Doze and App Standby limit background work | Target (permissions), OS (Doze) |
| 24 | 7.0 | `file://` URIs shared with other apps throw `FileUriExposedException`; use `FileProvider`. Multi-window | OS |
| 26 | 8.0 | Background service limits. Notification channels required. Manifest receivers lose most implicit broadcasts. `startForegroundService()` must be followed quickly by `startForeground()` | Target |
| 28 | 9 | Cleartext HTTP blocked by default. Non-SDK interface restrictions. `FOREGROUND_SERVICE` permission | Target (cleartext), OS (non-SDK) |
| 29 | 10 | Scoped storage begins. Background activity launches restricted. Separate background location permission | Target (storage), OS (background launches) |
| 30 | 11 | Scoped storage enforced. Package visibility: `<queries>` needed to see other apps. One-time permissions and permission auto-reset | Target |
| 31 | 12 | `android:exported` required for components with intent filters. `PendingIntent` must declare `FLAG_IMMUTABLE` or `FLAG_MUTABLE`. Foreground service starts from background restricted. New Bluetooth permissions. Notification trampolines blocked | Target |
| 33 | 13 | `POST_NOTIFICATIONS` runtime permission. Granular media permissions replace `READ_EXTERNAL_STORAGE`. Exact alarm permissions | Target |
| 34 | 14 | Foreground service type required, with matching permission. Context-registered receivers must declare an exported flag. Exact alarms not granted by default to new installs. Partial photo access | Target |
| 35 | 15 | Edge-to-edge enforced. Foreground service timeouts for some types. Devices with 16 KB memory pages appear | Target (edge-to-edge), OS (16 KB) |
| 36 | 16 | Predictive back on by default. Orientation and resizability restrictions ignored on large screens. Edge-to-edge opt-out removed | Target |
| 37+ | 17+ | Not covered here. Check the official behavior-changes pages | n/a |

Verify the newest rows against developer.android.com before relying on them. Details and deadlines change.

## Native code (NDK)

- Devices with 16 KB page size exist from Android 15 onward. Native libraries must be built with 16 KB alignment.
- Google Play has a requirement for this. Check the current deadline.
- Check APK/AAB native libraries with the Android Studio APK Analyzer.

## Cross-version bug patterns to flag

- Newer API called without a version guard
- Missing `android:exported` on components with intent filters
- `PendingIntent` without an explicit mutability flag
- `READ_EXTERNAL_STORAGE` used on API 33+
- `file://` URIs passed in intents
- `startService()` from the background on API 26+
- Notification posted without a channel, or without handling `POST_NOTIFICATIONS`
- Exact alarms assumed to be available
- Foreground service started without a declared type on API 34+
- `java.time` used below API 26 without desugaring
- Hardcoded external storage paths
- Layout that ignores window insets on API 35+
- Missing `<queries>` when resolving other apps on API 30+

## Testing version behavior

- Test on the lowest supported API, the current targetSdk, and the newest release.
- Developer options > App Compatibility Changes toggles individual behavior changes per app (Android 11+).
- `adb shell am compat enable|disable CHANGE_ID PACKAGE` does the same from the command line.
- Run lint (`NewApi`, `ExportedReceiver`, `UnspecifiedImmutableFlag`) in CI.