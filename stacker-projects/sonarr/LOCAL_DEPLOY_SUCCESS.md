# sonarr — LOCAL deploy SUCCESS

**Date:** 2026-10-05
**Stacker:** v0.3.4 (ccd7184)

## Command

```bash
cd stacker-projects/sonarr
stacker deploy --target local
```

## Verification

- `stacker status` — container(s) Up
- `stacker logs --service app` — application started
- `stacker destroy -y` — ✓ Stack destroyed successfully
