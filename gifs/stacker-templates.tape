Output gifs/stacker-templates.gif

Set FontSize 16
Set Width 1200
Set Height 700
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 50ms

Type "$ stacker templates --json | jq '.[].slug'"
Enter
Sleep 1s

Type '"archivebox"'
Enter
Type '"dify"'
Enter
Type '"dockge"'
Enter
Type '"ghost"'
Enter
Type '"lamp"'
Enter
Type '"n8n"'
Enter
Type '"plausible"'
Enter
Type '"umami"'
Enter
Type '"uptime-kuma-in-one-click"'
Enter
Type '"wordpress"'
Enter
Type '... and 60+ more'
Sleep 1s
Enter
Enter

Type "$ stacker find ghost --json | jq '.[0]'"
Enter
Sleep 500ms

Type '{'
Enter
Type '  "slug": "ghost",'
Enter
Type '  "name": "ghost",'
Enter
Type '  "description": "Install Ghost stack in one click using the upstream Ghost image with MySQL",'
Enter
Type '  "billing_cycle": "free"'
Enter
Type '}'
Sleep 2s
