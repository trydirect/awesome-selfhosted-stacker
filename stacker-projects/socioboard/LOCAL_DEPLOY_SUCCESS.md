# LOCAL_DEPLOY_SUCCESS.md

## socioboard — Local Deployment

- **Project**: socioboard
- **Target**: local
- **Timestamp**: 2026-07-14

## Commands Used

From `$BASE_PATH/stacker-projects/socioboard`, after loading the root `.env`:

```bash
stacker deploy --target local --force-rebuild --watch
```

## Verification

- `stacker deploy` completed with exit code 0.
- Local containers running:
  - `stacker-app-1` (socioboard-web) — `0.0.0.0:80->80/tcp`
  - `stacker-socioboard-1` (socioboard API)
  - `stacker-socioboard-mysql-1`
  - `stacker-socioboard-mongo-1`
- Home page responded with HTTP 302 redirect to `/login`:
  ```bash
  curl -I http://localhost:80/
  ```
  Output:
  ```
  HTTP/1.1 302 Found
  Location: http://localhost/login
  Server: nginx
  X-Powered-By: PHP/8.0.18
  ```

## Notes

- The `.env` file already contained generated secrets, so the `pre_build` hook skipped regeneration.
- The 302 to `/login` indicates the PHP/Nginx frontend is healthy.
