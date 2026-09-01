# etherpad — Test Notes

Not stacker bugs — recorded here for accuracy (see `LOCAL_DEPLOY_SUCCESS.md`).

## Fixture fixes applied to `stacker.yml` (repo template defects, not stacker bugs)

1. Removed `socketIo: {}` / `logconfig: {}` from `app.environment` —
   invalid map values (env must be strings; also not real etherpad env
   vars). stacker correctly rejected them with a precise parse error, so
   this was stacker working as intended, not a defect.
2. Added `env_file: .env` (was missing) and a `proxy:` block for testing.

## stacker feature gap (already tracked)

- Proxy config generation is unimplemented — `proxy.type: nginx` (and
  `traefik`) start a proxy container but generate no routing config, so
  the app is only reachable on its direct port. Tracked in
  [stacker#242](https://github.com/trydirect/stacker/issues/242); not
  re-filing.

## Result

etherpad deploys and runs correctly via stacker (app 200 on all
endpoints, secrets injected). No stacker bug here.
