# statistics-for-strava — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (default)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (pre-approved class): generator produced "No generated secrets
required" while the contract declares `STRAVA_CLIENT_SECRET`/`STRAVA_REFRESH_TOKEN`
`generated` and the app env keeps `${...}` placeholders — extended the generator to
fill them (hex). Contract-quality note: a refresh token is an OAuth credential the
*buyer* supplies in reality (`provided` fits better than `generated`).

## Verification

| Check | Result |
|---|---|
| Containers | `statistics-for-strava-app-1` Up (8081), `daemon-1` Up |
| HTTP `GET /` (8081) | **200** |
