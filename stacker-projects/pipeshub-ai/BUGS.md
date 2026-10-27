# pipeshub-ai — known issues

## [NOTE] Resource floor confirmed on cpx42

**Status:** verified working — the 2 GB-test-server note is superseded.

The slim subset (app + mongo + redis + qdrant + neo4j) runs on cpx42
(16 GB): all five containers healthy, app answers HTTP 200. RAM steady at
~4.6 GiB — so the stack needs **≥6 GB RAM** (the earlier "not deployable on
the 2 GB test server" assessment was correct and is now proven by the
measurement).

Deployed and verified on 2026-10-16 — see EXISTING_DEPLOY_SUCCESS.md.

## [FIXED] A fresh instance could be claimed by anyone

**Status:** fixed in 0.10.1, not yet verified on a cloud clone.

PipesHub's `POST /api/v1/org` is unauthenticated and the first caller
becomes the admin (upstream `deployment/docker-compose/BOOTSTRAP.md`). On a
server with port 3000 public that is whoever finds the IP first. The
one-shot `claim-org` service now creates the organization with
`ADMIN_EMAIL` / `ADMIN_PASSWORD` as soon as the app is healthy. The window
between the app becoming healthy and the claim is a few seconds, not zero.

The contract pattern only checks the character set and length: stacker's
regex engine has no look-ahead, so "contains an uppercase letter, a digit
and a symbol" is checked by `scripts/claim-org.sh`, which exits with the
rule named. Test: `scripts/test-claim-org.sh`.
