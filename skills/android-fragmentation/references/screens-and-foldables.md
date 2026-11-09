# Screens, Densities, Tablets and Foldables

Read when: layouts break on tablets, foldables, landscape, split-screen, or unusual densities or font scales.

## Core approach

Size the UI to the **window**, not the device. Windows change at runtime (split-screen, foldable unfold, desktop windowing, rotation).

## Window size classes

| Class | Width | Height |
|---|---|---|
| Compact | < 600dp | < 480dp |
| Medium | 600-839dp | 480-899dp |
| Expanded | >= 840dp | >= 900dp |

Newer Jetpack versions add larger width classes (around 1200dp and 1600dp). Check current docs before relying on them.

- Compose: `currentWindowAdaptiveInfo()` and its `windowSizeClass`.
- Views: `WindowMetricsCalculator.computeCurrentWindowMetrics(activity)`, recompute on configuration change.
- Branch layout on width class first. Use height class mainly for landscape phones.

## Adaptive patterns

- Navigation: bottom bar (Compact), rail (Medium), drawer or rail (Expanded). Compose: `NavigationSuiteScaffold`.
- Content: single pane on Compact, list-detail or supporting pane on Medium/Expanded. Compose: `ListDetailPaneScaffold`, `SupportingPaneScaffold`.
- Cap content width on very wide windows (readable line length) instead of stretching.
- Grids: `LazyVerticalGrid` with `GridCells.Adaptive(minSize)`, not a fixed column count.

## XML resource qualifiers

- Prefer `sw600dp`, `w840dp`, `h480dp`, `land`.
- Avoid the deprecated size buckets (`small`, `normal`, `large`, `xlarge`).
- Keep one default layout and override only what differs.

## Densities and units

- Layout in `dp`, text in `sp`. Never px.
- Buckets: mdpi 160, hdpi 240, xhdpi 320, xxhdpi 480, xxxhdpi 640 dpi.
- Use vector drawables. Ship bitmaps only when a vector cannot express the image, and then provide xxhdpi at minimum.
- Users can change display size and font scale. Test font scale 200% and the largest display size. Avoid fixed-height text containers.

## Foldables

- Use Jetpack WindowManager: `WindowInfoTracker.getOrCreate(activity).windowLayoutInfo(activity)`.
- Read `FoldingFeature`: `state` (FLAT, HALF_OPENED), `orientation`, `isSeparating`, `occlusionType`.
- Tabletop posture = HALF_OPENED with horizontal fold. Put content above the fold and controls below.
- Never place critical UI across a separating fold or hinge.
- Preserve state across fold/unfold. The activity may be recreated, so keep UI state in a ViewModel or saved state.

## Multi-window and resizing

- `resizeableActivity` defaults to true for apps targeting API 24+. Do not set it to false to avoid work.
- On large screens (600dp+), recent Android versions ignore manifest orientation and resizability restrictions for apps targeting newer API levels. Locking orientation will not hold, so design for it. Verify the exact behavior and target API in current docs.
- Handle `onConfigurationChanged` only if you declare `configChanges`. Prefer recreation plus saved state.
- Camera apps: use CameraX. Do not assume preview orientation equals device orientation.

## Insets and cutouts

- Call `enableEdgeToEdge()` and apply `WindowInsets` (system bars, display cutout, IME).
- Do not hardcode status bar or navigation bar heights.

## Input

- Large screens and Chromebooks expect keyboard, mouse, and stylus support: focus order, hover states, keyboard shortcuts, right-click menus.

## Anti-patterns to flag

- Hardcoded px or fixed widths and heights in dp for containers
- Assuming portrait, or locking orientation
- `Display.getMetrics()` / `getRealSize()` to decide layout (use window metrics)
- Fixed column counts in grids
- Phone layout stretched to tablet width
- Dialogs or bottom sheets with fixed width
- Branching on `Build.MODEL` or manufacturer for UI
- Ignoring the fold or hinge area

## Verify

- Resizable emulator, and foldable and tablet emulator profiles
- Rotate and resize while on every key screen, check state is preserved
- Font scale 200% and largest display size
- Split-screen at multiple ratios