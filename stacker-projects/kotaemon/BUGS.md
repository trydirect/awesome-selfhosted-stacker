# kotaemon — known issues

## [SEC] Open RCE #844 / IDOR #846 — self-host only, never expose publicly

**Status:** upstream security caveat (from the quick-deploy targets list).
Do **not** submit this template to the marketplace until upstream fixes
https://github.com/Cinnamon/kotaemon/issues/844 and related IDOR #846.

## [NOTE] Resource note corrected — this template is the single-container build

**Status:** verified working on cpx42 (2026-10-16).

Earlier note ("ES-heavy, needs ≥6 GB") referred to the full upstream compose
with Elasticsearch. **This template ships the `main-lite` single-container
build** (ES not included) — it is light: one healthy container, HTTP 200 on
7860, ~1.3 GiB RAM for the whole host at idle. Runs on small servers fine.

Deployed and verified on 2026-10-16 — see CLOUD/EXISTING deploy success
file. The security caveat above still applies.
