# android-fragmentation-skill

[![License: MIT](https://img.shields.io/github/license/ramsha1554/android-fragmentation-skill)](LICENSE)
[![Release](https://img.shields.io/github/v/release/ramsha1554/android-fragmentation-skill)](https://github.com/ramsha1554/android-fragmentation-skill/releases)
![Agents](https://img.shields.io/badge/works%20with-OpenCode%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20Cursor-blue)

**Teach your AI coding agent to audit and fix Android device fragmentation:** screen sizes, foldables, API-level differences, OEM background kills, and test matrices.

```bash
npx skills add ramsha1554/android-fragmentation-skill -g
```

## Contents

- [Is this for me?](#is-this-for-me)
- [Install](#install)
- [Try it](#try-it)
- [How it works](#how-it-works)
- [Audit script](#audit-script)
- [Contribute](#contribute)
- [Limitations](#limitations)
- [License](#license)

## Is this for me?

| Your app | Coverage |
|---|---|
| Native Android (Compose or XML) | Full |
| Flutter | Partial: API levels, OEM quirks, testing, and the `android/` manifest checks apply. Screen guidance is Compose/XML only. |
| iOS or web | Not covered |

## Install

```bash
npx skills add ramsha1554/android-fragmentation-skill -g
```

- `-g` installs for your user account (every project). Leave it out to install into the current project only.
- Add `-a opencode`, `-a claude-code` or `-a codex` to target one agent. Leave it out to choose interactively.
- Requires Node.js.

Update or remove:

```bash
npx skills update
npx skills remove android-fragmentation -g
```

<details>
<summary>Manual install (no Node.js)</summary>

Clone this repo and copy `skills/android-fragmentation` into your agent's skills folder, for example `~/.config/opencode/skills/` (OpenCode) or `~/.claude/skills/` (Claude Code).

</details>

## Try it

Ask your agent any of these:

- "My Compose app looks stretched on tablets and breaks when I unfold a Galaxy Z Fold."
- "My WorkManager sync never runs in the background on Xiaomi and Samsung phones."
- "I want to raise targetSdk. What behavior changes should I check?"
- "Audit my Android project for fragmentation problems. Report only, don't edit files."

Illustrative difference:

| Without the skill | With the skill |
|---|---|
| Generic advice such as "use ConstraintLayout and test on several devices" | Identifies the axis (screen), recommends window size classes and `FoldingFeature`, flags orientation locks, and ends with what to test and on which devices |

## How it works

1. **You ask** a multi-device Android question.
2. **The agent picks the axis:** screen, API level, OEM, or hardware.
3. **It reads only the matching reference**, then reports findings (axis, where, why it breaks, fix, priority) before changing anything.

| Topic | Reference |
|---|---|
| Tablets, foldables, window size classes, densities, insets | [screens-and-foldables.md](skills/android-fragmentation/references/screens-and-foldables.md) |
| Behavior changes by Android version, minSdk and targetSdk | [api-level-changes.md](skills/android-fragmentation/references/api-level-changes.md) |
| Samsung, Xiaomi, Oppo, Vivo, Huawei, OnePlus background kills | [oem-quirks.md](skills/android-fragmentation/references/oem-quirks.md) |
| Device matrix, emulators vs real devices, CI, staged rollouts | [testing-matrix.md](skills/android-fragmentation/references/testing-matrix.md) |

## Audit script

A read-only scan for common problems: missing `android:exported`, locked orientation, non-resizable activities, required hardware features, hardcoded px, legacy display APIs, `PendingIntent` flags, legacy storage use, and `java.time` without desugaring.

```bash
python skills/android-fragmentation/scripts/audit_project.py <project_root>
python skills/android-fragmentation/scripts/audit_project.py <project_root> --json
```

- Standard library only. Never modifies files.
- Findings are leads to verify, not proof.
- For Flutter, point it at the `android/` folder.

## Contribute

Issues and pull requests are welcome, especially corrections to OEM behavior and new Android version changes.

```
skills/android-fragmentation/
  SKILL.md              Router: description, workflow, rules, report format
  references/           One file per axis, loaded only when needed
  scripts/audit_project.py   Read-only project scan
  evals/evals.json      Test prompts with expected behavior
  evals/fixtures/       Small project used by the audit eval
```

Guidelines:
- Keep `SKILL.md` short. Put details in `references/`.
- Keep the audit script standard-library only and read-only.
- Run the prompts in `evals/evals.json` by hand in your agent before opening a PR, and add an eval for any new behavior.
- Add an entry to `CHANGELOG.md`.

## Limitations

- API-level and OEM tables change often. Verify against official Android docs and current devices.
- The audit script checks common patterns only.
- OEM setting names vary by skin version.

## License

MIT. See [LICENSE](LICENSE).