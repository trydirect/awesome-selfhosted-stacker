Output gifs/stacker-plausible.gif

Set FontSize 16
Set Width 1200
Set Height 700
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 50ms

Type "$ stacker install plausible --domain analytics.example.com \\"
Enter
Type "    --key htz-0 --provider hetzner --region fsn1 --size cx23"
Enter
Sleep 1s

Type "Stacker wants to create stacker.yml in the current directory. Allow? [y/N]"
Enter
Type "y"
Enter
Sleep 1s

Type "Installed 'plausible' as project #372."
Sleep 200ms
Enter
Type "Wrote stacker.yml"
Sleep 200ms
Enter
Type "  Hooks in this file will be REFUSED by 'stacker deploy' until you review"
Sleep 200ms
Enter
Type "  them and remove the '# @stacker-origin: marketplace' marker line (or pass"
Sleep 200ms
Enter
Type "  --allow-untrusted-hooks)."
Sleep 200ms
Enter
Type "Deploy with: stacker deploy --project plausible"
Sleep 500ms
Enter
Enter

Type "$ cat stacker.yml"
Enter
Sleep 500ms

Type "name: plausible"
Enter
Type "services:"
Enter
Type "  plausible:"
Enter
Type "    image: ghcr.io/plausible/community-edition:latest"
Enter
Type "    ports: [8000:8000]"
Enter
Type "  plausible_db:"
Enter
Type "    image: postgres:latest"
Enter
Type "    ports: [5432:5432]"
Enter
Type "  plausible_events_db:"
Enter
Type "    image: clickhouse/clickhouse-server:latest"
Enter
Type "    ports: [8123:8123]"
Sleep 500ms
Enter
Enter

Type "$ stacker deploy --target cloud --key htz-0 --force-new"
Enter
Sleep 2s

Type "Using cloud credential override: htz-0 (id=11, provider=htz)"
Enter
Type "Deploying project 'plausible' (id=251)..."
Sleep 500ms
Enter
Type "  ✓ completed (deployment #403)"
Sleep 500ms
Enter
Enter

Type "$ stacker list deployments | head -3"
Enter
Sleep 500ms

Type "ID     PROJECT    STATUS        DEPLOYMENT HASH"
Enter
Type "403    251        ✓ completed   deployment_7e4c1c95..."
Sleep 500ms
Enter
Enter

Type "$ # Plausible is running at http://94.130.99.220:8000"
Sleep 2s
