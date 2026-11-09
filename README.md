# android-fragmentation-skill

A portable agent skill (`SKILL.md` format) for handling Android device fragmentation: screen sizes and densities, API levels, OEM quirks, hardware differences, and testing strategy.

## Install

Clone the repo, then copy the skill folder into your agent's skills directory.

```powershell
git clone https://github.com/ramsha1554/android-fragmentation-skill.git
```

Claude Code:
```powershell
Copy-Item -Recurse android-fragmentation-skill\skills\android-fragmentation $HOME\.claude\skills\
```

Codex:
```powershell
Copy-Item -Recurse android-fragmentation-skill\skills\android-fragmentation $HOME\.codex\skills\
```

Other agents: copy the `skills/android-fragmentation` folder into the directory your agent reads skills from (check its docs).

## Contents

- `skills/android-fragmentation/SKILL.md`: the skill instructions