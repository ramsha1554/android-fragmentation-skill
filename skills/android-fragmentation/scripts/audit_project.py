#!/usr/bin/env python3
"""Read-only scan of an Android project for common fragmentation problems.

Usage:
    python audit_project.py <project_root> [--json]

Standard library only. Never modifies files. Findings are leads to verify,
not proof: regex checks can produce false positives.
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

SKIP_DIRS = {".git", ".gradle", ".idea", "build", "node_modules", "out", "Pods"}
ANDROID = "{http://schemas.android.com/apk/res/android}"
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
LOCKED_ORIENTATIONS = {
    "portrait", "landscape", "reversePortrait", "reverseLandscape",
    "sensorPortrait", "sensorLandscape", "userPortrait", "userLandscape",
}

GRADLE_PATTERNS = {
    "minSdk": [
        r"\bminSdk(?:Version)?\s*(?:=\s*)?\(?\s*(\d+)",
        r'(?i)\bmin[-_]?sdk\s*=\s*"(\d+)"',
    ],
    "targetSdk": [
        r"\btargetSdk(?:Version)?\s*(?:=\s*)?\(?\s*(\d+)",
        r'(?i)\btarget[-_]?sdk\s*=\s*"(\d+)"',
    ],
    "compileSdk": [
        r"\bcompileSdk(?:Version)?\s*(?:=\s*)?\(?\s*(\d+)",
        r'(?i)\bcompile[-_]?sdk\s*=\s*"(\d+)"',
    ],
}

LAYOUT_RULES = [
    ("layout-px", "screen", "medium", r'="-?\d+(?:\.\d+)?px"',
     "Hardcoded px value; it will not scale across densities.",
     "Use dp for sizes and sp for text."),
    ("layout-textsize-dp", "screen", "medium",
     r'android:textSize="\d+(?:\.\d+)?dp"',
     "Text size in dp ignores the user's font scale.",
     "Use sp for text sizes."),
    ("layout-absolute", "screen", "high", r"<AbsoluteLayout",
     "AbsoluteLayout positions by fixed coordinates and breaks on other screens.",
     "Use ConstraintLayout or another responsive layout."),
    ("layout-fixed-wide", "screen", "low",
     r'android:layout_width="(?:[4-9]\d\d|\d{4,})dp"',
     "Very wide fixed width can overflow small screens.",
     "Use match_parent, weights, constraints, or a max width."),
]

PENDING_RE = re.compile(
    r"PendingIntent\.get(?:Activity|Activities|Broadcast|Service|ForegroundService)\("
)


def add(findings, rule, axis, priority, why, fix, where):
    entry = findings.setdefault(rule, {
        "rule": rule, "axis": axis, "priority": priority,
        "why": why, "fix": fix, "where": [],
    })
    entry["where"].append(where)


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield os.path.join(dirpath, name)


def read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def detect_sdk(gradle_texts):
    found = {"minSdk": [], "targetSdk": [], "compileSdk": []}
    for text in gradle_texts:
        for key, patterns in GRADLE_PATTERNS.items():
            for pat in patterns:
                found[key] += [int(v) for v in re.findall(pat, text)]
    return {
        "minSdk": min(found["minSdk"]) if found["minSdk"] else None,
        "targetSdk": max(found["targetSdk"]) if found["targetSdk"] else None,
        "compileSdk": max(found["compileSdk"]) if found["compileSdk"] else None,
    }


def check_manifest(path, rel, sdk, findings):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        add(findings, "manifest-unparsed", "api", "low",
            "Manifest could not be parsed.", "Check the file for XML errors.", rel)
        return
    target = sdk["targetSdk"]

    for perm in root.iter("uses-permission"):
        if (perm.get(ANDROID + "name") == "android.permission.READ_EXTERNAL_STORAGE"
                and perm.get(ANDROID + "maxSdkVersion") is None
                and target is not None and target >= 33):
            add(findings, "legacy-storage-permission", "api", "medium",
                "READ_EXTERNAL_STORAGE has no effect for media on API 33+.",
                "Use READ_MEDIA_* permissions or the Photo Picker.", rel)

    for tag in ("activity", "activity-alias", "service", "receiver"):
        for el in root.iter(tag):
            name = el.get(ANDROID + "name", "?")
            where = f"{rel} ({name})"
            if el.find("intent-filter") is not None and el.get(ANDROID + "exported") is None:
                add(findings, "missing-exported", "api", "high",
                    "Component with an intent filter has no android:exported; "
                    "builds targeting API 31+ fail.",
                    "Add android:exported=\"true\" or \"false\" explicitly.", where)
            if tag.startswith("activity") and el.get(ANDROID + "screenOrientation") in LOCKED_ORIENTATIONS:
                add(findings, "manifest-orientation-lock", "screen", "medium",
                    "Locked orientation; large screens may ignore it and layouts break.",
                    "Support all orientations and adapt to window size.", where)

    for el in root.iter():
        if el.get(ANDROID + "resizeableActivity") == "false":
            add(findings, "not-resizable", "screen", "high",
                "resizeableActivity=false breaks split-screen, foldables and desktop windows.",
                "Remove it and support resizing.",
                f"{rel} ({el.get(ANDROID + 'name', el.tag)})")

    for el in root.iter("uses-feature"):
        name = el.get(ANDROID + "name") or ""
        if name.startswith("android.hardware.") and el.get(ANDROID + "required") != "false":
            add(findings, "required-hardware", "hardware", "medium",
                "Hardware feature is required by default; devices without it cannot install the app.",
                "Add android:required=\"false\" unless the app truly cannot work without it, "
                "and check with hasSystemFeature at runtime.",
                f"{rel} ({name})")


def scan_rules(text, rel, rules, findings):
    for rule, axis, priority, pattern, why, fix in rules:
        for m in re.finditer(pattern, text):
            add(findings, rule, axis, priority, why, fix, f"{rel}:{line_of(text, m.start())}")


def source_rules(sdk):
    target = sdk["targetSdk"]
    storage_priority = "high" if target is not None and target >= 30 else "medium"
    return [
        ("build-model", "oem", "medium",
         r"\bBuild\.(?:MANUFACTURER|MODEL|BRAND)\b",
         "Device or manufacturer string in code; if it branches behavior, it breaks on other devices.",
         "Use feature checks, API checks, or window size classes. Keep device strings for logging only."),
        ("display-metrics", "screen", "medium",
         r"\.getDefaultDisplay\(|\.getRealSize\(|\.getRealMetrics\(",
         "Legacy display APIs report the screen, not the app window, so layout breaks in split-screen and on foldables.",
         "Use WindowMetricsCalculator or currentWindowAdaptiveInfo()."),
        ("orientation-lock", "screen", "medium",
         r"setRequestedOrientation\(|\brequestedOrientation\s*=",
         "Orientation locked in code; large screens may ignore it.",
         "Support both orientations and adapt to window size."),
        ("fixed-grid", "screen", "low", r"GridCells\.Fixed\(",
         "Fixed column count does not adapt to window width.",
         "Use GridCells.Adaptive(minSize)."),
        ("external-storage", "api", storage_priority,
         r"Environment\.getExternalStorage(?:Public)?Directory\(",
         "Direct external storage paths are restricted by scoped storage (API 29+).",
         "Use MediaStore, the Photo Picker, or the Storage Access Framework."),
        ("file-uri", "api", "medium", r'Uri\.fromFile\(|"file://',
         "file:// URIs shared with other apps throw FileUriExposedException on API 24+.",
         "Use FileProvider and content:// URIs."),
        ("start-service", "api", "medium", r"\bstartService\(",
         "startService() from the background throws on API 26+.",
         "Use WorkManager, or a foreground service started with startForegroundService()."),
    ]


def check_source(text, rel, sdk, desugar, rules, findings):
    scan_rules(text, rel, rules, findings)
    target = sdk["targetSdk"]
    for m in PENDING_RE.finditer(text):
        window = text[m.start():m.start() + 400]
        if "FLAG_IMMUTABLE" not in window and "FLAG_MUTABLE" not in window:
            priority = "high" if target is not None and target >= 31 else "medium"
            add(findings, "pending-intent-flag", "api", priority,
                "PendingIntent without FLAG_IMMUTABLE or FLAG_MUTABLE crashes on API 31+ "
                "(may be a false positive if flags are built elsewhere).",
                "Pass FLAG_IMMUTABLE unless the intent must be modified.",
                f"{rel}:{line_of(text, m.start())}")
    if sdk["minSdk"] is not None and sdk["minSdk"] < 26 and not desugar:
        for m in re.finditer(r"^\s*import\s+java\.time\.", text, re.M):
            add(findings, "java-time-no-desugar", "api", "high",
                "java.time needs API 26+; minSdk is lower and desugaring is not enabled.",
                "Enable core library desugaring or raise minSdk.",
                f"{rel}:{line_of(text, m.start())}")


def print_report(root, sdk, results):
    def show(v):
        return "not found" if v is None else str(v)

    print(f"Android fragmentation audit: {root}")
    print(f"minSdk: {show(sdk['minSdk'])} | targetSdk: {show(sdk['targetSdk'])} "
          f"| compileSdk: {show(sdk['compileSdk'])}")
    print(f"Findings: {len(results)}\n")
    for f in results:
        print(f"[{f['priority'].upper()}] Axis: {f['axis']}")
        print(f"  Why it breaks: {f['why']}")
        print(f"  Fix: {f['fix']}")
        shown = f["where"][:5]
        extra = len(f["where"]) - len(shown)
        suffix = f" (+{extra} more)" if extra > 0 else ""
        print(f"  Where: {', '.join(shown)}{suffix}\n")
    if not results:
        print("No findings from automated checks.")
    print("These are leads to verify. Automated checks cover only common patterns; "
          "still run the manual test matrix.")


def main():
    parser = argparse.ArgumentParser(description="Scan an Android project for fragmentation problems.")
    parser.add_argument("root", help="Path to the project root")
    parser.add_argument("--json", action="store_true", help="Print findings as JSON")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    files = list(iter_files(root))
    gradle_texts = [
        read(p) for p in files
        if os.path.basename(p) in ("build.gradle", "build.gradle.kts")
        or p.endswith(".versions.toml")
    ]
    sdk = detect_sdk(gradle_texts)
    desugar = any("corelibrarydesugaring" in t.lower() for t in gradle_texts)
    rules = source_rules(sdk)
    findings = {}

    for path in files:
        rel = os.path.relpath(path, root)
        base = os.path.basename(path)
        parts = rel.replace("\\", "/").split("/")
        if base == "AndroidManifest.xml":
            check_manifest(path, rel, sdk, findings)
        elif path.endswith(".xml") and "res" in parts and any(p.startswith("layout") for p in parts):
            scan_rules(read(path), rel, LAYOUT_RULES, findings)
        elif path.endswith((".kt", ".java")):
            check_source(read(path), rel, sdk, desugar, rules, findings)

    results = sorted(
        findings.values(),
        key=lambda f: (PRIORITY_ORDER[f["priority"]], f["axis"], f["rule"]),
    )
    if args.json:
        print(json.dumps({"sdk": sdk, "findings": results}, indent=2))
    else:
        print_report(root, sdk, results)
    return 0


if __name__ == "__main__":
    sys.exit(main())