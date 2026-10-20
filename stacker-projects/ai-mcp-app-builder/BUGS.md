# ai-mcp-app-builder — known issues

## [BUG] Upstream Git LFS objects are missing (404) — image assets unbuildable

**Severity:** High for source builds (Next.js build fails)
**Date:** 2026-10-20
**Status:** worked around in the template Dockerfile

### Summary
Asset PNGs in `Shubhamsaboo/awesome-llm-apps` (e.g.
`generative_ui_agents/ai-mcp-app-builder/apps/web/app/image.png`) are Git LFS
pointers whose objects **do not exist on GitHub's LFS server**:

```
[4f3988…] Object does not exist on the server: [404] Object does not exist on the server
error: failed to fetch some objects from 'https://github.com/.../info/lfs'
```

Anyone cloning the repo gets pointer files, and the Next.js build dies with
`Format error decoding Png: Invalid PNG signature`.

### Workaround in the template
The Dockerfile replaces every `.png` that is still an LFS pointer with a
valid 1x1 placeholder PNG before `pnpm turbo run build`. UI images are
placeholders until upstream restores the LFS objects.

## [NOTE] Local builds on arm64 are impractical

The Next.js (Turbopack) build under amd64 emulation hung for 50+ minutes on
Apple Silicon. The same Dockerfile completes in ~2 minutes on a native x86
host. Build and run were verified on x86 (Docker build + `docker run`,
`curl :3000` → HTTP 200).

## Verification (2026-10-20)

- Docker image builds on x86 (Hetzner, native) with the placeholder fix
- Container runs and serves HTTP 200 on port 3000
