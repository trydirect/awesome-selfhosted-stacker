Output gifs/stacker-install-ghost.gif

Set FontSize 16
Set Width 1200
Set Height 700
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 50ms

Type "$ stacker install ghost --domain blog.example.com --key htz-0 \\"
Enter
Type "    --provider hetzner --region fsn1 --size cx23"
Enter
Sleep 1s

Type "Stacker wants to create stacker.yml in the current directory. Allow? [y/N]"
Enter
Type "y"
Enter
Sleep 1s

Type "Stacker wants to create stacker.yml in the current directory. Allow? yes"
Sleep 200ms
Enter
Type "Installed 'ghost' as project #371."
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
Type "Deploy with: stacker deploy --project ghost"
Sleep 500ms
Enter
Enter

Type "$ cat stacker.yml"
Enter
Sleep 500ms

Type "name: ghost"
Enter
Type "services:"
Enter
Type "  ghost:"
Enter
Type "    image: ghost:5-alpine"
Enter
Type "    ports:"
Enter
Type "    - 2368:2368"
Enter
Type "    environment:"
Enter
Type "      database__client: mysql"
Enter
Type "      database__connection__host: mysql"
Enter
Type "      NODE_ENV: production"
Enter
Type "  mysql:"
Enter
Type "    image: mysql:8"
Enter
Type "    ports:"
Enter
Type "    - 3306:3306"
Enter
Type "    environment:"
Enter
Type "      MYSQL_DATABASE: ghost"
Enter
Type "      MYSQL_USER: ghost"
Sleep 1s
Enter
Enter

Type "$ stacker deploy --target cloud --key htz-0 --force-new"
Enter
Sleep 3s

Type "Using cloud credential override: htz-0 (id=11, provider=htz)"
Enter
Type "Deploying project 'ghost' (id=370)..."
Sleep 200ms
Enter
Type "Server details: ghost-ae91 (root@94.130.99.220:22)"
Sleep 200ms
Enter
Type "✓ Local SSH backup key authorized"
Sleep 500ms
Enter
Enter

Type "$ stacker status"
Enter
Sleep 1s

Type "CONTAINER              IMAGE            STATUS   PORTS"
Enter
Type "project-ghost-1        ghost:5-alpine   Up 30s   0.0.0.0:2368->2368/tcp"
Enter
Type "project-mysql-1        mysql:8          Up 31s   0.0.0.0:3306->3306/tcp"
Sleep 2s
