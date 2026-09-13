# Memos — Cloud Deploy Success

**Date:** 2026-09-13
**Server:** 116.202.19.183 (Hetzner, fsn1, cpx22)
**Deployment:** #309 — status: completed

## Access

- **Web UI:** http://116.202.19.183:5230

## Verification

```
$ curl -s -o /dev/null -w '%{http_code}' http://116.202.19.183:5230/
200
```
