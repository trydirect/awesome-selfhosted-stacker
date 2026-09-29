# rocket-chat — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture changes; `DOCKER_DEFAULT_PLATFORM=linux/amd64` (rocket.chat:latest is
amd64-only). One-time DB init: `mongosh --eval 'rs.initiate()'` (mongo runs with
`--replSet rs0` but nothing initiates it — Rocket.Chat dies with `Topology is
closed`), then app restart.

## Verification

| Check | Result |
|---|---|
| Containers | `rocket-chat-app-1` Up, `rocket-chat-mongo-1` (healthy) |
| HTTP `GET /` (3000) | **200** |
