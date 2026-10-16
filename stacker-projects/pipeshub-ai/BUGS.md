# pipeshub-ai — known issues

## [NOTE] Resource floor confirmed on cpx42

**Status:** verified working — the 2 GB-test-server note is superseded.

The slim subset (app + mongo + redis + qdrant + neo4j) runs on cpx42
(16 GB): all five containers healthy, app answers HTTP 200. RAM steady at
~4.6 GiB — so the stack needs **≥6 GB RAM** (the earlier "not deployable on
the 2 GB test server" assessment was correct and is now proven by the
measurement).

Deployed and verified on 2026-10-16 — see EXISTING_DEPLOY_SUCCESS.md.
